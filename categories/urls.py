from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('',
         views.IndexView.as_view(), name='index'),
    path('api/',
         views.api_root),

    path('categories/',
         views.CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/',
         views.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/new/',
         views.CategoryCreateView.as_view(), name='category_new'),
    path('categories/<int:pk>/edit/',
         views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/',
         views.CategoryDeleteView.as_view(), name='category_delete'),

    path('api/categories/',
         views.CategoryListDrf.as_view(), name='category-list'),
    path('api/categories/<int:pk>/',
         views.CategoryDetailDrf.as_view(), name='category-detail'),

    path('questions/',
         views.QuestionListView.as_view(), name='question_list'),
    path('questions/<int:pk>/',
         views.QuestionDetailView.as_view(), name='question_detail'),
    path('questions/new/',
         views.QuestionCreateView.as_view(), name='question_new'),
    path('questions/<int:pk>/edit/',
         views.QuestionUpdateView.as_view(), name='question_edit'),
    path('questions/<int:pk>/delete/',
         views.QuestionDeleteView.as_view(), name='question_delete'),

    path('api/questions/',
         views.QuestionListDrf.as_view(), name='question-list'),
    path('api/questions/<int:pk>/',
         views.QuestionDetailDrf.as_view(), name='question-detail'),

    path('options/',
         views.OptionListView.as_view(), name='option_list'),
    path('options/<int:pk>/',
         views.OptionDetailView.as_view(), name='option_detail'),
    path('options/new/',
         views.OptionCreateView.as_view(), name='option_new'),
    path('options/<int:pk>/edit/',
         views.OptionUpdateView.as_view(), name='option_edit'),
    path('options/<int:pk>/delete/',
         views.OptionDeleteView.as_view(), name='option_delete'),

    path('api/options/',
         views.OptionListDrf.as_view(), name='option-list'),
    path('api/options/<int:pk>/',
         views.OptionDetailDrf.as_view(), name='option-detail'),

    path('td/',
         views.TdListView.as_view(), name='td_list'),
    path('td/new/',
         views.new_td, name='td_new'),
    path('td/new/<str:pk>',
         views.new_td, name='td_new'),
    path('td/<str:pk>/',
         views.TdDetailView.as_view(), name='td_detail'),
    path('td/<str:pk>/delete/',
         views.TdDeleteView.as_view(), name='td_delete'),

    path('api/td/',
         views.TdListDrf.as_view(), name='td-list'),
    path('api/td/<str:pk>/',
         views.TdDetailDrf.as_view(), name='td-detail'),

    path('api/questionanswer/',
         views.QuestionAnswerListDrf.as_view(), name='questionanswer-list'),
    path('api/questionanswer/<int:pk>/',
         views.QuestionAnswerDetailDrf.as_view(), name='questionanswer-detail'),

    path('lt/',
         views.LatestTransactionView.as_view(), name='latest_transaction'),
    path('week/',
         views.WeekView.as_view(), name='week'),
    path('analysis/',
         views.AnalysisView.as_view(), name='analysis_view'),
    path('ingest/',
         views.ingest_view, name='ingest_view'),

    path('login/',
         views.login_view, name='login_view'),
    path('oauth-callback/',
         views.oauth_callback_view, name='oauth_callback'),

    path('ajax/load-questions-for-category/',
         views.LoadQuestionsForCategoryView.as_view(), name='ajax_load_questions_for_category'),
    path('ajax/load-options-for-question/',
         views.LoadOptionsForQuestionView.as_view(), name='ajax_load_options_for_question'),

]

urlpatterns = format_suffix_patterns(urlpatterns)
