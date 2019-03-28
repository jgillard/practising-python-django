from rest_framework import serializers

from .models import *


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    questions = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='question-detail')
    child_categories = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='category-detail')

    class Meta:
        model = Category
        fields = ('id', 'url', 'name', 'parent',
                  'questions', 'child_categories')


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    options = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='option-detail')

    class Meta:
        model = Question
        fields = ('id', 'url', 'title', 'categories', 'answer_type', 'options')


class OptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Option
        fields = ('id', 'url', 'title', 'question')


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    applicable_questions = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='question-detail')
    question_answers = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'url', 'category',
                  'applicable_questions', 'question_answers')


class QuestionAnswerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = ('id', 'url', 'transaction', 'question',
                  'option_answer', 'number_answer')
