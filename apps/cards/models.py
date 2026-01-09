from django.db import models
from apps.decks.models import Deck


def card_image_path(instance, filename):
    """カード画像の保存パスを生成"""
    return f"cards/{instance.deck.user.id}/{instance.deck.id}/{filename}"


class Card(models.Model):
    """カードモデル"""

    deck = models.ForeignKey(
        Deck,
        on_delete=models.CASCADE,
        related_name="cards",
        verbose_name="デッキ"
    )
    front = models.TextField(
        verbose_name="表面（質問）"
    )
    back = models.TextField(
        verbose_name="裏面（答え）"
    )
    front_image = models.ImageField(
        upload_to=card_image_path,
        blank=True,
        null=True,
        verbose_name="表面画像"
    )
    back_image = models.ImageField(
        upload_to=card_image_path,
        blank=True,
        null=True,
        verbose_name="裏面画像"
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
        verbose_name = "カード"
        verbose_name_plural = "カード"
        ordering = ["-created_at"]

    def __str__(self):
        # 表面の最初の30文字を表示
        return self.front[:30] + "..." if len(self.front) > 30 else self.front

    @property
    def is_new(self):
        """新規カード（未学習）かどうか"""
        return not hasattr(self, "card_state") or self.card_state is None

    @property
    def is_due(self):
        """復習が必要かどうか"""
        if self.is_new:
            return False
        from django.utils import timezone
        return self.card_state.next_review <= timezone.now()
