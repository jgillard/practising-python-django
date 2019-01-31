from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('categories/<int:category_id>/', views.category, name='category'),
    path('questions/<int:question_id>/', views.question, name='question'),
    path('options/<int:option_id>/', views.option, name='option'),
]
