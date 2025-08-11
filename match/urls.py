from django.urls import path
from .views import UserMatchPreferenceAPIView, RandomMatchUserAPIView, like_user, dislike_user

urlpatterns = [
    path('preference/', UserMatchPreferenceAPIView.as_view(), name='user-match-preference'),
    path('random-user/', RandomMatchUserAPIView.as_view(), name='random-match-user'),
    path('like/<int:user_id>/', like_user, name='like-user'),
    path('dislike/<int:user_id>/', dislike_user, name='dislike-user'),
]