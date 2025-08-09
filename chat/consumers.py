import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import ChatRoom, Message
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    # WebSocket 연결 시 실행
    async def connect(self):
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()  # 인증 안 된 사용자는 연결 거부
            return

        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # 그룹 참가
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    # WebSocket 단절 시 실행
    async def disconnect(self, close_code):
        # 그룹 나가기
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    @sync_to_async
    def save_message(self, sender_username, message, translated_content=None):
        chatroom = ChatRoom.objects.get(id=self.room_id)
        sender = User.objects.get(username=sender_username)
        msg = Message.objects.create(
            chatroom=chatroom,
            sender=sender,
            content=message or "",
            translated_content=translated_content or None,
        )
        chatroom.updated_at = timezone.now()
        chatroom.save(update_fields=['updated_at'])
        return msg.created_at.isoformat()

    # 클라이언트로부터 WebSocket으로 메시지 수신 시 실행
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        sender_username = data.get('sender')
        image_url = data.get('image')
        translated_content = data.get('translated_content')

        timestamp = await self.save_message(sender_username, message, translated_content)

        # 그룹에 메시지 전송
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_username,
                'timestamp': timestamp,
                'image': image_url,
                'translated_content': translated_content,
            }
        )

    # 그룹에서 메시지 수신 시 클라이언트에 전송
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
            'image': event.get('image'),
            'translated_content': event.get('translated_content'),
        }))