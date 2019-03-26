from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.decorators.http import require_http_methods

from collections import Counter
import time

from .forms import CategoryForm, QuestionForm, OptionForm, TransactionDataForm, QuestionAnswerForm
from .models import Category, Question, Option, TransactionData, QuestionAnswer

from .monzo_integration import MonzoRequest, NoAccessTokenException, get_login_url, exchange_authorization_code, \
    OAUTH_STATE_TOKEN


### Category Views ###

class CategoryListView(generic.ListView):
    http_method_names = ['get']
    model = Category
    template_name = 'category_list.html'


class CategoryDetailView(generic.DetailView):
    http_method_names = ['get']
    model = Category
    template_name = 'category_detail.html'


class CategoryCreateView(generic.edit.CreateView):
    http_method_names = ['get', 'post']
    model = Category
    form_class = CategoryForm
    template_name = 'generic_new.html'
    extra_context = {'class_name': model.__name__}

    def post(self, request, *args, **kwargs):
        if 'save-and-add-another' in request.POST:
            self.success_url = reverse_lazy('category_new')
        return super().post(self, request, *args, **kwargs)


class CategoryUpdateView(generic.edit.UpdateView):
    http_method_names = ['get', 'post']
    model = Category
    form_class = CategoryForm
    template_name = 'generic_edit.html'
    extra_context = {'class_name': model.__name__}


class CategoryDeleteView(generic.edit.DeleteView):
    http_method_names = ['get', 'post']
    # this currently throws an exception if there are child objects
    model = Category
    template_name = 'generic_delete.html'
    extra_context = {'class_name': model.__name__}
    success_url = reverse_lazy('category_list')


### Question Views ###

class QuestionListView(generic.ListView):
    http_method_names = ['get']
    model = Question
    template_name = 'question_list.html'


class QuestionDetailView(generic.DetailView):
    http_method_names = ['get']
    model = Question
    template_name = 'question_detail.html'


class QuestionCreateView(generic.edit.CreateView):
    http_method_names = ['get', 'post']
    model = Question
    form_class = QuestionForm
    template_name = 'generic_new.html'
    extra_context = {'class_name': model.__name__}

    def post(self, request, *args, **kwargs):
        if 'save-and-add-another' in request.POST:
            self.success_url = reverse_lazy('question_new')
        return super().post(self, request, *args, **kwargs)


class QuestionUpdateView(generic.edit.UpdateView):
    http_method_names = ['get', 'post']
    model = Question
    form_class = QuestionForm
    template_name = 'generic_edit.html'
    extra_context = {'class_name': model.__name__}


class QuestionDeleteView(generic.edit.DeleteView):
    http_method_names = ['get', 'post']
    # this currently allows deletion of questions with referencing options
    model = Question
    form_class = QuestionForm
    template_name = 'generic_delete.html'
    extra_context = {'class_name': model.__name__}
    success_url = reverse_lazy('question_list')


### Option Views ###

class OptionListView(generic.ListView):
    http_method_names = ['get']
    model = Option
    template_name = 'option_list.html'


class OptionDetailView(generic.DetailView):
    http_method_names = ['get']
    model = Option
    template_name = 'option_detail.html'


class OptionCreateView(generic.edit.CreateView):
    http_method_names = ['get', 'post']
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
            question_id = self.request.POST.get('question')
            self.success_url = reverse_lazy(
                'option_new') + f'?question={question_id}'
        return super().post(self, request, *args, **kwargs)


class OptionUpdateView(generic.edit.UpdateView):
    http_method_names = ['get', 'post']
    model = Option
    form_class = OptionForm
    template_name = 'generic_edit.html'
    extra_context = {'class_name': model.__name__}


class OptionDeleteView(generic.edit.DeleteView):
    http_method_names = ['get', 'post']
    model = Option
    form_class = OptionForm
    template_name = 'generic_delete.html'
    extra_context = {'class_name': model.__name__}
    success_url = reverse_lazy('option_list')


### Transaction Views ###

class TxidListView(generic.ListView):
    http_method_names = ['get']
    model = TransactionData
    template_name = 'txid_list.html'


class TxidDetailView(generic.DetailView):
    http_method_names = ['get']
    model = TransactionData
    template_name = 'txid_detail.html'


@require_http_methods(['GET', 'POST'])
def new_txid(request, pk=None):
    # instructions for adding a formset: https://stackoverflow.com/a/28059352
    # requires for additional/configurable number of QAs

    if request.method == 'POST':
        return process_txid_post(request)
    else:
        prefill_data = {'id': pk}
        form_td = TransactionDataForm(initial=prefill_data)
        form_qa = QuestionAnswerForm()

        context = {'form_td': form_td, 'form_qa': form_qa}
        return render(request, 'txid_new.html', context=context)


class TxidDeleteView(generic.edit.DeleteView):
    http_method_names = ['get', 'post']
    model = TransactionData
    template_name = 'generic_delete.html'
    extra_context = {'class_name': 'txid', 'footer': 'foobles'}
    success_url = reverse_lazy('txid_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # add debug data for deletions
        td = context['object']
        qas = td.question_answers
        context['footer'] = f'''In addition to the TransactionData: {repr(td)},
        the following QuestionAnswer objects will be first be deleted {list(qas)}'''

        return context


### Composite Views ###

class IndexView(generic.TemplateView):
    http_method_names = ['get']
    template_name = 'index.html'


class LatestTransactionView(LoginRequiredMixin, generic.TemplateView):
    http_method_names = ['get']
    template_name = 'latest_transaction.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            MonzoRequest()
        except NoAccessTokenException:
            self.request.session['final_redirect'] = reverse(
                'latest_transaction')
            return redirect('login_view')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        t0 = time.time()
        monzo = MonzoRequest()
        latest = monzo.get_latest_transaction()
        req_secs = time.time() - t0

        context['data'] = latest
        context['req_1_secs'] = req_secs
        try:
            context['td'] = TransactionData.objects.get(pk=latest['id'])
            context['qs'] = Question.objects.filter(
                category=context['td'].category)
            context['qas'] = QuestionAnswer.objects.filter(txid=latest['id'])
        except TransactionData.DoesNotExist:
            pass

        return context


class WeekView(LoginRequiredMixin, generic.TemplateView):
    http_method_names = ['get']
    template_name = 'week.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            MonzoRequest()
        except NoAccessTokenException:
            self.request.session['final_redirect'] = reverse('week')
            return redirect('login_view')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        t0 = time.time()
        monzo = MonzoRequest()
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

        context['object_list'] = spending
        context['reqs1secs'] = req_1_secs

        return context


class AnalysisView(LoginRequiredMixin, generic.TemplateView):
    http_method_names = ['get']
    template_name = 'analysis.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            MonzoRequest()
        except NoAccessTokenException:
            self.request.session['final_redirect'] = reverse('analysis_view')
            return redirect('login_view')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        monzo = MonzoRequest()
        spending = monzo.get_week_of_spends()

        # sums
        spending_sum_pennies = abs(sum([t['amount'] for t in spending]))

        ingested_spends = monzo.get_week_of_ingested_spends()

        ingested_sum_pennies = abs(sum([t['amount'] for t in ingested_spends]))

        diff = spending_sum_pennies - ingested_sum_pennies

        uningested_transactions = monzo.get_week_of_uningested_spends()
        uningested_sum_pennies = abs(
            sum([t['amount'] for t in uningested_transactions]))

        # some category stuff
        ingested_transactions_monzo = monzo.get_week_of_ingested_spends()
        ingested_transaction_ids = [t['id']
                                    for t in ingested_transactions_monzo]
        ingested_transactions_td = list(
            TransactionData.objects.filter(pk__in=ingested_transaction_ids))

        summary = Counter()
        for td in ingested_transactions_td:
            # Get top-level category for each transaction
            category = td.category.parent if td.category.parent else td.category
            monzo_transaction = [
                t for t in ingested_transactions_monzo if t['id'] == td.id][0]
            # spend amounts are always negative
            summary[category.name] -= monzo_transaction['amount']

        context_add = {
            'total_transactions_count': len(spending),
            'spending_sum_pennies': spending_sum_pennies,
            'ingested_sum_pennies': ingested_sum_pennies,
            'count_ingested': len(ingested_spends),
            'diff': diff,
            'uningested_sum_pennies': uningested_sum_pennies,
            'count_uningested': len(uningested_transactions),
            'summary': summary,
        }

        return {**context, **context_add}


@login_required(login_url='/admin/')
@require_http_methods(['GET', 'POST'])
def ingest_view(request):
    if request.method == 'POST':
        return process_txid_post(request)

    try:
        monzo = MonzoRequest()
    except NoAccessTokenException:
        request.session['final_redirect'] = reverse('ingest_view')
        return login_view(request)

    transaction = monzo.get_latest_uningested_transaction()
    form_td = TransactionDataForm(initial={'id': transaction['id']})
    form_qa = QuestionAnswerForm()
    context = {'data': transaction, 'form_td': form_td, 'form_qa': form_qa}
    return render(request, 'ingest.html', context)


### Login Views ###

@login_required(login_url='/admin/')
@require_http_methods(['GET'])
def login_view(request):
    redirect_uri = request.build_absolute_uri(reverse('oauth_callback'))
    login_url = get_login_url(redirect_uri)
    return redirect(login_url)


@login_required(login_url='/admin/')
@require_http_methods(['GET'])
def oauth_callback_view(request):
    state = request.GET.get('state')
    # Improving this is out-of-scope for now
    assert (state == OAUTH_STATE_TOKEN)

    authorization_code = request.GET.get('code')
    redirect_uri = request.build_absolute_uri(reverse('oauth_callback'))
    exchange_authorization_code(authorization_code, redirect_uri)

    return redirect(request.session['final_redirect'])


### AJAX Views ###

class LoadQuestionsForCategoryView(generic.TemplateView):
    http_method_names = ['get']
    template_name = 'components/question_dropdown_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category_id = self.request.GET.get('category')
        category = Category.objects.get(pk=category_id)
        questions = category.questions
        context['questions'] = questions

        return context


class LoadOptionsForQuestionView(generic.TemplateView):
    http_method_names = ['get']
    template_name = 'components/option_dropdown_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        question_id = self.request.GET.get('question')
        question = Question.objects.get(pk__exact=question_id)
        if question.answer_type == 'N':
            return HttpResponse(status=204)
        options = question.options
        context['options'] = options

        return context


### Shared Logic ###

@require_http_methods(['GET', 'POST'])
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
        return redirect('txid_detail', pk=td.id)
