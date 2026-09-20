from rest_framework import serializers
from .models import *

class LiveQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveQuiz
        fields = ['id', 'title', 'start_time', 'entry_fee_coins', 'revive_cost_coins', 'is_active', 'is_finished']


class QuizParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizParticipant
        fields = ['id', 'quiz', 'score', 'is_eliminated', 'is_spectator', 'joined_at']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = ['id', 'order', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d']

class LiveQuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True) # جلب الأسئلة المرتبطة

    class Meta:
        model = LiveQuiz
        fields = ['id', 'title', 'start_time', 'entry_fee_coins', 'revive_cost_coins', 'is_active', 'is_finished', 'questions']