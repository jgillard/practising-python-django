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
    path('questions/<int:pk>/', views.QuestionDetailView.as_view(), name='question_detail'),
    path('questions/new/', views.QuestionCreateView.as_view(), name='question_new'),
    path('questions/<int:pk>/edit/', views.QuestionUpdateView.as_view(), name='question_edit'),
    path('questions/<int:pk>/delete/', views.QuestionDeleteView.as_view(), name='question_delete'),

    path('options/', views.OptionListView.as_view(), name='option_list'),
    path('options/<int:pk>/', views.OptionDetailView.as_view(), name='option_detail'),
    path('options/new/', views.OptionCreateView.as_view(), name='option_new'),
    path('options/<int:pk>/edit/', views.OptionUpdateView.as_view(), name='option_edit'),
    path('options/<int:pk>/delete/', views.OptionDeleteView.as_view(), name='option_delete'),

    path('lt/', views.latest_monzo_transaction, name='latest_transaction'),
    path('txid/', views.TxidListView.as_view(), name='txid_list'),
    path('txid/new/', views.new_txid, name='txid_new'),
    path('txid/<str:txid>/', views.TxidDetailView.as_view(), name='txid_detail'),
    path('txid/new/<str:txid>', views.new_txid, name='txid_new'),
    path('txid/<str:txid>/delete/', views.TxidDeleteView.as_view(), name='txid_delete'),
    path('week/', views.week_list_view, name='week'),
    path('spending/', views.spending_view, name='spending_view'),
    path('ingest/', views.ingest_view, name='ingest_view'),

    path('ajax/load-questions-for-category/', views.load_questions_for_category,
         name='ajax_load_questions_for_category'),
    path('ajax/load-options-for-question/', views.load_options_for_question,
         name='ajax_load_options_for_question'),

]
