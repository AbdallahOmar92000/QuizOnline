import json
from channels.generic.websocket import AsyncWebsocketConsumer

class QuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.quiz_id = self.scope['url_route']['kwargs']['quiz_id']
        
        # التعديل هنا: إضافة live_ ليطابق Celery تماماً
        self.room_group_name = f'live_quiz_{self.quiz_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 1. استقبال بداية المسابقة
    async def broadcast_quiz_start(self, event):
        await self.send(text_data=json.dumps({
            'type': 'broadcast_quiz_start',
            'message': event.get('message'),
            'total_questions': event.get('total_questions')
        }))

    # 2. استقبال السؤال
    async def broadcast_question(self, event):
        await self.send(text_data=json.dumps({
            'type': 'broadcast_question',
            'question_id': event.get('question_id'),
            'order': event.get('order'),
            'total_questions': event.get('total_questions'),
            'question_text': event.get('question_text'),
            'options': event.get('options'),
            'duration_seconds': event.get('duration_seconds', 15)
        }))

    # 3. استقبال كشف الإجابة الصحيحة
    async def broadcast_answer_reveal(self, event):
        await self.send(text_data=json.dumps({
            'type': 'broadcast_answer_reveal',
            'question_id': event.get('question_id'),
            'correct_option': event.get('correct_option'),
            'revive_duration_seconds': event.get('revive_duration_seconds', 5),
            'is_last_question': event.get('is_last_question', False)
        }))

    # 4. استقبال نهاية المسابقة
    async def broadcast_quiz_finish(self, event):
        await self.send(text_data=json.dumps({
            'type': 'broadcast_quiz_finish',
            'message': event.get('message')
        }))