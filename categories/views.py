from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views import generic

from collections import Counter
import time

from .forms import CategoryForm, QuestionForm, OptionForm, TransactionDataForm, QuestionAnswerForm
from .models import Category, Question, Option, TransactionData, QuestionAnswer

from .monzo_integration import MonzoRequest, NoAccessTokenException, get_login_url, exchange_authorization_code, \
    OAUTH_STATE_TOKEN


### Category Views ###

class CategoryListView(generic.ListView):
    model = Category
    template_name = 'category_list.html'


class CategoryDetailView(generic.DetailView):
    model = Category
    template_name = 'category_detail.html'


class CategoryCreateView(generic.edit.CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'generic_new.html'
    extra_context = {'class_name': model.__name__}

    def post(self, request, *args, **kwargs):
        if 'save-and-add-another' in request.POST:
            self.success_url = reverse_lazy('category_new')
        return super().post(self, request, *args, **kwargs)


class CategoryUpdateView(generic.edit.UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'generic_edit.html'
    extra_context = {'class_name': model.__name__}


class CategoryDeleteView(generic.edit.DeleteView):
    # this currently throws an exception if there are child objects
    model = Category
    template_name = 'generic_delete.html'
    extra_context = {'class_name': model.__name__}
    success_url = reverse_lazy('category_list')


### Question Views ###

class QuestionListView(generic.ListView):
    model = Question
    template_name = 'question_list.html'


class QuestionDetailView(generic.DetailView):
    model = Question
    template_name = 'question_detail.html'


class QuestionCreateView(generic.edit.CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'generic_new.html'
    extra_context = {'class_name': model.__name__}

    def post(self, request, *args, **kwargs):
        if 'save-and-add-another' in request.POST:
            self.success_url = reverse_lazy('question_new')
        return super().post(self, request, *args, **kwargs)


class QuestionUpdateView(generic.edit.UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'generic_edit.html'
    extra_context = {'class_name': model.__name__}


class QuestionDeleteView(generic.edit.DeleteView):
    # this currently allows deletion of questions with referencing options
    model = Question
    form_class = QuestionForm
    template_name = 'generic_delete.html'
    extra_context = {'class_name': model.__name__}
    success_url = reverse_lazy('question_list')


### Option Views ###

class OptionListView(generic.ListView):
    model = Option
    template_name = 'option_list.html'


class OptionDetailView(generic.DetailView):
    model = Option
    template_name = 'option_detail.html'


class OptionCreateView(generic.edit.CreateView):
    model = Option
    form_class = OptionForm
    template_name = 'generic_new.html'
    extra_context = {'class_name': model.__name__}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        question_id = self.request.GET.get('question')
        # Passes question_id into the Form
        kwargs['initial'].update({'question': question_id})
        return kwargs

    def post(self, request, *args, **kwargs):
        if 'save-and-add-another' in request.POST:
            self.success_url = reverse_lazy('option_new')
        return super().post(self, request, *args, **kwargs)


class OptionUpdateView(generic.edit.UpdateView):
    model = Option
    form_class = OptionForm
    template_name = 'generic_edit.html'
    extra_context = {'class_name': model.__name__}


class OptionDeleteView(generic.edit.DeleteView):
    model = Option
    form_class = OptionForm
    template_name = 'generic_delete.html'
    extra_context = {'class_name': model.__name__}
    success_url = reverse_lazy('option_list')


### Transaction Views ###

class TxidListView(generic.ListView):
    model = TransactionData
    template_name = 'txid_list.html'


class TxidDetailView(generic.DetailView):
    model = TransactionData
    template_name = 'txid_detail.html'
    pk_url_kwarg = 'txid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        td = context['object']
        context['qs'] = Question.objects.filter(category=td.category)
        context['qas'] = QuestionAnswer.objects.filter(txid=td)
        return context


def new_txid(request, txid=None):
    # instructions for adding a formset: https://stackoverflow.com/a/28059352
    # requires for additional/configurable number of QAs

    if request.method == 'POST':
        return process_txid_post(request)
    else:
        prefill_data = {'txid': txid}
        form_td = TransactionDataForm(initial=prefill_data)
        form_qa = QuestionAnswerForm()

        context = {'form_td': form_td, 'form_qa': form_qa}
        return render(request, 'txid_new.html', context=context)


class TxidDeleteView(generic.edit.DeleteView):
    model = TransactionData
    template_name = 'generic_delete.html'
    extra_context = {'class_name': 'txid', 'footer': 'foobles'}
    pk_url_kwarg = 'txid'
    success_url = reverse_lazy('txid_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # add debug data for deletions
        td = repr(context['object'])
        qas = list(QuestionAnswer.objects.filter(txid__exact=context['object']))
        context['footer'] = f'''In addition to the TransactionData: {td},
            the following QuestionAnswer objects will be first be deleted {qas}'''

        return context

    def delete(self, request, *args, **kwargs):
        # delete the dependant QAs first
        qas = QuestionAnswer.objects.filter(txid__exact=kwargs['txid'])
        qas.delete()
        return super().delete(request, *args, **kwargs)


### Composite Views ###

def index(request):
    context = {
        'category_list': Category.objects.all(),
        'question_list': Question.objects.all(),
        'option_list': Option.objects.all(),
    }
    return render(request, 'index.html', context)


@login_required(login_url='/admin/')
def latest_monzo_transaction(request):
    try:
        monzo = MonzoRequest()
    except NoAccessTokenException:
        request.session['final_redirect'] = reverse('latest_transaction')
        return start_login_view(request)

    t0 = time.time()
    latest = monzo.get_latest_transaction()
    req_secs = time.time() - t0

    context = {'data': latest, 'reqs1secs': req_secs}
    try:
        context['td'] = TransactionData.objects.get(pk=latest['id'])
        context['qs'] = Question.objects.filter(category=context['td'].category)
        context['qas'] = QuestionAnswer.objects.filter(txid=latest['id'])
    except TransactionData.DoesNotExist:
        pass

    return render(request, 'latest_transaction.html', context)


@login_required(login_url='/admin')
def week_list_view(request):
    try:
        monzo = MonzoRequest()
    except NoAccessTokenException:
        request.session['final_redirect'] = reverse('week')
        return start_login_view(request)

    t0 = time.time()
    spending = monzo.get_week_of_spends()
    req_1_secs = time.time() - t0

    ids = [t['id'] for t in spending]
    # get any TD objects with a matching ID
    tds = list(TransactionData.objects.filter(pk__in=ids))

    # Attach TransactionData object to monzo spends if it exists
    for spend in spending:
        spend['td_obj'] = None
        for td in tds:
            if td.txid == spend['id']:
                spend['td_obj'] = td

    # Put the latest transactions at the front of the list
    spending = spending[::-1]

    context = {'object_list': spending, 'reqs1secs': req_1_secs}
    return render(request, 'week.html', context)


@login_required(login_url='/admin')
def analysis_view(request):
    try:
        monzo = MonzoRequest()
    except NoAccessTokenException:
        request.session['final_redirect'] = reverse('analysis')
        return start_login_view(request)

    spending = monzo.get_week_of_spends()

    ############################### sums
    spending_sum_pennies = abs(sum([t['amount'] for t in spending]))

    ingested_spends = monzo.get_week_of_ingested_spends()

    ingested_sum_pennies = abs(sum([t['amount'] for t in ingested_spends]))

    diff = spending_sum_pennies - ingested_sum_pennies

    uningested_transactions = monzo.get_week_of_uningested_spends()
    uningested_sum_pennies = abs(sum([t['amount'] for t in uningested_transactions]))

    ############################# some category stuff
    ingested_transactions_monzo = monzo.get_week_of_ingested_spends()
    ingested_transaction_ids = [t['id'] for t in ingested_transactions_monzo]
    ingested_transactions_td = list(TransactionData.objects.filter(pk__in=ingested_transaction_ids))

    summary = Counter()
    for td in ingested_transactions_td:
        # Get top-level category for each transaction
        category = td.category.parent if td.category.parent else td.category
        monzo_transaction = [t for t in ingested_transactions_monzo if t['id'] == td.txid][0]
        # spend amounts are always negative
        summary[category.name] -= monzo_transaction['amount']

    context = {
        'total_transactions_count': len(spending),
        'spending_sum_pennies': spending_sum_pennies,
        'ingested_sum_pennies': ingested_sum_pennies,
        'count_ingested': len(ingested_spends),
        'diff': diff,
        'uningested_sum_pennies': uningested_sum_pennies,
        'count_uningested': len(uningested_transactions),
        'summary': summary,
    }
    return render(request, 'analysis.html', context)


@login_required(login_url='/admin/')
def ingest_view(request):
    if request.method == 'POST':
        return process_txid_post(request)

    try:
        monzo = MonzoRequest()
    except NoAccessTokenException:
        request.session['final_redirect'] = reverse('ingest')
        return start_login_view(request)

    transaction = monzo.get_latest_uningested_transaction()
    form_td = TransactionDataForm(initial={'txid': transaction['id']})
    form_qa = QuestionAnswerForm()
    context = {'data': transaction, 'form_td': form_td, 'form_qa': form_qa}
    return render(request, 'ingest.html', context)


### Login Views ###

@login_required(login_url='/admin/')
def start_login_view(request):
    redirect_uri = request.build_absolute_uri(reverse('oauth_callback'))
    login_url = get_login_url(redirect_uri)
    return redirect(login_url)


@login_required(login_url='/admin/')
def oauth_callback_view(request):
    state = request.GET.get('state')
    # Improving this is out-of-scope for now
    assert (state == OAUTH_STATE_TOKEN)

    authorization_code = request.GET.get('code')
    redirect_uri = request.build_absolute_uri(reverse('oauth_callback'))
    exchange_authorization_code(authorization_code, redirect_uri)

    return redirect(request.session['final_redirect'])


### AJAX Views ###

def load_questions_for_category(request):
    # Also returns questions from a parent category
    category_id = request.GET.get('category')
    category = Category.objects.get(pk=category_id)
    parent_id = category.parent.pk
    questions = Question.objects.filter(category__in=[category_id, parent_id])
    return render(request, 'components/question_dropdown_list.html', {'questions': questions})


def load_options_for_question(request):
    question_id = request.GET.get('question')
    question = Question.objects.get(pk__exact=question_id)
    if question.answer_type == 'N':
        return HttpResponse(status=204)
    options = Option.objects.filter(question=question_id)
    return render(request, 'components/option_dropdown_list.html', {'options': options})


### Shared Logic ###

def process_txid_post(request):
    form_td = TransactionDataForm(request.POST)
    form_qa = QuestionAnswerForm(request.POST)
    if all([form_td.is_valid(), form_qa.is_valid()]):
        td = form_td.save()
        if form_qa.cleaned_data:
            # don't create QA if no question supplied
            if request.POST['question'] != '':
                qa = form_qa.save(commit=False)
                qa.txid = td
                qa.save()
        return redirect('txid_detail', txid=td.txid)
