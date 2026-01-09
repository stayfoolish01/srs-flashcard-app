from django.contrib import admin
from .models import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    """カード管理"""

    list_display = ("front_preview", "deck", "created_at", "updated_at")
    list_filter = ("deck", "created_at")
    search_fields = ("front", "back", "deck__name")
    readonly_fields = ("created_at", "updated_at")

    def front_preview(self, obj):
        return obj.front[:50] + "..." if len(obj.front) > 50 else obj.front
    front_preview.short_description = "表面"
