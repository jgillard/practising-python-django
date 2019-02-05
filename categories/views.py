from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic

from .models import Category, Question, Option
from .forms import CategoryForm


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
    context_object_name = 'category_list'


class CategoryDetailView(generic.DetailView):
    model = Category
    template_name = 'category_detail.html'


class CategoryCreateView(generic.edit.CreateView):
    model = Category
    template_name = 'category_new.html'
    fields = ('name', 'parent')


class CategoryUpdateView(generic.edit.UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category_edit.html'


class CategoryDeleteView(generic.edit.DeleteView):
    # this currently throws an exception if there are child objects
    model = Category
    template_name = 'category_delete.html'
    success_url = reverse_lazy('category_list')


### Question Views ###

class QuestionListView(generic.ListView):
    model = Question
    template_name = 'question_list.html'
    context_object_name = 'question_list'


class QuestionView(generic.DetailView):
    model = Question
    template_name = 'question_detail.html'


### Option Views ###

class OptionListView(generic.ListView):
    model = Option
    template_name = 'option_list.html'
    context_object_name = 'option_list'


class OptionView(generic.DetailView):
    model = Option
    template_name = 'option_detail.html'
