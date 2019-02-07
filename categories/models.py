from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=30,
        unique=True,
    )

    parent = models.ForeignKey(
        'self',

        # prevent deletion of referenced upper-level categories
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

        # prevent deletion of referenced categories
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


class Option(models.Model):
    title = models.CharField(
        max_length=30,
    )

    question = models.ForeignKey(
        'Question',

        # deleting a question causes its options to be deleted
        on_delete=models.CASCADE,

        # only allow options for string questions
        limit_choices_to={'answer_type': 'S'},
    )

    def __str__(self):
        return f'{self.question.title} -> {self.title}'
