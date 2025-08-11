from django.urls import path
from . import views

app_name = 'reviews'
urlpatterns = [
    #후기 목록 조회
    path('user/<int:user_id>/', views.review_list, name='list'),

    #후기 작성
    path('create/<int:chat_room_id>/', views.create_review, name='create'),

    #AJAX 후기 작성
    path('ajax/create/', views.ajax_create_review, name='ajax_create'),
]