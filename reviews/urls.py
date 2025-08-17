from django.urls import path
from .views import CreateReviewView, UserReviewListView

app_name = 'reviews'
urlpatterns = [
    #후기 작성 (채팅방 기준)
    path('create/<int:chat_room_id>/', CreateReviewView.as_view(), name='create'),

    #특정 유저의 후기 목록 보기
    path('user/<int:user_id>/', UserReviewListView.as_view(), name='list'),
]