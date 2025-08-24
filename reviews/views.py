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

PERSONALITY_LABEL_TO_KEY = {v: k for k, v in PERSONALITY_CHOICES.items()}

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

        #이미 이 채팅에서 후기 작성했는지 확인(중복체크)
        if Review.objects.filter(reviewer=request.user, reviewed_user=other_user).exists():
            return Response(
                {"detail": "이미 후기를 작성했습니다.", "already_reviewed": True},
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

        selected_keys = []
        for personality_label in selected_personalities:
            key = PERSONALITY_LABEL_TO_KEY.get(personality_label)
            if not key:
                return Response(
                    {"detail": f"유효하지 않은 성격: {personality_label}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            selected_keys.append(key)

        #Review 객체 생성
        review_data = {
            'reviewer': request.user,
            'reviewed_user': other_user,
        }

        for key in PERSONALITY_CHOICES.keys():
            review_data[key] = (key in selected_keys)

        review = Review.objects.create(**review_data)

        return Response(
            {
                "message": "후기가 작성되었습니다.",
                "review_id": review.id,
                "reviewed_user_id": other_user.id,
                "reviewed_user_name": other_user.username
            },
            status=status.HTTP_201_CREATED,
        )

class UserReviewListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        #해당 사용자가 받은 모든 리뷰
        reviews = Review.objects.filter(reviewed_user=user)

        #총리뷰 참여 횟수(실제 리뷰 개수)
        total_review_count = reviews.count()

        #총 성격 선택 횟수 계산
        total_personality_selections = 0

        #각 성격별 카운트 및 정렬
        personality_counts = []
        for key, label in PERSONALITY_CHOICES.items():
            count = reviews.filter(**{key: True}).count()
            total_personality_selections += count
            if count > 0:
                personality_counts.append((key, label, count))

        #카운트 순으로 정렬
        personality_counts.sort(key=lambda x: x[2], reverse=True)


        reviews_data = []
        for key, label, count in personality_counts:
            reviews_data.append({
                f"personalities_{key.split('_')[1]}": label,
                "count": count
            })

        return Response(
            {
                "user_id": user.id,
                "username": user.username,
                "total_reviews": total_review_count, #실제 참여 횟수
                "total_personality_selections": total_personality_selections, #총 성격 횟수
                "reviews": reviews_data,
            },
            status=status.HTTP_200_OK,
        )

class CanWriteReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, chat_room_id):
        chatroom = get_object_or_404(ChatRoom, id=chat_room_id)

        if not chatroom.is_active:
            return Response(
                {
                    "can_write": False,
                    "reason": "아직 수락되지 않은 대화입니다."
                }
            )

        if request.user not in [chatroom.requester, chatroom.receiver]:
            return Response({
                "can_write": False,
                "reason": "이 채팅의 참가자가 아닙니다.",
            })

        other_user = chatroom.get_other_participant(request.user)
        already_reviewed = Review.objects.filter(
            reviewer=request.user,
            reviewed_user=other_user,
        ).exists()

        return Response({
            "can_write": not already_reviewed,
            "already_reviewed": already_reviewed,
            "other_user_id": other_user.id,
            "other_user_name": other_user.username,
        })