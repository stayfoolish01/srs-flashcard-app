from django.db import models
from django.contrib.auth.models import User


class Deck(models.Model):
    """デッキモデル"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="decks",
        verbose_name="ユーザー"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="デッキ名"
    )
    description = models.TextField(
        blank=True,
        verbose_name="説明"
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
        verbose_name = "デッキ"
        verbose_name_plural = "デッキ"
        ordering = ["-updated_at"]
        # 同一ユーザー内でデッキ名は一意
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_deck_name_per_user"
            )
        ]

    def __str__(self):
        return self.name

    @property
    def card_count(self):
        """デッキ内のカード数を返す"""
        if hasattr(self, "cards"):
            return self.cards.count()
        return 0

    @property
    def new_card_count(self):
        """新規カード数を返す（デッキ所有者のCardStateがないカード）"""
        if not hasattr(self, "cards"):
            return 0
        # CardStateモデルが存在するかチェック
        try:
            from apps.study.models import CardState
            # デッキ所有者のCardStateがないカードをカウント
            cards_with_state = CardState.objects.filter(
                card__deck=self,
                user=self.user
            ).values_list("card_id", flat=True)
            return self.cards.exclude(pk__in=cards_with_state).count()
        except (ImportError, LookupError):
            # Phase 4実装前は全カードが新規
            return self.cards.count()

    @property
    def due_card_count(self):
        """復習が必要なカード数を返す（デッキ所有者の視点）"""
        if not hasattr(self, "cards"):
            return 0
        # CardStateモデルが存在するかチェック
        try:
            from apps.study.models import CardState
            from django.utils import timezone
            return self.cards.filter(
                card_states__user=self.user,
                card_states__next_review__lte=timezone.now()
            ).count()
        except (ImportError, LookupError):
            # Phase 4実装前は復習待ちなし
            return 0
