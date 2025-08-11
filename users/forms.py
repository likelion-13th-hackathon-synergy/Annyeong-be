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

class ProfileForm(forms.ModelForm):
    purpose = forms.MultipleChoiceField(
        choices=User.PURPOSE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input',
        }),
        required=False,
        label='목적(복수 선택 가능)'
    )

    class Meta:
        model = User
        fields = [
            'age', 'profile_image', 'nationality', 'purpose',
        'introduction', 'city', 'district', 'service_language',]
        widgets = {
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 18,
                'max': 100
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'nationality': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': '예: 대한민국, 미국 등'
            }),
            'introduction': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '자신을 소개해보세요 (최대 500자)',
                'maxlength': 500
            }),
            'city': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': '예: 서울특별시, 부산광역시 등'
            }),
            'district': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': '예: 강남구, 해운대구 등'
            }),
            'service_language': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.purpose:
            self.initial['purpose'] = self.instance.purpose