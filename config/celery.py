import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# جدولة إطلاق المسابقة يومياً الساعة 03:00 مساءً بتوقيت الأردن
app.conf.beat_schedule = {
    'trigger-daily-3pm-quiz': {
        'task': 'quizApi.tasks.trigger_daily_quiz_at_3pm',
        'schedule': crontab(hour=15, minute=0),  # الساعة 15:00 (3:00 PM)
    },
}