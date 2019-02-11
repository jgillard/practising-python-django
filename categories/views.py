from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic

import time

from .forms import CategoryForm, QuestionForm, OptionForm, TransactionDataForm, QuestionAnswerForm
from .models import Category, Question, Option, TransactionData, QuestionAnswer

from .integrations import MonzoRequest


def index(request):
    context = {
        'category_list': Category.objects.all(),
        'question_list': Question.objects.all(),
        'option_list': Option.objects.all(),
    }
    return render(request, 'index.html', context)


### Category Views ###

class CategoryListView(generic.ListView):
    model = Category
    template_name = 'category_list.html'


class CategoryDetailView(generic.DetailView):
    model = Category
    template_name = 'category_detail.html'


class CategoryCreateView(generic.edit.CreateView):
    model = Category
    template_name = 'generic_new.html'
    extra_context = {'class_name': model.__name__}
    fields = ('name', 'parent')


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
    template_name = 'generic_new.html'
    extra_context = {'class_name': model.__name__}
    fields = ('title', 'category', 'answer_type')


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
    template_name = 'generic_new.html'
    extra_context = {'class_name': model.__name__}
    fields = ('title', 'question')


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
        form_td = TransactionDataForm(request.POST)
        form_qa = QuestionAnswerForm(request.POST)
        if all([form_td.is_valid(), form_qa.is_valid()]):
            td = form_td.save()
            if form_qa.cleaned_data:
                qa = form_qa.save(commit=False)
                qa.txid = td
                qa.save()
            return redirect('txid_detail', txid=td.txid)
    else:
        prefill_data = {'txid': txid}
        form_td = TransactionDataForm(initial=prefill_data)
        form_qa = QuestionAnswerForm(initial=prefill_data)

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


@login_required(login_url='/admin/')
def latest_monzo_transaction(request):
    monzo = MonzoRequest()

    t0 = time.time()
    spending = monzo.get_week_of_spends()
    req_1_secs = time.time() - t0

    latest_txid = spending[-1]['id']

    # Get the latest expenditure with full merchant data
    t0 = time.time()
    latest = monzo.get_transaction(latest_txid)
    req_2_secs = time.time() - t0

    context = {'data': latest, 'reqs1secs': req_1_secs, 'reqs2secs': req_2_secs}
    try:
        context['td'] = TransactionData.objects.get(pk=latest_txid)
        context['qs'] = Question.objects.filter(category=context['td'].category)
        context['qas'] = QuestionAnswer.objects.filter(txid=latest_txid)
    except TransactionData.DoesNotExist:
        pass

    return render(request, 'latest_transaction.html', context)
