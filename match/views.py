from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.contrib.auth import get_user_model
from .models import UserMatchPreference, MatchLike, MatchDislike
from .serializers import UserMatchPreferenceSerializer, MatchLikeSerializer
from chat.models import ChatRoom
from chat.views import create_chat_request
from users.serializers import UserSerializer

User = get_user_model()

class UserMatchPreferenceAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        preference, _ = UserMatchPreference.objects.get_or_create(user=request.user)
        serializer = UserMatchPreferenceSerializer(preference)

        return Response(serializer.data)

    def put(self, request):
        preference, _ = UserMatchPreference.objects.get_or_create(user=request.user)
        serializer = UserMatchPreferenceSerializer(preference, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RandomMatchUserAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            user_mode = UserMatchPreference.objects.get(user=user).mode
        except UserMatchPreference.DoesNotExist:
            return Response({"detail": "모드가 설정되어 있지 않습니다."}, status=400)

        liked_ids = MatchLike.objects.filter(from_user=user).values_list('to_user_id', flat=True)
        disliked_ids = MatchDislike.objects.filter(from_user=user).values_list('to_user_id', flat=True)
        excluded_ids = list(liked_ids) + list(disliked_ids) + [user.id]
        candidates = (
            UserMatchPreference.objects
            .filter(mode=user_mode)
            .exclude(user_id__in=excluded_ids)
            .exclude(user__user_type=user.user_type)
            .values_list('user_id', flat=True)
        )

        if not candidates:
            return Response({"detail": "추천할 사용자가 존재하지 않습니다."})

        import random
        chosen_id = random.choice(candidates)
        chosen_user = User.objects.get(id=chosen_id)

        serializer = UserSerializer(chosen_user)
        return Response(serializer.data, status=200)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_user(request, user_id):
    user = request.user

    try:
        target = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "사용자를 찾을 수 없습니다."}, status=404)

    # 이미 채팅방이 존재하는 경우
    chatroom_qs = ChatRoom.objects.filter(requester=user, receiver=target, is_active=False)
    if chatroom_qs.exists():
        return Response({"detail": "이미 대화가 존재합니다.", "chatroom_id": chatroom_qs.first().id}, status=400)

    # 좋아요 생성 및 채팅 요청 생성
    MatchLike.objects.create(from_user=user, to_user=target)
    chatroom = create_chat_request(user, target)

    return Response({"detail": "호감을 표시했습니다.", "chatroom_id": chatroom.id})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def dislike_user(request, user_id):
    user = request.user

    try:
        target = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "사용자를 찾을 수 없습니다."}, status=404)

    MatchDislike.objects.create(from_user=user, to_user=target)
    return Response({"detail": "다른 사용자를 찾습니다."})