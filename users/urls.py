from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    #인증
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    #프로필
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),

    #구글 OAuth
    path('auth/google/', views.google_login, name='google_login'),
    path('auth/google/callback/', views.google_callback, name='google_callback'),
    path('auth/google/remove/', views.remove_google_auth, name='remove_google_auth'),

    path('profile/preview/', views.profile_preview_api, name='profile_preview_api'),
]
