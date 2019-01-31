from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:category_id>/', views.category, name='category'),

    path('questions/', views.question_list, name='question_list'),
    path('questions/<int:question_id>/', views.question, name='question'),

    path('options/', views.option_list, name='option_list'),
    path('options/<int:option_id>/', views.option, name='option'),
]
