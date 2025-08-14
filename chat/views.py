import requests
from django.db.models import Count, Q
from django.conf import settings
from django.utils import timezone

from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    # 채팅 목록 조회
    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(
            Q(requester=user) | Q(receiver=user)
        ).annotate(
            unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=user))
        ).order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        chatroom_id = self.request.query_params.get('chatroom')
        qs = Message.objects.all()
        if chatroom_id:
            qs = qs.filter(chatroom_id=chatroom_id)
        return qs.order_by('created_at')

    def perform_create(self, serializer):
        # 메시지 저장 및 발신자 지정
        message = serializer.save(sender=self.request.user)

        # 메시지 저장 후 채팅방 갱신
        message.chatroom.updated_at = timezone.now()
        message.chatroom.save(update_fields=['updated_at'])

        # WebSocket 그룹 이름 생성
        group_name = f'chat_{message.chatroom.id}'

        # 메시지 직렬화
        message_data = MessageSerializer(message).data

        # 채널 레이어 가져오기
        channel_layer = get_channel_layer()

        # 그룹에 메시지 전송
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'chat_message',
                'message': message_data,
            }
        )

        return message

class UploadImageView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        # 요청에서 이미지 파일과 채팅방 ID 추출
        file_obj = request.data.get('image')
        chatroom_id = request.data.get('chatroom')
        content = request.data.get('content', '')

        if not file_obj or not chatroom_id:
            # 이미지 또는 채팅방 ID가 없을 시 400 Bad Request 응답
            return Response({'error': '이미지 파일과 채팅방 ID가 필요합니다.'}, status=400)

        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
        except ChatRoom.DoesNotExist:
            # 채팅방이 없을 시 404 Not Found 응답
            return Response({'error': '존재하지 않는 채팅방입니다.'}, status=404)

        # 메시지 객체 생성
        message = Message.objects.create(
            chatroom=chatroom,
            sender=request.user,
            content=content,
            image=file_obj,
        )

        # WebSocket 전송
        channel_layer = get_channel_layer()
        group_name = f'chat_{chatroom.id}'
        message_data = MessageSerializer(message).data
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'chat_message',
                'message': message_data,
            }
        )

        serializer = MessageSerializer(message)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_messages_read(request, chat_id):
    user = request.user

    try:
        chatroom = ChatRoom.objects.get(id=chat_id)
    except ChatRoom.DoesNotExist:
        return Response({'error': '존재하지 않는 채팅방입니다.'}, status=404)

    if user != chatroom.receiver and user != chatroom.requester:
        return Response({'error': '접근 권한이 없습니다.'}, status=403)

    Message.objects.filter(chatroom=chatroom, is_read=False).exclude(sender=user).update(is_read=True)

    return Response({'message': '메시지가 읽음 처리되었습니다.'})

def create_chat_request(from_user, to_user):
    # 채팅방 생성
    chatroom = ChatRoom.objects.create(requester=from_user, receiver=to_user, is_active=False)

    # 초대 메시지 자동 생성
    intro_msg = f"(요청) 새로운 인연이 시작될까요? {from_user.username} 님이 호감을 표시했어요!"
    Message.objects.create(chatroom=chatroom, sender=from_user, content=intro_msg)

    return chatroom

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_chat(request, chat_id):
    # 사용자만 처리 가능
    user = request.user

    try:
        chatroom = ChatRoom.objects.get(id=chat_id, is_active=False)
    except ChatRoom.DoesNotExist:
        return Response({'error': '존재하지 않거나 이미 처리된 요청입니다.'}, status=404)

    if user != chatroom.receiver:
        return Response({'error': '접근 권한이 없습니다.'}, status=403)

    chatroom.is_active = True
    chatroom.save()

    return Response({'message': '대화 요청을 수락했습니다.'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def decline_chat(request, chat_id):
    user = request.user
    try:
        chatroom = ChatRoom.objects.get(id=chat_id, is_active=False)
    except ChatRoom.DoesNotExist:
        return Response({'error': '존재하지 않거나 이미 처리된 요청입니다.'}, status=404)

    if user != chatroom.receiver:
        return Response({'error': '접근 권한이 없습니다.'}, status=403)

    chatroom.delete()

    return Response({'message': '대화 요청을 거절했습니다.'})

def get_user_language(user):
    # User 모델의 service_language 필드 선택
    if hasattr(user, 'service_language') and user.service_language:
        return user.service_language.upper()

    # 기본 값: 한국어
    return "KO"

def call_translation_api(text, user):
    api_key = settings.DEEPL_API_KEY
    if not api_key:
        raise Exception("DEEPL API KEY가 존재하지 않습니다.")

    target_lang = get_user_language(user)
    url = "https://api-free.deepl.com/v2/translate"

    data = {
        'auth_key': api_key,
        'text': text,
        'target_lang': target_lang,
    }

    response = requests.post(url, data=data)
    response.raise_for_status()  # HTTP 오류 체크
    result = response.json()
    return result['translations'][0]['text']

@api_view(['POST'])
def translate_message(request):
    # 요청에서 번역할 메시지를 GET
    text = request.data.get('text')
    if not text:
        # 텍스트가 없을 시 400 Bad Request 응답
        return Response({"error": "텍스트가 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        translated = call_translation_api(text, request.user)
        target_lang = get_user_language(request.user)
        return Response({"translated_text": translated, "target_language": target_lang})
    except Exception as e:
        # 번역 중 오류 발생 시 500 Internal Server Error 응답
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)