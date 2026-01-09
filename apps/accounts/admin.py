from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """ユーザープロフィール管理"""

    list_display = ("user", "timezone", "daily_new_cards", "created_at")
    list_filter = ("timezone", "created_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")