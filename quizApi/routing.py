from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # تم تعديل level_id إلى quiz_id للتوافق مع consumers.py
    re_path(r'ws/quiz/(?P<quiz_id>\d+)/$', consumers.QuizConsumer.as_asgi()),
]