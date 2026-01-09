from django.contrib import admin
from .models import CardState, ReviewLog


@admin.register(CardState)
class CardStateAdmin(admin.ModelAdmin):
    """カード状態管理"""

    list_display = ("card", "state", "stability", "difficulty", "next_review", "reps", "lapses")
    list_filter = ("state", "created_at")
    search_fields = ("card__front", "card__deck__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ReviewLog)
class ReviewLogAdmin(admin.ModelAdmin):
    """復習履歴管理"""

    list_display = ("card", "rating", "state", "scheduled_days", "review_time")
    list_filter = ("rating", "state", "review_time")
    search_fields = ("card__front", "card__deck__name")
    readonly_fields = ("review_time",)
