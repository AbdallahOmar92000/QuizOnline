import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LiveQuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.quiz_id = self.scope['url_route']['kwargs']['quiz_id']
        self.room_group_name = f'live_quiz_{self.quiz_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # معالجة رسائل البث الصادرة من Celery
    async def broadcast_quiz_start(self, event):
        await self.send(text_data=json.dumps(event))

    async def broadcast_question(self, event):
        await self.send(text_data=json.dumps(event))

    async def broadcast_answer_reveal(self, event):
        await self.send(text_data=json.dumps(event))

    async def broadcast_quiz_finish(self, event):
        await self.send(text_data=json.dumps(event))