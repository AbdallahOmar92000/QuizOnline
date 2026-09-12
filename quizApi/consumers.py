# quizApi/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Question, UserQuizProgress

class QuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.level_id = self.scope['url_route']['kwargs']['level_id']
        self.room_group_name = f'quiz_level_{self.level_id}'
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

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

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'submit_answer':
            question_id = data.get('question_id')
            submitted_answer = data.get('answer', '').strip()

            is_correct = await self.check_and_save_answer(question_id, submitted_answer)

            await self.send(text_data=json.dumps({
                'type': 'answer_result',
                'question_id': question_id,
                'is_correct': is_correct,
            }))

    @database_sync_to_async
    def check_and_save_answer(self, question_id, submitted_answer):
        try:
            question = Question.objects.get(id=question_id)
            clean_correct = question.logo_name.replace(" ", "").upper()
            clean_submitted = submitted_answer.replace(" ", "").upper()

            if clean_correct == clean_submitted:
                progress, created = UserQuizProgress.objects.get_or_create(
                    user=self.user,
                    question=question
                )
                if not progress.is_solved:
                    progress.is_solved = True
                    progress.save()
                    self.user.coins += question.points
                    self.user.save()
                return True
            return False
        except Question.DoesNotExist:
            return False