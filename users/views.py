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

from .forms import SignUpForm, LoginForm, ProfileForm
from .models import User

def signup(request):
    if request.user.is_authenticated:
        return redirect('users:profile')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if (form.is_valid()):
            user = form.save()
            from django.contrib.auth import login, authenticate

            #유저 다시 인증 -> backend 정보 불러오기
            auth_user = authenticate(username=form.cleaned_data['username'],
                                     password=form.cleaned_data['password1'])
            login(request, auth_user)
            messages.success(request, f'{user.real_name}님, 환영합니다! 프로필을 완성해보세요.')
            return redirect('users:profile_edit')
        else:
            print("Form errors:", form.errors)
    else:
        form = SignUpForm()

    return render(request, 'users/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('users:profile')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        print("=== LOGIN DEBUG ===")
        print("Form valid?", form.is_valid())
        print("Form errors:", form.errors)
        print("Form data:", request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            print(f"Attempting login with username: '{username}'")
            print(f"Password: '{password}' (length: {len(password)})")

            # 사용자 존재 여부 확인
            from django.contrib.auth import get_user_model
            User = get_user_model()

            try:
                db_user = User.objects.get(username=username)
                print(f"User found in DB: {db_user}")
                print(f"User is active: {db_user.is_active}")
                print(f"Password check result: {db_user.check_password(password)}")
                print(f"Stored password hash: {db_user.password[:50]}...")
            except User.DoesNotExist:
                print(f"User '{username}' does not exist in database")
                messages.error(request, '존재하지 않는 사용자입니다.')
                return render(request, 'users/login.html', {'form': form})

            # Django authenticate 시도
            user = authenticate(request, username=username, password=password)
            print(f"Django authenticate result: {user}")

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'{user.real_name}님, 환영합니다!')
                    next_url = request.GET.get('next', 'users:profile')
                    print(f"Login successful, redirecting to: {next_url}")
                    return redirect(next_url)
                else:
                    messages.error(request, '비활성화된 계정입니다.')
            else:
                messages.error(request, '아이디 또는 비밀번호가 잘못되었습니다.')
        else:
                messages.error(request, '입력 정보를 다시 확인해주세요.')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, '로그아웃되었습니다.')
    return redirect('users:login')

@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})

@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)

            purpose = form.cleaned_data.get('purpose')
            if purpose is not None:
                user.purpose = list(purpose)

            user.save()
            messages.success(request, '프로필이 수정되었습니다.')
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'users/profile_edit.html', {'form': form})

#구글 관련 뷰들
def google_login(request):
    google_oauth_url = 'https://accounts.google.com/o/oauth2/v2/auth'

    print("=== Google Login View Called ===")
    print("Request path:", request.path)
    print("User authenticated?", request.user.is_authenticated)
    print("Request GET params:", request.GET)

    request.session['pending_user_id'] = request.user.id
    print("Pending user ID in session:", request.session['pending_user_id'])

    params = {
        'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
        'redirect_uri': request.build_absolute_uri(reverse('users:google_callback')),
        'scope': 'openid email profile',
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'select_account',
    }

    url = f"{google_oauth_url}?{urlencode(params)}"
    print("Redirecting to:", url)
    return redirect(url)


@login_required
def google_callback(request):
    print("=== Google callback reached ===")
    print("Full path:", request.get_full_path())
    print("GET params:", request.GET)
    print("Session keys:", list(request.session.keys()))

    code = request.GET.get('code')

    if not code:
        messages.error(request, '구글 인증에 실패했습니다.')
        return redirect('users:login')

    pending_user_id = request.session.get('pending_user_id')
    if not pending_user_id:
        messages.error(request, '세션이 만료되었습니다. 다시 시도해주세요.')
        return redirect('users:login')

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=pending_user_id)

        # Access token 받기
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
            'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': request.build_absolute_uri(reverse('users:google_callback')),
        }

        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()

        if 'access_token' not in token_json:
            messages.error(request, '구글 인증에 실패했습니다.')
            return redirect('users:profile_edit')

        # 사용자 정보 가져오기
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f"Bearer {token_json['access_token']}"}
        user_response = requests.get(user_info_url, headers=headers)
        user_data = user_response.json()

        # 사용자 정보 업데이트
        user.google_verified = True
        user.google_id = user_data.get('id')
        user.save()

        if 'pending_user_id' in request.session:
            del request.session['pending_user_id']

        messages.success(request, '구글 인증이 완료되었습니다!')

    except Exception as e:
        messages.error(request, f'구글 인증 중 오류가 발생했습니다: {str(e)}')

        if 'pending_user_id' in request.session:
            del request.session['pending_user_id']

    return redirect('users:profile_edit')


@login_required
def remove_google_auth(request):
    if request.method == 'POST':
        user = request.user
        user.google_verified = False
        user.google_id = None
        user.save()
        messages.info(request, '구글 인증이 제거되었습니다.')

    return redirect('users:profile_edit')

from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({"detail": "로그인 성공"})
    return Response({"detail": "아이디 또는 비밀번호 오류"}, status=400)