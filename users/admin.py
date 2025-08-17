from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import User


class CustomUserAdmin(UserAdmin):
    # 목록 페이지에서 보여줄 필드들
    list_display = ('username', 'real_name', 'user_type', 'age', 'nationality',
    'translation_category', 'google_auth_status', 'date_joined')
    list_filter = ('user_type', 'google_verified', 'nationality', 'service_language',
        'translation_category', 'date_joined')
    search_fields = ('username', 'real_name', 'nationality', 'google_id')

    def google_auth_status(self, obj):
        if obj.google_verified:
            return format_html(
                '<span style="color: green;">✅ 인증완료</span><br><small>{}</small>',
                obj.google_id[:20] + '...' if obj.google_id and len(obj.google_id) > 20 else obj.google_id or ''
            )
        else:
            return format_html('<span style="color: red;">❌ 미인증</span>')

    google_auth_status.short_description = '구글 인증'

    # 상세 페이지 필드 그룹화
    fieldsets = UserAdmin.fieldsets + (
        ('개인 정보', {
            'fields': ('real_name', 'user_type', 'age', 'nationality', 'profile_image')
        }),
        ('프로필 정보', {
            'fields': ('introduction', 'city')
        }),
        ('인증 및 설정', {
            'fields': ('google_verified', 'google_id', 'service_language', 'translation_category')
        }),
    )

    # 새 사용자 생성 시 필수 필드
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('추가 정보', {
            'fields': ('real_name', 'user_type')
        }),
    )

    # 읽기 전용 필드
    readonly_fields = ('date_joined', 'last_login', 'created_at', 'updated_at')


# User 모델 등록
admin.site.register(User, CustomUserAdmin)

# 관리자 사이트 제목 변경
admin.site.site_header = "안녕 관리자"
admin.site.site_title = "안녕 Admin"
admin.site.index_title = "안녕 서비스 관리"
