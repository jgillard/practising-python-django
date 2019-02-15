from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views, views_experimental

router = DefaultRouter()
router.register(r'categories', views.CategoryDrfViewSet)
router.register(r'questions', views.QuestionDrfViewSet)
router.register(r'options', views.OptionDrfViewSet)
router.register(r'questionanswers', views.QuestionAnswerDrfViewSet)
router.register(r'transactions', views.TransactionDrfViewSet)


urlpatterns = [
    path('api/', include(router.urls)),

    path('',
         views.IndexView.as_view(), name='index'),

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

    path('transactions/',
         views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/new/',
         views.new_transaction, name='transaction_new'),
    path('transactions/new/<str:pk>',
         views.new_transaction, name='transaction_new'),
    path('transactions/<str:pk>/',
         views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('transactions/<str:pk>/delete/',
         views.TransactionDeleteView.as_view(), name='transaction_delete'),

    path('cashtransactions/new/',
         views.new_cash_transaction, name='cash_transaction_new'),

    path('lt/',
         views_experimental.LatestTransactionView.as_view(), name='latest_transaction'),
    path('week/',
         views_experimental.WeekView.as_view(), name='week'),
    path('week-cash/',
         views_experimental.WeekCashView.as_view(), name='week_cash'),
    path('analysis/',
         views_experimental.AnalysisView.as_view(), name='analysis_view'),
    path('ingest/',
         views_experimental.ingest_view, name='ingest_view'),
    path('categorytree/',
         views_experimental.category_tree_view, name='category_tree_view'),

    path('login/',
         views.login_view, name='login_view'),
    path('oauth-callback/',
         views.oauth_callback_view, name='oauth_callback'),

    path('webhooks/monzo/',
         views.webhook_monzo_view, name='webhook_monzo'),

    path('ajax/load-questions-for-category/',
         views.LoadQuestionsForCategoryView.as_view(), name='ajax_load_questions_for_category'),
    path('ajax/load-options-for-question/',
         views.LoadOptionsForQuestionView.as_view(), name='ajax_load_options_for_question'),

]
