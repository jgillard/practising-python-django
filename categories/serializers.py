from rest_framework import serializers

from .models import Category, Option, TransactionData, Question


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'url', 'name', 'parent')


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'url', 'title', 'category', 'answer_type')


class OptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Option
        fields = ('id', 'url', 'title', 'question')


class TransactionDataSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='td-detail')

    class Meta:
        model = TransactionData
        fields = ('id', 'url', 'category')
