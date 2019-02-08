from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic

from .models import Category, Question, Option
from .forms import CategoryForm, QuestionForm, OptionForm


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
