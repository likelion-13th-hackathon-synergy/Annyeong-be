from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count, Q
from .models import Review
import json

@login_required
def review_list(request, user_id):
    reviewed_user = get_object_or_404(User, id=user_id) #특정 사용자의 후기 목록 조회(더보기 버튼)

    #해당 사용자에 대한 모든 후기 조회
    reviews = Review.objects.filter(user=reviewed_user)

    #각 성격별 선택 횟수 현황
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

    #총 후기 개수
    total_reviews = reviews.count()

    #선택 횟수 많은 순서로 정렬
    sorted_personalities = sorted(personality_stats.items(), key=lambda x: x[1], reverse=True)

    #선택된 성격들만 필터링(0개 초과)
    filtered_personalities = [(personality, count) for personality, count in sorted_personalities if count > 0]

    context = {
        'reviewed_user': reviewed_user,
        'personality_stats': filtered_personalities,
        'total_reviews': total_reviews,
        'total_participants': total_reviews #총 참여자 수 = 총 후기 수
    }

    return render(request, 'reviews/review_list.html', context)

#후기 작성 페이지 -> 채팅 기능과 연동 필요
@login_required
def create_review(request, chat_room_id):
    other_user = get_object_or_404(User, id=request.user.id) #임시로 상대 사용자 설정(실제는 채팅방에서 가져와야 함)

    if request.method == 'POST':
        return handle_review_submission(request, other_user)

    existing_review = None
    if other_user:
        existing_review = Review.objects.filter(reviewer=request.user, reviewed_user=other_user).first()

    personalities = [
        {'key': 'personality_1', 'label': '성격1'},
        {'key': 'personality_2', 'label': '성격2'},
        {'key': 'personality_3', 'label': '성격3'},
        {'key': 'personality_4', 'label': '성격4'},
        {'key': 'personality_5', 'label': '성격5'},
        {'key': 'personality_6', 'label': '성격6'},
        {'key': 'personality_7', 'label': '성격7'},
        {'key': 'personality_8', 'label': '성격8'},
        {'key': 'personality_9', 'label': '성격9'},
        {'key': 'personality_10', 'label': '성격10'},
    ]

    context = {
        'other_user': other_user,
        'personalities': personalities,
        'existing_review': existing_review,
        'chat_room_id': chat_room_id
    }
    return render(request, 'reviews/create_review.html', context)

def handle_review_submission(request, other_user):
    #후기 제출 처리
    if not other_user:
        messages.error(request, '후기를 작성할 수 없습니다.')
        return redirect('chat:room', room_id=request.POST.get('chat_room_id'))

    #선택된 성격들 가져오기
    selected_personalities = request.POST.getlist('personalities')

    #최대 5개 선택 기능
    if len(selected_personalities) > 5:
        messages.error(request, '최대 5개까지만 선택할 수 있습니다.')
        return redirect('reviews:create', chat_room_id=request.POST.get('chat_room_id'))

    if len(selected_personalities) == 0:
        messages.error(request, '최소 하나의 성격을 선택해주세요.')
        return redirect('reviews:create', chat_room_id=request.POST.get('chat_room_id'))

    #기존 후기 확인
    review, created = Review.objects.get_or_create(
        reviewer=request.user,
        reviewed_user=other_user,
    )

    #모든 성격을 false로 초기화
    for i in range(1, 11):
        setattr(review, f'personality_{i}', False)

    #선택된 성격들을 True로 설정
    for personality in selected_personalities:
        setattr(review, personality, True)

    review.save()

    if created:
        messages.success(request, '후기가 성공적으로 작성되었습니다.')
    else:
        messages.success(request, '후기가 성공적으로 수정되었습니다.')

    return redirect('chat:room', room_id=request.POST.get('chat_room_id'))
