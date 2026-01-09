from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """ユーザープロフィール（Django Userモデルの拡張）"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="ユーザー"
    )
    timezone = models.CharField(
        max_length=50,
        default="Asia/Tokyo",
        verbose_name="タイムゾーン"
    )
    daily_new_cards = models.PositiveIntegerField(
        default=20,
        verbose_name="1日の新規カード上限"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="作成日時"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新日時"
    )

    class Meta:
        verbose_name = "ユーザープロフィール"
        verbose_name_plural = "ユーザープロフィール"

    def __str__(self):
        return f"{self.user.username}のプロフィール"