from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('korean', '내국인'),
        ('foreigner', '외국인'),
    ]

    LANGUAGE_CHOICES = [
        ('zh', 'Chinese'),
        ('en', 'English'),
        ('ja', 'Japanese'),
        ('ja', 'Japanese'),
        ('mn', 'Mongolian'),
        ('mm', 'Myanmar'),
        ('ne', 'Nepali'),
        ('ko', 'Korean'),
        ('th', 'Thai'),
        ('uz', 'Uzbek'),
        ('vi', 'Vietnamese'),
    ]

    #기본 정보
    real_name = models.CharField(max_length=50, verbose_name='실명')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, verbose_name='사용자 구분')

    #프로필 정보
    age = models.CharField(
        max_length=10,
        null=True, blank=True,
        verbose_name='나이'
    )
    profile_image = models.ImageField(
        upload_to='profile_image/',
        null=True, blank=True,
        verbose_name = '프로필 사진'
    )

    nationality = models.CharField(max_length=50, null=True, blank=True, verbose_name='국적')
    introduction = models.TextField(max_length=500, null=True, blank=True, verbose_name='소개글')

    #거주지역
    city = models.CharField(max_length=50, null=True, blank=True, verbose_name='시/도')

    #서비스 설정
    service_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='ko', verbose_name='언어')
    translation_category = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, null=True, blank=True, verbose_name='번역')

    #인증
    google_verified = models.BooleanField(default=False, verbose_name='구글 인증')
    google_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='구글 ID')

    #메타데이터
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.real_name}({self.username})"

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'
