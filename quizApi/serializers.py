from rest_framework import serializers
from .models import LiveQuiz, QuizParticipant

class LiveQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveQuiz
        fields = ['id', 'title', 'start_time', 'entry_fee_coins', 'revive_cost_coins', 'is_active', 'is_finished']


class QuizParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizParticipant
        fields = ['id', 'quiz', 'score', 'is_eliminated', 'is_spectator', 'joined_at']