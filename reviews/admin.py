from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'reviewed_user', 'created_at', 'get_selected_count']
    list_filter = ['created_at']
    search_fields = ['reviewer__username', 'reviewed_user__username']
    readonly_fields = ['created_at']

    def get_selected_count(self, obj):
        return len(obj.get_selected_personalities())
    get_selected_count.short_description = '선택된 성격 수'