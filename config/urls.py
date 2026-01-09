"""
URL configuration for SRS Flashcard App.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


def home_redirect(request):
    """ホームページへのリダイレクト"""
    if request.user.is_authenticated:
        return redirect("decks:deck_list")
    return redirect("accounts:login")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_redirect, name="home"),
    path("accounts/", include("apps.accounts.urls")),
    path("decks/", include("apps.decks.urls")),
    path("cards/", include("apps.cards.urls")),
    path("study/", include("apps.study.urls")),
]

# 開発環境でのメディアファイル配信
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])