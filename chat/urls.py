from rest_framework import routers
from django.urls import path, include
from .views import ChatRoomViewSet, MessageViewSet, translate_message, accept_chat, decline_chat, mark_messages_read, UploadImageView

router = routers.DefaultRouter()
router.register(r'chatrooms', ChatRoomViewSet, basename='chatroom')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),

    # 번역 API
    path('translate/', translate_message, name='translate-message'),

    # 채팅 요청 수락 API
    path('chatrooms/<int:chat_id>/accept/', accept_chat, name='accept-chat'),

    # 채팅 요청 거절 API
    path('chatrooms/<int:chat_id>/decline/', decline_chat, name='decline-chat'),

    # 메시지 읽음 처리 API
    path('chatrooms/<int:chat_id>/mark_read/', mark_messages_read, name='mark-messages-read'),

    # 이미지 첨부 API
    path('upload-image/', UploadImageView.as_view(), name='upload-image'),
]