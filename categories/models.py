from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=30,
        unique=True,
    )

    parent = models.ForeignKey(
        'self',

        # prevent cascading Category deletions
        on_delete=models.PROTECT,

        # for top-level categories, allow null for the db
        null=True,

        # for top-level categories, allow blank for form validation
        blank=True,
    )

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/categories/{self.pk}'

    def get_hierarchical_name(self):
        if not self.parent:
            return self.name
        else:
            return f'{self.parent.name} -> {self.name}'

    @property
    def questions(self):
        category_questions = self.question_set.all()
        parent_category_questions = Question.objects.none()
        if self.parent:
            parent_category_questions = self.parent.question_set.all()
        return category_questions.union(parent_category_questions)


class Question(models.Model):
    OPTION_TYPE_CHOICES = (
        ('N', 'number'),
        ('S', 'string'),
    )

    title = models.CharField(
        max_length=30,
        unique=True,
    )

    category = models.ForeignKey(
        'Category',

        # prevent deletion of Category if it has Questions
        on_delete=models.PROTECT
    )

    answer_type = models.CharField(
        max_length=1,
        choices=OPTION_TYPE_CHOICES,
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f'/questions/{self.pk}'

    @property
    def options(self):
        return self.option_set.all()

    def get_hierarchical_name(self):
        return f'{self.category.name} -> {self.title}'


class Option(models.Model):
    title = models.CharField(
        max_length=30,
    )

    question = models.ForeignKey(
        'Question',

        # deleting a Question causes its Options to be deleted
        on_delete=models.CASCADE,

        # only allow options for string questions
        limit_choices_to={'answer_type': 'S'},
    )

    def __str__(self):
        return f'{self.question.title} -> {self.title}'

    def get_absolute_url(self):
        return f'/options/{self.pk}'


class TransactionData(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=30,
    )

    category = models.ForeignKey(
        'Category',

        # prevent deletion of Category if it has TransactionData
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name_plural = 'TransactionData'

    def __str__(self):
        return self.id

    def delete(self, *args, **kwargs):
        # delete dependent QuestionAnswers first
        for qa in self.question_answers:
            qa.delete()
        super().delete(*args, **kwargs)

    @property
    def applicable_questions(self):
        category_questions = Question.objects.filter(category=self.category)
        parent_category_questions = Question.objects.filter(
            category=self.category.parent)
        return category_questions.union(parent_category_questions)

    @property
    def question_answers(self):
        return self.questionanswer_set.all()


class QuestionAnswer(models.Model):
    txid = models.ForeignKey(
        'TransactionData',

        # prevent deletion of TransactionData if it has QuestionAnswer
        on_delete=models.PROTECT,
    )

    question = models.ForeignKey(
        'Question',

        # prevent deletion of Question if it has QuestionAnswer
        on_delete=models.PROTECT,
    )

    option_answer = models.ForeignKey(
        'Option',

        # prevent deletion of Option if it has QuestionAnswer
        on_delete=models.PROTECT,

        null=True,
        blank=True,
    )

    number_answer = models.IntegerField(
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = 'QuestionAnswers'


class MonzoUser(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=40,
        unique=True,
    )

    account_id = models.CharField(
        max_length=40
    )

    access_token = models.CharField(
        max_length=300,
    )

    refresh_token = models.CharField(
        max_length=300,
    )

    class Meta:
        verbose_name_plural = 'MonzoUsers'
