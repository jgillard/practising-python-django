from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.decorators.http import require_http_methods

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from collections import Counter
import time

from .forms import CategoryForm, QuestionForm, OptionForm, TransactionDataForm, QuestionAnswerForm
from .models import Category, Question, Option, TransactionData, QuestionAnswer
from .serializers import CategorySerializer, OptionSerializer, QuestionSerializer, TransactionDataSerializer

from .monzo_integration import MonzoRequest, NoAccessTokenException, get_login_url, exchange_authorization_code, \
    OAUTH_STATE_TOKEN

### API Root ###


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'categories': reverse('category-list', request=request, format=format),
        'questions': reverse('question-list', request=request, format=format),
        'options': reverse('option-list', request=request, format=format),
        'transactiondata': reverse('td-list', request=request, format=format),
    })


### Category Views ###

class CategoryListView(generic.ListView):
    http_method_names = ['get']
    model = Category
    template_name = 'category_list.html'


class CategoryListDrf(generics.ListCreateAPIView):
    queryset = Category.objects.all().order_by('-id')
    serializer_class = CategorySerializer


class CategoryDetailView(generic.DetailView):
    http_method_names = ['get']
    model = Category
    template_name = 'category_detail.html'


class CategoryDetailDrf(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


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


class QuestionListDrf(generics.ListCreateAPIView):
    queryset = Question.objects.all().order_by('-id')
    serializer_class = QuestionSerializer


class QuestionDetailView(generic.DetailView):
    http_method_names = ['get']
    model = Question
    template_name = 'question_detail.html'


class QuestionDetailDrf(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


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


class OptionListDrf(generics.ListCreateAPIView):
    queryset = Option.objects.all().order_by('-id')
    serializer_class = OptionSerializer


class OptionDetailView(generic.DetailView):
    http_method_names = ['get']
    model = Option
    template_name = 'option_detail.html'


class OptionDetailDrf(generics.RetrieveUpdateDestroyAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer


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

class TdListView(generic.ListView):
    http_method_names = ['get']
    model = TransactionData
    template_name = 'td_list.html'


class TdListDrf(generics.ListCreateAPIView):
    queryset = TransactionData.objects.all().order_by('-id')
    serializer_class = TransactionDataSerializer


class TdDetailView(generic.DetailView):
    http_method_names = ['get']
    model = TransactionData
    template_name = 'td_detail.html'


class TdDetailDrf(generics.RetrieveUpdateDestroyAPIView):
    queryset = TransactionData.objects.all()
    serializer_class = TransactionDataSerializer


@require_http_methods(['GET', 'POST'])
def new_td(request, pk=None):
    # instructions for adding a formset: https://stackoverflow.com/a/28059352
    # requires for additional/configurable number of QAs

    if request.method == 'POST':
        return process_td_post(request)
    else:
        prefill_data = {'id': pk}
        form_td = TransactionDataForm(initial=prefill_data)
        form_qa = QuestionAnswerForm()

        context = {'form_td': form_td, 'form_qa': form_qa}
        return render(request, 'td_new.html', context=context)


class TdDeleteView(generic.edit.DeleteView):
    http_method_names = ['get', 'post']
    model = TransactionData
    template_name = 'generic_delete.html'
    extra_context = {'class_name': 'td', 'footer': 'foobles'}
    success_url = reverse_lazy('td_list')

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
            context['qas'] = QuestionAnswer.objects.filter(td=latest['id'])
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
                if td.id == spend['id']:
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
        return process_td_post(request)

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

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if context['answer_type'] == 'N':
            return HttpResponse(status=204)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        question_id = self.request.GET.get('question')
        question = Question.objects.get(pk__exact=question_id)
        context['answer_type'] = question.answer_type
        options = question.options
        context['options'] = options

        return context


### Shared Logic ###

@require_http_methods(['GET', 'POST'])
def process_td_post(request):
    form_td = TransactionDataForm(request.POST)
    form_qa = QuestionAnswerForm(request.POST)
    if all([form_td.is_valid(), form_qa.is_valid()]):
        td = form_td.save()
        if form_qa.cleaned_data:
            # don't create QA if no question supplied
            if request.POST['question'] != '':
                qa = form_qa.save(commit=False)
                qa.td = td
                qa.save()
        return redirect('td_detail', pk=td.id)
