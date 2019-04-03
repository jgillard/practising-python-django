from django.test import TestCase

import categories.models as models
from unittest import expectedFailure


class TestCategoryModel(TestCase):
    def setUp(self):
        self.parent_category = models.Category.objects.create(
            name='top-level category',
            parent=None
        )

        self.sub_category = models.Category.objects.create(
            name='second-level category',
            parent=self.parent_category
        )

    def test_category_get_hierarchical_name_toplevel(self):
        got = self.parent_category.get_hierarchical_name()
        want = f'{self.parent_category}'
        self.assertEquals(got, want)

    def test_category_get_hierarchical_name_subcategory(self):
        got = self.sub_category.get_hierarchical_name()
        want = f'{self.parent_category} -> {self.sub_category}'
        self.assertEquals(got, want)

    def test_category_get_questions_toplevel(self):
        want = models.Question.objects.create(
            title='attached to parent category',
            answer_type='N'
        )
        want.categories.add(self.parent_category)
        got = self.parent_category.questions
        self.assertEquals(list(got), [want])

    def test_category_get_questions_subcategory(self):
        # Ensures that questions from parent category are also returned
        q1 = models.Question.objects.create(
            title='attached to parent category',
            answer_type='N'
        )
        q1.categories.add(self.parent_category)

        q2 = models.Question.objects.create(
            title='attached to a subcategory',
            answer_type='N'
        )
        q2.categories.add(self.sub_category)

        got = self.sub_category.questions
        want = [q1, q2]
        self.assertEquals(list(got), want)


class TestQuestionModel(TestCase):
    def setUp(self):
        self.category = models.Category.objects.create(
            name='category',
            parent=None
        )

        self.question = models.Question.objects.create(
            title='question title',
            answer_type='S'
        )
        self.question.categories.add(self.category)

        self.option = models.Option.objects.create(
            title='option title',
            question=self.question
        )

    def test_question_get_options(self):
        got = self.question.options
        want = self.option
        self.assertEquals(list(got)[0], want)


class TestTransaction(TestCase):
    def setUp(self):
        self.parent_category = models.Category.objects.create(
            name='top-level category',
            parent=None
        )

        self.sub_category = models.Category.objects.create(
            name='second-level category',
            parent=self.parent_category
        )

        self.transaction = models.Transaction.objects.create(
            id='123',
            category=self.sub_category
        )

        self.cash_transaction = models.CashTransaction.objects.create(
            id='1234',
            category=self.parent_category,
            amount=-1,
            description='foobar',
            merchant_name='foobar'
        )

        self.question = models.Question.objects.create(
            title='attached to parent category',
            answer_type='S'
        )
        self.question.categories.add(self.parent_category)

        self.option = models.Option.objects.create(
            title='option title',
            question=self.question
        )

        self.qa = models.QuestionAnswer.objects.create(
            transaction=self.transaction,
            question=self.question,
            option_answer=self.option,
            number_answer=None
        )

    def test_delete(self):
        # Test that dependent qas are deleted too
        self.transaction.delete()
        self.assertRaises(models.QuestionAnswer.DoesNotExist,
                          models.QuestionAnswer.objects.get, pk=self.transaction.pk)
        self.assertRaises(models.Transaction.DoesNotExist,
                          models.Transaction.objects.get, pk=self.transaction.pk)

    def test_transaction_get_applicable_questions(self):
        got = self.transaction.category.questions[0]
        want = self.question
        self.assertEquals(got, want)

    def test_transaction_get_question_answers(self):
        got = self.transaction.question_answers[0]
        want = self.qa
        self.assertEquals(got, want)

    def test_transaction_is_cash_transaction_true(self):
        got = self.cash_transaction.is_cash_transaction
        want = True
        self.assertEquals(got, want)

    def test_transaction_is_cash_transaction_false(self):
        got = self.transaction.is_cash_transaction
        want = False
        self.assertEquals(got, want)
