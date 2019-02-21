from django.test import SimpleTestCase
from django.urls import resolve, reverse

import categories.views as views


class TestUrls(SimpleTestCase):

    def test_resolves_index(self):
        url = reverse('index')
        self.assertEquals(resolve(url).func, views.index)

    def test_resolves_category_list(self):
        url = reverse('category_list')
        self.assertEquals(resolve(url).func.view_class, views.CategoryListView)

    def test_resolves_category_detail(self):
        url = reverse('category_detail', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.CategoryDetailView)

    def test_resolves_category_new(self):
        url = reverse('category_new')
        self.assertEquals(resolve(url).func.view_class, views.CategoryCreateView)

    def test_resolves_category_edit(self):
        url = reverse('category_edit', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.CategoryUpdateView)

    def test_resolves_category_delete(self):
        url = reverse('category_delete', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.CategoryDeleteView)

    def test_resolves_question_list(self):
        url = reverse('question_list')
        self.assertEquals(resolve(url).func.view_class, views.QuestionListView)

    def test_resolves_question_detail(self):
        url = reverse('question_detail', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.QuestionDetailView)

    def test_resolves_question_new(self):
        url = reverse('question_new')
        self.assertEquals(resolve(url).func.view_class, views.QuestionCreateView)

    def test_resolves_question_edit(self):
        url = reverse('question_edit', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.QuestionUpdateView)

    def test_resolves_question_delete(self):
        url = reverse('question_delete', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.QuestionDeleteView)

    def test_resolves_option_list(self):
        url = reverse('option_list')
        self.assertEquals(resolve(url).func.view_class, views.OptionListView)

    def test_resolves_option_detail(self):
        url = reverse('option_detail', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.OptionDetailView)

    def test_resolves_option_new(self):
        url = reverse('option_new')
        self.assertEquals(resolve(url).func.view_class, views.OptionCreateView)

    def test_resolves_option_edit(self):
        url = reverse('option_edit', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.OptionUpdateView)

    def test_resolves_option_delete(self):
        url = reverse('option_delete', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.OptionDeleteView)

    def test_resolves_txid_list(self):
        url = reverse('txid_list')
        self.assertEquals(resolve(url).func.view_class, views.TxidListView)

    def test_resolves_txid_new(self):
        url = reverse('txid_new')
        self.assertEquals(resolve(url).func, views.new_txid)

    def test_resolves_txid_new_with_arg(self):
        url = reverse('txid_new', args=[1])
        self.assertEquals(resolve(url).func, views.new_txid)

    def test_resolves_txid_detail(self):
        url = reverse('txid_detail', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.TxidDetailView)

    # NOT IMPLEMENTED
    # def test_resolves_txid_edit(self):
    #     url = reverse('txid_edit', args=[1])
    #     self.assertEquals(resolve(url).func.view_class, views.TxidUpdateView)

    def test_resolves_txid_delete(self):
        url = reverse('txid_delete', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.TxidDeleteView)

    def test_resolves_latest_transaction(self):
        url = reverse('latest_transaction')
        self.assertEquals(resolve(url).func, views.latest_monzo_transaction)

    def test_resolves_week(self):
        url = reverse('week')
        self.assertEquals(resolve(url).func, views.week_view)

    def test_resolves_analysis_view(self):
        url = reverse('analysis_view')
        self.assertEquals(resolve(url).func, views.analysis_view)

    def test_resolves_ingest_view(self):
        url = reverse('ingest_view')
        self.assertEquals(resolve(url).func, views.ingest_view)

    def test_resolves_login(self):
        url = reverse('login_view')
        self.assertEquals(resolve(url).func, views.login_view)

    def test_resolves_oauth_callback(self):
        url = reverse('oauth_callback')
        self.assertEquals(resolve(url).func, views.oauth_callback_view)

    def test_resolves_ajax_load_questions_for_category(self):
        url = reverse('ajax_load_questions_for_category')
        self.assertEquals(resolve(url).func, views.load_questions_for_category)

    def test_resolves_ajax_load_options_for_question(self):
        url = reverse('ajax_load_options_for_question')
        self.assertEquals(resolve(url).func, views.load_options_for_question)
