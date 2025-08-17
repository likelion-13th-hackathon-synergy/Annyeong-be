from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


def get_user_review_stats(user):
    from .models import Review

    reviews = Review.objects.filter(reviewed_user=user)

    personality_stats = {
        '성격1': reviews.filter(personality_1=True).count(),
        '성격2': reviews.filter(personality_2=True).count(),
        '성격3': reviews.filter(personality_3=True).count(),
        '성격4': reviews.filter(personality_4=True).count(),
        '성격5': reviews.filter(personality_5=True).count(),
        '성격6': reviews.filter(personality_6=True).count(),
        '성격7': reviews.filter(personality_7=True).count(),
        '성격8': reviews.filter(personality_8=True).count(),
        '성격9': reviews.filter(personality_9=True).count(),
        '성격10': reviews.filter(personality_10=True).count(),
    }

    total_reviews = reviews.count()
    top_personalities = sorted(personality_stats.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        'total_reviews': total_reviews,
        'personality_stats': personality_stats,
        'top_personalities': top_personalities
    }


def can_write_review(reviewer, reviewed_user):

    #임시로 True 반환 (채팅 기능 구현 전까지)
    return True


def get_personality_name(personality_key):
    personality_names = {
        'personality_1': '성격1',
        'personality_2': '성격2',
        'personality_3': '성격3',
        'personality_4': '성격4',
        'personality_5': '성격5',
        'personality_6': '성격6',
        'personality_7': '성격7',
        'personality_8': '성격8',
        'personality_9': '성격9',
        'personality_10': '성격10',
    }
    return personality_names.get(personality_key, personality_key)