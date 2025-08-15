from random import choices
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User

class SignUpForm(UserCreationForm):
    real_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '이름을 입력하세요'}),
                                label='실명')
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'}),
        label='사용자 구분'
    )

    class Meta:
        model = User
        fields = ('username', 'real_name', 'user_type', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '아이디를 입력하세요',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '비밀번호를 입력하세요',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '비밀번호를 다시 입력하세요',
        })

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '아이디',
        }),
        label='아이디'
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '비밀번호',
        }),
        label='비밀번호'
    )

NATIONALITY_CHOICES = [
    ('CN', 'China'),
    ('VN', 'Vietnam'),
    ('MM', 'Myanmar'),
    ('UZ', 'Uzbekistan'),
    ('MN', 'Mongolia'),
    ('NP', 'Nepal'),
    ('US', 'United States'),
    ('JP', 'Japan'),
    ('TH', 'Thailand'),
    ('KR', 'South Korea'),
]

CITY_CHOICES = [
    ('서울특별시', '서울특별시'),
    ('부산광역시', '부산광역시'),
    ('대구광역시', '대구광역시'),
    ('인천광역시', '인천광역시'),
    ('광주광역시', '광주광역시'),
    ('대전광역시', '대전광역시'),
    ('울산광역시', '울산광역시'),
    ('세종특별자치시', '세종특별자치시'),
    ('경기도', '경기도'),
    ('강원특별자치도', '강원특별자치도'),
    ('충청북도', '충청북도'),
    ('충청남도', '충청남도'),
    ('전북특별자치도', '전북특별자치도'),
    ('전라남도', '전라남도'),
    ('경상북도', '경상북도'),
    ('경상남도', '경상남도'),
    ('제주특별자치도', '제주특별자치도'),
]

class ProfileForm(forms.ModelForm):
    real_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '실명을 입력하세요',
        }),
        label='이름'
    )

    age = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '나이를 입력하세요',
        }),
        label='나이'
    )

    nationality = forms.ChoiceField(
        choices=[('', '국가 선택')] + NATIONALITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='국적'
    )

    city = forms.ChoiceField(
        choices=[('', '시/도')] + CITY_CHOICES,
        widget=forms.Select(attrs={'class': "form-control"}),
        required=False,
        label='시/도'
    )

    translation_category = forms.ChoiceField(
        choices=[('', '번역 언어 선택')] + User.LANGUAGE_CHOICES,
        widget=forms.Select(attrs={'class': "form-control"}),
        required=False,
        label='번역'
    )

    class Meta:
        model = User
        fields = [
            'real_name', 'age', 'profile_image', 'nationality',
            'introduction', 'city', 'service_language','translation_category']
        widgets = {
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'introduction': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '자신을 소개해보세요 (최대 500자)',
                'maxlength': 500
            }),
            'service_language': forms.Select(attrs={
                'class': 'form-control'
            })
        }
