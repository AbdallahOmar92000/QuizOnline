from django.urls import path
from .views import UpcomingQuizView, JoinQuizView

urlpatterns = [
    path('upcoming/', UpcomingQuizView.as_view(), name='upcoming_quiz'),
    path('join/<int:quiz_id>/', JoinQuizView.as_view(), name='join_quiz'),
]