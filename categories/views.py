from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.decorators.http import require_http_methods

from rest_framework import permissions, viewsets

from .forms import *
from .models import *
from .serializers import *

from .monzo_integration import get_login_url, exchange_authorization_code, OAUTH_STATE_TOKEN


### Category Views ###

class CategoryDrfViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('-id')
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


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

class QuestionDrfViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all().order_by('-id')
    serializer_class = QuestionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


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

class OptionDrfViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all().order_by('-id')
    serializer_class = OptionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


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


### QuestionAnswer Views ###

class QuestionAnswerDrfViewSet(viewsets.ModelViewSet):
    queryset = QuestionAnswer.objects.all().order_by('-id')
    serializer_class = QuestionAnswerSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


### Transaction Views ###

class TransactionDrfViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('-id')
    serializer_class = TransactionSerializer
    permission_classes = (permissions.IsAuthenticated,)


class TdListView(generic.ListView):
    http_method_names = ['get']
    model = Transaction
    template_name = 'td_list.html'


class TdDetailView(generic.DetailView):
    http_method_names = ['get']
    model = Transaction
    template_name = 'td_detail.html'


@require_http_methods(['GET', 'POST'])
def new_td(request, pk=None):
    # instructions for adding a formset: https://stackoverflow.com/a/28059352
    # requires for additional/configurable number of QAs

    if request.method == 'POST':
        return process_td_post(request)
    else:
        prefill_data = {'id': pk}
        form_td = TransactionForm(initial=prefill_data)
        form_qa = QuestionAnswerForm()

        context = {'form_td': form_td, 'form_qa': form_qa}
        return render(request, 'td_new.html', context=context)


class TdDeleteView(generic.edit.DeleteView):
    http_method_names = ['get', 'post']
    model = Transaction
    template_name = 'generic_delete.html'
    extra_context = {'class_name': 'td', 'footer': 'foobles'}
    success_url = reverse_lazy('td_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # add debug data for deletions
        td = context['object']
        qas = td.question_answers
        context['footer'] = f'''In addition to the Transaction: {repr(td)},
        the following QuestionAnswer objects will be first be deleted {list(qas)}'''

        return context


### Composite Views ###

class IndexView(generic.TemplateView):
    http_method_names = ['get']
    template_name = 'index.html'


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
    form_td = TransactionForm(request.POST)
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
