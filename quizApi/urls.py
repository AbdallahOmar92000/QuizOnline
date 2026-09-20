from django.urls import path
from .views import *

urlpatterns = [
    path('upcoming/', UpcomingQuizView.as_view(), name='upcoming_quiz'),
    path('join/<int:quiz_id>/', JoinQuizView.as_view(), name='join_quiz'),
    path('quiz/<int:quiz_id>/submit-answer/', SubmitAnswerView.as_view(), name='submit-answer'),
    path('quiz/<int:quiz_id>/revive/', ReviveParticipantView.as_view(), name='revive-participant'),
    path('test-quiz/<int:quiz_id>/', test_quiz_view, name='test-quiz'),
]