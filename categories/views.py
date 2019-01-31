from django.http import Http404
from django.shortcuts import render

from .models import Category, Question, Option


def index(request):
    latest_category_list = Category.objects.all()[:5]
    context = {'latest_category_list': latest_category_list}
    return render(request, 'index.html', context)


def category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        context = {'category': category}
    except Category.DoesNotExist:
        raise Http404("Category does not exist")
    return render(request, 'category.html', context)


def question(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
        context = {'question': question}
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'question.html', context)


def option(request, option_id):
    try:
        option = Option.objects.get(id=option_id)
        context = {'option': option}
    except Option.DoesNotExist:
        raise Http404("Option does not exist")
    return render(request, 'option.html', context)
