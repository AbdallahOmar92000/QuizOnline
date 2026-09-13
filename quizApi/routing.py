# quizApi/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/quiz/(?P<level_id>\d+)/$', consumers.LiveQuizConsumer.as_asgi()),
]