from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "reviewer", "reviewer_id_col",
                    "reviewed_user", "reviewed_user_id_col", "created_at")
    list_filter = ("created_at",)
    search_fields = ("reviewer__username", "reviewed_user__username",
                     "reviewer__id", "reviewed_user__id")
    autocomplete_fields = ("reviewer", "reviewed_user")

    # 성격 필드들을 읽기 쉽게 표시
    fieldsets = (
        (None, {
            'fields': ('reviewer', 'reviewed_user')
        }),
        ('선택된 성격', {
            'fields': (
                'personality_1', 'personality_2', 'personality_3',
                'personality_4', 'personality_5', 'personality_6',
                'personality_7', 'personality_8', 'personality_9',
                'personality_10', 'personality_11', 'personality_12',
            ),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description="작성자 ID")
    def reviewer_id_col(self, obj):
        return getattr(obj.reviewer, "id", None)

    @admin.display(description="대상자 ID")
    def reviewed_user_id_col(self, obj):
        return getattr(obj.reviewed_user, "id", None)