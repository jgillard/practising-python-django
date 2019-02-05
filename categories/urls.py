from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/new/', views.CategoryCreateView.as_view(), name='category_new'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    path('questions/', views.QuestionListView.as_view(), name='question_list'),
    path('questions/<int:pk>/', views.QuestionView.as_view(), name='question_detail'),

    path('options/', views.OptionListView.as_view(), name='option_list'),
    path('options/<int:pk>/', views.OptionView.as_view(), name='option_detail'),
]
