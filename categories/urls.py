from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/', views.CategoryView.as_view(), name='category_detail'),
    path('categories/new/', views.category_new, name='category_new'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),

    path('questions/', views.QuestionListView.as_view(), name='question_list'),
    path('questions/<int:pk>/', views.QuestionView.as_view(), name='question_detail'),

    path('options/', views.OptionListView.as_view(), name='option_list'),
    path('options/<int:pk>/', views.OptionView.as_view(), name='option_detail'),
]
