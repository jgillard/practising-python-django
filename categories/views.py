from django.http import Http404
from django.shortcuts import render

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
    try:
        context = {'category': Category.objects.get(id=category_id)}
    except Category.DoesNotExist:
        raise Http404("Category does not exist")
    return render(request, 'category.html', context)


def question_list(request):
    context = {'question_list': Question.objects.all()}
    return render(request, 'question_list.html', context)


def question(request, question_id):
    try:
        context = {'question': Question.objects.get(id=question_id)}
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'question.html', context)


def option_list(request):
    context = {'option_list': Option.objects.all()}
    return render(request, 'option_list.html', context)


def option(request, option_id):
    try:
        context = {'option': Option.objects.get(id=option_id)}
    except Option.DoesNotExist:
        raise Http404("Option does not exist")
    return render(request, 'option.html', context)
