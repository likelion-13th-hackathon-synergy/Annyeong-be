import requests

from django.db import models
from django.db.models import Count, Q
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny] # 테스트용

    def get_queryset(self):
        # 채팅 목록 조회
        user = self.request.user

        # 테스트용
        if not user.is_authenticated:
            from django.contrib.auth.models import User
            user = User.objects.first()  # 임시로 첫 번째 유저를 사용

        return ChatRoom.objects.filter(
            models.Q(requester=user) | models.Q(receiver=user)
        ).annotate(
            unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=user))
        ).order_by('-updated_at')

    def perform_create(self, serializer):
        from django.contrib.auth.models import User

        user = self.request.user
        if not user.is_authenticated:
            try:
                user = User.objects.get(id=1)  # 테스트용 유저 ID
            except User.DoesNotExist:
                from rest_framework import serializers
                raise serializers.ValidationError("테스트용 유저가 없습니다.")

        serializer.save(requester=user)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]  # 테스트용
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        chatroom_id = self.request.query_params.get('chatroom')
        qs = Message.objects.all()
        if chatroom_id:
            qs = qs.filter(chatroom_id=chatroom_id)
        return qs.order_by('created_at')

    def perform_create(self, serializer):
        # 로그인 없이 테스트용 유저 지정 (예: id=1)
        from django.contrib.auth.models import User

        try:
            user = User.objects.get(id=1)
        except User.DoesNotExist:
            user = None

        message = serializer.save(sender=user)  # user를 sender로 지정

        # 메시지 저장 및 발신자 지정
        # message = serializer.save(sender=self.request.user)

        # 메시지 저장 후 채팅방 갱신
        message.chatroom.updated_at = timezone.now()
        message.chatroom.save(update_fields=['updated_at'])
        return message

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

class UploadImageView(APIView):
    permission_classes = []
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

        # 테스트용 코드
        from django.contrib.auth.models import User

        user = request.user
        if not user.is_authenticated:
            try:
                user = User.objects.get(id=1)  # 테스트용 유저 ID
            except User.DoesNotExist:
                return Response({'error': '테스트용 유저가 없습니다.'}, status=400)

        # 메시지 객체 생성
        message = Message.objects.create(
            chatroom=chatroom,
            # sender=request.user,
            sender=user, # 테스트용
            content=content,
            image=file_obj,
        )

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
@permission_classes([AllowAny])
@authentication_classes([])

@csrf_exempt
def create_chatroom_api_no_auth(request):
    print("create_chatroom_api_no_auth 호출됨")
    print("request.user:", request.user)

    request._authenticator = None

    from_user_id = request.data.get('requester_id')
    to_user_id = request.data.get('receiver_id')

    if not from_user_id or not to_user_id:
        return Response({"error": "requester_id와 receiver_id가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        from django.contrib.auth.models import User
        from_user = User.objects.get(id=from_user_id)
        to_user = User.objects.get(id=to_user_id)
    except User.DoesNotExist:
        return Response({"error": "존재하지 않는 사용자입니다."}, status=status.HTTP_404_NOT_FOUND)

    chatroom = create_chat_request(from_user, to_user)

    from .serializers import ChatRoomSerializer
    serializer = ChatRoomSerializer(chatroom)

    return Response(serializer.data, status=status.HTTP_201_CREATED)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def test_simple(request):
    print("test_simple 호출됨")
    return Response({"message": "simple test success"})

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def test_no_csrf(request):
    return Response({"message": "CSRF exempt test success"})

def create_chat_request(from_user, to_user):
    # 채팅방 생성
    chatroom = ChatRoom.objects.create(requester=from_user, receiver=to_user, is_active=False)

    # 초대 메시지 자동 생성
    intro_msg = f"(요청) 새로운 인연이 시작될까요? {from_user.username} 님이 호감을 표시했어요!"
    Message.objects.create(chatroom=chatroom, sender=from_user, content=intro_msg)

    return chatroom

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def accept_chat(request, chat_id):
    # 테스트용 코드
    from django.contrib.auth.models import User

    user = None
    try:
        user = User.objects.get(id=2)  # 테스트용 유저 지정
    except User.DoesNotExist:
        return Response({'error': '테스트용 유저가 없습니다.'}, status=400)

    try:
        chatroom = ChatRoom.objects.get(id=chat_id, is_active=False)
    except ChatRoom.DoesNotExist:
        return Response({'error': '존재하지 않거나 이미 처리된 요청입니다.'}, status=404)

    # 사용자만 처리 가능
    # if request.user != chatroom.receiver:
    if user != chatroom.receiver: # 테스트용
        return Response({'error': '접근 권한이 없습니다.'}, status=403)

    chatroom.is_active = True
    chatroom.save()

    return Response({'message': '대화 요청을 수락했습니다.'})

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def decline_chat(request, chat_id):
    # 테스트용 코드
    from django.contrib.auth.models import User

    user = None
    try:
        user = User.objects.get(id=2)  # 테스트용 유저 지정
    except User.DoesNotExist:
        return Response({'error': '테스트용 유저가 없습니다.'}, status=400)

    try:
        chatroom = ChatRoom.objects.get(id=chat_id, is_active=False)
    except ChatRoom.DoesNotExist:
        return Response({'error': '존재하지 않거나 이미 처리된 요청입니다.'}, status=404)

    # if request.user != chatroom.receiver:
    if user != chatroom.receiver:  # 테스트용
        return Response({'error': '접근 권한이 없습니다.'}, status=403)

    chatroom.delete()

    return Response({'message': '대화 요청을 거절했습니다.'})

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

def get_user_language(user):
    # 유저 프로필에서 받아오는 로직 구현 (KO, EN, ZH, JA, VI, TH)
    if hasattr(user, 'profile') and user.profile.preferred_language:
        return user.profile.preferred_language.upper()

    # 기본 값: 한국어
    return "KO"

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

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def mark_messages_read(request, chat_id):
    # 테스트용 코드
    from django.contrib.auth.models import User

    user = None
    try:
        user = User.objects.get(id=2)  # 테스트용 유저 지정
    except User.DoesNotExist:
        return Response({'error': '테스트용 유저가 없습니다.'}, status=400)

    try:
        chatroom = ChatRoom.objects.get(id=chat_id)
    except ChatRoom.DoesNotExist:
        return Response({'error': '존재하지 않는 채팅방입니다.'}, status=404)

    # if request.user != chatroom.receiver and request.user != chatroom.requester:
    if user != chatroom.receiver and user != chatroom.requester:  # 테스트용
        return Response({'error': '접근 권한이 없습니다.'}, status=403)

    # 안 읽은 메시지 중 사용자가 보낸 메시지는 제외하고 is_read=True로 변경
    # Message.objects.filter(chatroom=chatroom, is_read=False).exclude(sender=request.user).update(is_read=True)
    Message.objects.filter(chatroom=chatroom, is_read=False).exclude(sender=user).update(is_read=True) # 테스트용

    return Response({'message': '메시지가 읽음 처리되었습니다.'})