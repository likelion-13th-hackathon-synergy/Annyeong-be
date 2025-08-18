from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoom(models.Model):
    requester = models.ForeignKey(User, related_name="requested_chatrooms", on_delete=models.CASCADE)  # 요청자
    receiver = models.ForeignKey(User, related_name="received_chatrooms", on_delete=models.CASCADE)  # 수신자
    chat_mode = models.CharField(max_length=20) # 생성 시점 모드
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)  # 대화 요청 수락 시 True

    def get_other_participant(self, user):
        # 현재 사용자 기준으로 상대 User 객체 반환
        if user == self.requester:
            return self.receiver
        return self.requester

class Message(models.Model):
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    translated_content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)