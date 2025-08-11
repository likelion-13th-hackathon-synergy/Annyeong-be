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
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'{user.real_name}님, 환영합니다! 프로필을 완성해보세요.')
            return redirect('users:profile_edit')
    else:
        form = SignUpForm()

    return render(request, 'users/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('users:profile')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'{user.real_name}님, 환영합니다!')
                next_url = request.GET.get('next', 'users:profile')
                return redirect(next_url)
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

            purposes = form.cleaned_data.get('purposes')
            if purposes is not None:
                user.purposes = list(purposes)

            user.save()
            messages.success(request, '프로필이 수정되었습니다.')
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'users/profile_edit.html', {'form': form})

#구글 관련 뷰들
def google_login(request):
    google_oauth_url = 'https://accounts.google.com/oauth2/authorize'

    request.session['pending_user_id'] = request.user.id

    params = {
        'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
        'redirect_uri': request.build_absolute_uri(reverse('users:google_callback')),
        'scope': 'openid email profile',
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'select_account',
    }

    url = f"{google_oauth_url}?{urlencode(params)}"
    return redirect(url)


@login_required
def google_callback(request):
    code = request.GET.get('code')

    if not code:
        messages.error(request, '구글 인증에 실패했습니다.')
        return redirect('users:login')

    pending_user_id = request.session('pending_user_id')
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