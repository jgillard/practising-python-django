from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import Category, Question, Option


def index(request):
    context = {
        'category_list': Category.objects.all(),
        'question_list': Question.objects.all(),
        'option_list': Option.objects.all(),
    }
    return render(request, 'index.html', context)


def category_list(request):
    context = {'category_list': Category.objects.all()}
    return render(request, 'category_list.html', context)


def category(request, category_id):
    context = {'category': get_object_or_404(Category, id=category_id)}
    return render(request, 'category.html', context)


def question_list(request):
    context = {'question_list': Question.objects.all()}
    return render(request, 'question_list.html', context)


def question(request, question_id):
    context = {'question': get_object_or_404(Question, id=question_id)}
    return render(request, 'question.html', context)


def option_list(request):
    context = {'option_list': Option.objects.all()}
    return render(request, 'option_list.html', context)


def option(request, option_id):
    context = {'option': get_object_or_404(Option, id=option_id)}
    return render(request, 'option.html', context)
