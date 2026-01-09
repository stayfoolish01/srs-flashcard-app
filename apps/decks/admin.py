from django.contrib import admin
from .models import Deck


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    """デッキ管理"""

    list_display = ("name", "user", "card_count", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name", "description", "user__username")
    readonly_fields = ("created_at", "updated_at")

    def card_count(self, obj):
        return obj.card_count
    card_count.short_description = "カード数"
