from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers
from django.urls import path, include
from .views import ChatRoomViewSet, MessageViewSet, translate_message, accept_chat, decline_chat, mark_messages_read, \
    UploadImageView, test_simple
from .views import create_chatroom_api_no_auth  # 인증 없는 채팅방 생성 API
from .views import test_no_csrf

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

    path('chatrooms_create_no_auth/', create_chatroom_api_no_auth, name='create_chatroom_no_auth'),

    path('test_no_csrf/', csrf_exempt(test_no_csrf)),

    path('test_simple/', test_simple),
]