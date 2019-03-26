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
            category=self.parent_category,
            answer_type='N'
        )
        got = self.parent_category.questions
        self.assertEquals(list(got), [want])

    def test_category_get_questions_subcategory(self):
        # Ensures that questions from parent category are also returned
        q1 = models.Question.objects.create(
            title='attached to parent category',
            category=self.parent_category,
            answer_type='N'
        )

        q2 = models.Question.objects.create(
            title='attached to a subcategory',
            category=self.sub_category,
            answer_type='N'
        )

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
            category=self.category,
            answer_type='S'
        )

        self.option = models.Option.objects.create(
            title='option title',
            question=self.question
        )

    def test_question_get_options(self):
        got = self.question.options
        want = self.option
        self.assertEquals(list(got)[0], want)

    def test_question_get_hierarchical_name(self):
        got = self.question.get_hierarchical_name()
        want = f'{self.category} -> {self.question}'
        self.assertEquals(got, want)


class TestTransactionData(TestCase):
    def setUp(self):
        self.parent_category = models.Category.objects.create(
            name='top-level category',
            parent=None
        )

        self.sub_category = models.Category.objects.create(
            name='second-level category',
            parent=self.parent_category
        )

        self.td = models.TransactionData.objects.create(
            id='123',
            category=self.sub_category
        )

        self.question = models.Question.objects.create(
            title='attached to parent category',
            category=self.parent_category,
            answer_type='S'
        )

        self.option = models.Option.objects.create(
            title='option title',
            question=self.question
        )

        self.qa = models.QuestionAnswer.objects.create(
            td=self.td,
            question=self.question,
            option_answer=self.option,
            number_answer=None
        )

    def test_delete(self):
        # Test that dependent qas are deleted too
        self.td.delete()
        self.assertRaises(models.QuestionAnswer.DoesNotExist,
                          models.QuestionAnswer.objects.get, pk=self.td.pk)
        self.assertRaises(models.TransactionData.DoesNotExist,
                          models.TransactionData.objects.get, pk=self.td.pk)

    def test_transactiondata_get_applicable_questions(self):
        got = self.td.category.questions[0]
        want = self.question
        self.assertEquals(got, want)

    def test_transactiondata_get_question_answers(self):
        got = self.td.question_answers[0]
        want = self.qa
        self.assertEquals(got, want)
