from django.contrib.auth import get_user_model
from django.db.models import Q
from django.template.defaultfilters import first

from reviews.views import PERSONALITY_CHOICES

User = get_user_model()

PERSONALITY_CHOICES = {
    'personality_1': '이야기를 잘 들어줘요',
    'personality_2': '유머 감각이 뛰어나요',
    'personality_3': '대화가 재미있어요',
    'personality_4': '긍적적인 마인드예요',
    'personality_5': '친근하고 따뜻해요',
    'personality_6': '배려심이 깊어요',
    'personality_7': '지식이 풍부해요',
    'personality_8': '호기심이 많아요',
    'personality_9': '이해심이 많아요',
    'personality_10': '정직하고 솔직해요',
    'personality_11': '적극적이고 활발해요',
    'personality_12': '신뢰할 수 있어요',
}


def get_user_review_stats(user):
    from .models import Review

    reviews = Review.objects.filter(reviewed_user=user)

    #통계 반환 시 0으로 초기화
    personality_stats = {label: 0 for label in PERSONALITY_CHOICES.values()}


    #실제 카운트로 업데이트
    for key, label in PERSONALITY_CHOICES.items():
        personality_stats[label] = reviews.filter(**{key: True}).count()

    total_reviews = reviews.count()
    top_personalities = sorted(personality_stats.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        'total_reviews': total_reviews,
        'top_personalities': top_personalities,
        'personality_stats': personality_stats
    }


def can_write_review(reviewer, reviewed_user):
    #리뷰 작성 가능 여부 확인
    from chat.models import ChatRoom, Message

    chatroom = ChatRoom.objects.filter(
        Q(requester=reviewer, receiver=reviewed_user) |
        Q(requester=reviewed_user, receiver=reviewer),
        is_active=True
    ).first()

    if not chatroom:
        return False

    reviewer_sent = Message.objects.filter(chatroom=chatroom, sender=reviewer).exists()
    reviewed_user_sent = Message.objects.filter(chatroom=chatroom, sender=reviewed_user).exists()

    return reviewer_sent and reviewed_user_sent


def get_personality_name(personality_key):
    return PERSONALITY_CHOICES.get(personality_key, personality_key)