from django.shortcuts import redirect, render
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


class CategoryListView(generic.ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'category_list'


class CategoryView(generic.DetailView):
    model = Category
    template_name = 'category_detail.html'


def category_new(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            category.save()
            return redirect('category_detail', pk=category.pk)
    else:
        form = CategoryForm()
        return render(request, 'category_new.html', {'form': form})


class QuestionListView(generic.ListView):
    model = Question
    template_name = 'question_list.html'
    context_object_name = 'question_list'


class QuestionView(generic.DetailView):
    model = Question
    template_name = 'question_detail.html'


class OptionListView(generic.ListView):
    model = Option
    template_name = 'option_list.html'
    context_object_name = 'option_list'


class OptionView(generic.DetailView):
    model = Option
    template_name = 'option_detail.html'
