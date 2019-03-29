import logging

from django import forms
from django.core.exceptions import ValidationError

from .models import *

logger = logging.getLogger(__name__)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'parent', 'hidden')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Category.objects.filter(hidden=False)
        self.fields['parent'].label_from_instance = lambda obj: obj.get_hierarchical_name()

    def clean(self):
        cleaned_data = super().clean()

        form_parent = cleaned_data.get('parent')

        if form_parent and form_parent.name == self.instance.name:
            raise ValidationError('Category cannot be its own parent')

        if form_parent and form_parent.parent:
            raise ValidationError('Cannot currently nest Categories that deep')

        return cleaned_data


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('title', 'categories', 'answer_type')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categories'].queryset = Category.objects.filter(
            hidden=False)
        self.fields['categories'].label_from_instance = lambda obj: obj.get_hierarchical_name()

    def clean(self):
        logger.error('in clean')
        cleaned_data = super().clean()

        form_answer_type = cleaned_data.get('answer_type')

        question_id = self.instance.pk

        # prevent changing form type to number if options referencing the question exist
        if form_answer_type == 'N':
            question_options_count = Option.objects.filter(
                question__exact=question_id).count()
            if question_options_count > 0:
                raise ValidationError(
                    'Changing answer_type to number cannot occur if there are options referencing it')

        return cleaned_data


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ('title', 'question')


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ('id', 'category')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(
            hidden=False)
        self.fields['category'].label_from_instance = lambda obj: obj.get_hierarchical_name()


class QuestionAnswerForm(forms.ModelForm):
    class Meta:
        model = QuestionAnswer
        fields = ('question', 'option_answer', 'number_answer')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['question'].queryset = Question.objects.all()
        self.fields['question'].required = False
        self.fields['option_answer'].queryset = Option.objects.all()
