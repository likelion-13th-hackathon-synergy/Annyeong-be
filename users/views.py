from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse
import requests
import json
from urllib.parse import urlencode
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.views.generic import CreateView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, login, logout, get_user_model
from .serializers import UserSerializer, SignupSerializer

User = get_user_model()

class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return Response({"detail": "로그인 성공"}, status=status.HTTP_200_OK)
        return Response({"detail": "아이디 또는 비밀번호가 올바르지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"detail": "로그아웃되었습니다."}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    """
    GET: 내 프로필 조회
    PUT: 프로필 수정
    """
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#구글 관련 뷰들
def google_login(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "로그인이 필요합니다."}, status=401)

    google_oauth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    request.session["pending_user_id"] = request.user.id

    params = {
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "redirect_uri": request.build_absolute_uri(reverse("users:google_callback")),
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "select_account",
    }

    url = f"{google_oauth_url}?{urlencode(params)}"
    return JsonResponse({"redirect_url": url}, status=200)


def google_callback(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"detail": "구글 인증에 실패했습니다."}, status=400)

    pending_user_id = request.session.get("pending_user_id")
    if not pending_user_id:
        return JsonResponse({"detail": "세션이 만료되었습니다."}, status=400)

    try:
        user = User.objects.get(id=pending_user_id)

        # Access token 요청
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": request.build_absolute_uri(reverse("users:google_callback")),
        }

        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()

        if "access_token" not in token_json:
            return JsonResponse({"detail": "구글 인증에 실패했습니다."}, status=400)

        # 사용자 정보 가져오기
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {token_json['access_token']}"}
        user_response = requests.get(user_info_url, headers=headers)
        user_data = user_response.json()

        # 사용자 정보 업데이트
        user.google_verified = True
        user.google_id = user_data.get("id")
        user.save()

        if "pending_user_id" in request.session:
            del request.session["pending_user_id"]

        return JsonResponse({"detail": "구글 인증이 완료되었습니다."}, status=200)

    except Exception as e:
        if "pending_user_id" in request.session:
            del request.session["pending_user_id"]
        return JsonResponse({"detail": f"구글 인증 중 오류 발생: {str(e)}"}, status=500)


def remove_google_auth(request):
    if request.method == "POST":
        user = request.user
        user.google_verified = False
        user.google_id = None
        user.save()
        return JsonResponse({"detail": "구글 인증이 제거되었습니다."}, status=200)
    return JsonResponse({"detail": "허용되지 않은 메서드입니다."}, status=405)


#미리보기 기능
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile_preview_api(request):
    user = request.user
    data = {
        "real_name": user.real_name,
        "age": user.age,
        "profile_image": request.build_absolute_uri(user.profile_image.url) if user.profile_image and hasattr(user.profile_image, 'url') else None,
        "nationality": user.nationality,
        "introduction": user.introduction,
        "city": user.city,
        "service_language": user.service_language,
        "google_verified": user.google_verified,
    }
    return Response(data, status=status.HTTP_200_OK)