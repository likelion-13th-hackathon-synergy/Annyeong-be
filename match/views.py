from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.contrib.auth import get_user_model
from .models import UserMatchPreference, MatchLike, MatchDislike
from .serializers import UserMatchPreferenceSerializer
from chat.models import ChatRoom
from chat.views import create_chat_request

User = get_user_model()

def get_test_user():
    # 임시로 첫 번째 유저를 테스트용으로 반환
    return User.objects.first()

class UserMatchPreferenceAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [] # 테스트용

    def get(self, request):
        # 테스트용
        user = get_test_user()
        if not user:
            return Response({"detail": "테스트용 유저가 없습니다."}, status=400)

        # preference, _ = UserMatchPreference.objects.get_or_create(user=request.user)
        preference, _ = UserMatchPreference.objects.get_or_create(user=user) # 테스트용
        serializer = UserMatchPreferenceSerializer(preference)
        return Response(serializer.data)

    def put(self, request):
        # 테스트용
        user = get_test_user()
        if not user:
            return Response({"detail": "테스트용 유저가 없습니다."}, status=400)

        # preference, _ = UserMatchPreference.objects.get_or_create(user=request.user)
        preference, _ = UserMatchPreference.objects.get_or_create(user=user)  # 테스트용
        serializer = UserMatchPreferenceSerializer(preference, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RandomMatchUserAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [] # 테스트용

    def get(self, request):
        # user = request.user
        # 테스트용
        user = get_test_user()
        if not user:
            return Response({"detail": "테스트용 유저가 없습니다."}, status=400)

        try:
            user_mode = UserMatchPreference.objects.get(user=user).mode
        except UserMatchPreference.DoesNotExist:
            return Response({"detail": "모드가 설정되어 있지 않습니다."}, status=400)

        liked_ids = MatchLike.objects.filter(from_user=user).values_list('to_user_id', flat=True)
        excluded_ids = list(liked_ids) + [user.id]

        candidates = UserMatchPreference.objects.filter(mode=user_mode).exclude(user_id__in=excluded_ids).values_list('user_id', flat=True)

        if not candidates:
            return Response({"detail": "추천할 사용자가 존재하지 않습니다."})

        import random
        chosen_id = random.choice(candidates)
        chosen_user = User.objects.get(id=chosen_id)

        return Response({"id": chosen_user.id, "username": chosen_user.username})

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
@permission_classes([AllowAny]) # 테스트용
def like_user(request, user_id):
    # user = request.user
    # 테스트용
    user = get_test_user()
    if not user:
        return Response({"detail": "테스트용 유저가 없습니다."}, status=400)

    try:
        target = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "사용자를 찾을 수 없습니다."}, status=404)

    # 이미 좋아요 기록이 있으면 중복 방지
    if MatchLike.objects.filter(from_user=user, to_user=target).exists():
        return Response({"detail": "이미 호감을 표시한 사용자입니다."}, status=400)

    # 이미 채팅방이 존재하는 경우
    chatroom_qs = ChatRoom.objects.filter(
        requester=user,
        receiver=target,
        is_active=False,
    )
    if chatroom_qs.exists():
        return Response({"detail": "이미 대화 요청이 존재합니다.", "chatroom_id": chatroom_qs.first().id}, status=400)

    # 좋아요 생성 및 채팅 요청 생성
    MatchLike.objects.create(from_user=user, to_user=target)
    chatroom = create_chat_request(user, target)

    return Response({"detail": "호감을 표시했습니다.", "chatroom_id": chatroom.id})

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
@permission_classes([AllowAny]) # 테스트용
def dislike_user(request, user_id):
    # user = request.user
    # 테스트용
    user = get_test_user()
    if not user:
        return Response({"detail": "테스트용 유저가 없습니다."}, status=400)

    try:
        target = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "사용자를 찾을 수 없습니다."}, status=404)

    MatchDislike.objects.create(from_user=user, to_user=target)
    return Response({"detail": "다른 사용자를 찾습니다."})