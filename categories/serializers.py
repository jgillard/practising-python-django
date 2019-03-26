from rest_framework import serializers

from .models import Category, Option, Question, QuestionAnswer, TransactionData


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    questions = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='question-detail')

    class Meta:
        model = Category
        fields = ('id', 'url', 'name', 'parent', 'questions')


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    options = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='option-detail')

    class Meta:
        model = Question
        fields = ('id', 'url', 'title', 'category', 'answer_type', 'options')


class OptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Option
        fields = ('id', 'url', 'title', 'question')


class TransactionDataSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='td-detail')
    applicable_questions = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='question-detail')
    question_answers = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True)

    class Meta:
        model = TransactionData
        fields = ('id', 'url', 'category',
                  'applicable_questions', 'question_answers')


class QuestionAnswerSerializer(serializers.HyperlinkedModelSerializer):
    td = serializers.HyperlinkedIdentityField(view_name='td-detail')

    class Meta:
        model = QuestionAnswer
        fields = ('id', 'url', 'td', 'question',
                  'option_answer', 'number_answer')
