from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.contrib.auth import get_user_model

from .models import Review
from chat.models import ChatRoom

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Review

User = get_user_model()

PERSONALITY_CHOICES = {
    "personality_1": "이야기를 잘 들어줘요",
    "personality_2": "유머 감각이 뛰어나요",
    "personality_3": "대화가 재미있어요",
    "personality_4": "긍정적인 마인드예요",
    "personality_5": "친근하고 따뜻해요",
    "personality_6": "배려심이 깊어요",
    "personality_7": "지식이 풍부해요",
    "personality_8": "호기심이 많아요",
    "personality_9": "이해심이 많아요",
    "personality_10": "정직하고 솔직해요",
    "personality_11": "적극적이고 활발해요",
    "personality_12": "신뢰할 수 있어요",
}

class CreateReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, chat_room_id):
        chatroom = get_object_or_404(ChatRoom, id=chat_room_id)

        #채팅방이 활성화되지 않았다면
        if not chatroom.is_active:
            return Response(
                {"detail": "아직 수락되지 않은 대화입니다."},
                status=status.HTTP_403_FORBIDDEN)

        #요청 사용자가 채팅방 참가자가 아니라면
        if request.user not in [chatroom.requester, chatroom.receiver]:
            return Response(
                {"detail": "이 대화방의 참가자가 아닙니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        #상대방 찾기
        other_user = chatroom.get_other_participant(request.user)

        #이미 이 채팅에서 후기 작성했는지 확인
        if Review.objects.filter(author=request.user, target_user=other_user, chatroom=chatroom).exists():
            return Response(
                {"detail": "이미 후기를 작성했습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        selected_personalities = request.data.get("personalities", [])

        if not isinstance(selected_personalities, list):
            return Response(
                {"detail": "personalities는 리스트 형식이어야 합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(selected_personalities) > 5:
            return Response(
                {"detail": "최대 5개까지 선택할 수 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        #Review 객체 생성
        review = Review.objects.create(
            author=request.user,
            target_user=other_user,
            chatroom=chatroom,
            **{key: (key in selected_personalities) for key in PERSONALITY_CHOICES.keys()},
        )
        return Response(
            {"detail": "후기가 작성되었습니다.", "review_id": review.id,},
            status=status.HTTP_201_CREATED,
        )

class UserReviewListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        reviews = Review.objects.filter(target_user=user)

        personality_stats = {label: 0 for label in PERSONALITY_CHOICES.values()}

        for review in reviews:
            for key, label in PERSONALITY_CHOICES.items():
                if getattr(review, key):
                    personality_stats[label] += 1

        sorted_stats = sorted(personality_stats.items(), key=lambda x: x[1], reverse=True)

        return Response(
            {
                "user_id": user.id,
                "real_name": user.username,
                "personalities": [
                    {"label": label, "count": count} for label, count in sorted_stats
                ],
            },
            status=status.HTTP_200_OK,
        )