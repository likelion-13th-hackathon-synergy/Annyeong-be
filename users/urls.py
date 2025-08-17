from django.urls import path
from . import views
from .views import SignupView, LoginView, LogoutView, ProfileView
from .views import (
    SignupView, LoginView, LogoutView, ProfileView,
    google_login, google_callback, remove_google_auth, profile_preview_api,
)

app_name = 'users'

urlpatterns = [
    #인증
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    #프로필
    path("profile/", ProfileView.as_view(), name="profile"),
    path('profile/preview/', profile_preview_api, name="profile_preview"),

    #구글 OAuth
    path('auth/google/', google_login, name='google_login'),
    path('auth/google/callback/', google_callback, name='google_callback'),
    path('auth/google/remove/', remove_google_auth, name='remove_google_auth'),

]