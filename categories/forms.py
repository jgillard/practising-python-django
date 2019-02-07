import logging

from django.forms import ModelForm
from django.core.exceptions import ValidationError

from .models import Category, Question, Option

logger = logging.getLogger(__name__)


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'parent')

    def clean(self):
        cleaned_data = super().clean()

        form_parent = cleaned_data.get('parent')

        if form_parent and form_parent.name == self.instance.name:
            raise ValidationError('Category cannot be its own parent')

        return cleaned_data


class QuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ('title', 'category', 'answer_type')

    def clean(self):
        logger.error('in clean')
        cleaned_data = super().clean()

        form_answer_type = cleaned_data.get('answer_type')

        question_id = self.instance.pk

        # prevent changing form type to number if options referencing the question exist
        if form_answer_type == 'N':
            question_options_count = Option.objects.filter(question__exact=question_id).count()
            if question_options_count > 0:
                raise ValidationError('Changing answer_type to number cannot occur if there are options referencing it')

        return cleaned_data


class OptionForm(ModelForm):
    class Meta:
        model = Option
        fields = ('title', 'question')
