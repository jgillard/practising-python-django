import logging

from django.forms import ModelForm
from django.core.exceptions import ValidationError

from .models import Category

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
