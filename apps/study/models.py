from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.cards.models import Card


class CardState(models.Model):
    """カードのFSRS学習状態を保存（ユーザーごと）"""

    class State(models.IntegerChoices):
        """カードの状態"""
        NEW = 0, "新規"
        LEARNING = 1, "学習中"
        REVIEW = 2, "復習"
        RELEARNING = 3, "再学習"

    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name="card_states",
        verbose_name="カード"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="card_states",
        verbose_name="ユーザー"
    )
    # FSRSパラメータ
    stability = models.FloatField(
        default=0.0,
        verbose_name="安定性"
    )
    difficulty = models.FloatField(
        default=0.0,
        verbose_name="難易度"
    )
    # 復習スケジュール
    due = models.DateTimeField(
        default=timezone.now,
        verbose_name="期限"
    )
    next_review = models.DateTimeField(
        default=timezone.now,
        verbose_name="次回復習日時"
    )
    last_review = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="最終復習日時"
    )
    # 状態管理
    state = models.IntegerField(
        choices=State.choices,
        default=State.NEW,
        verbose_name="状態"
    )
    reps = models.PositiveIntegerField(
        default=0,
        verbose_name="復習回数"
    )
    lapses = models.PositiveIntegerField(
        default=0,
        verbose_name="忘却回数"
    )
    # タイムスタンプ
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="作成日時"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新日時"
    )

    class Meta:
        verbose_name = "カード状態"
        verbose_name_plural = "カード状態"
        constraints = [
            models.UniqueConstraint(
                fields=["card", "user"],
                name="unique_card_user_state"
            )
        ]

    def __str__(self):
        return f"{self.card} - {self.user.username} - {self.get_state_display()}"

    @property
    def is_due(self):
        """復習が必要かどうか"""
        return self.next_review <= timezone.now()


class ReviewLog(models.Model):
    """復習履歴を記録"""

    class Rating(models.IntegerChoices):
        """評価（FSRSの4段階評価）"""
        AGAIN = 1, "もう一度"
        HARD = 2, "難しい"
        GOOD = 3, "良い"
        EASY = 4, "簡単"

    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name="review_logs",
        verbose_name="カード"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="review_logs",
        verbose_name="ユーザー"
    )
    rating = models.IntegerField(
        choices=Rating.choices,
        verbose_name="評価"
    )
    # 復習時のFSRS状態（履歴保存用）
    state = models.IntegerField(
        choices=CardState.State.choices,
        verbose_name="復習時の状態"
    )
    stability = models.FloatField(
        verbose_name="復習時の安定性"
    )
    difficulty = models.FloatField(
        verbose_name="復習時の難易度"
    )
    # 復習間隔
    elapsed_days = models.FloatField(
        default=0,
        verbose_name="経過日数"
    )
    scheduled_days = models.FloatField(
        default=0,
        verbose_name="予定間隔（日）"
    )
    # 復習時間
    review_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="復習日時"
    )
    # 回答時間（ミリ秒）
    duration = models.PositiveIntegerField(
        default=0,
        verbose_name="回答時間(ms)"
    )

    class Meta:
        verbose_name = "復習履歴"
        verbose_name_plural = "復習履歴"
        ordering = ["-review_time"]

    def __str__(self):
        return f"{self.card} - {self.get_rating_display()} ({self.review_time})"
