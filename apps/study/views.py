"""
学習機能のビュー
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.decks.models import Deck
from apps.cards.models import Card
from .models import CardState, ReviewLog
from .services import FSRSService


def get_study_cards(deck, user, limit=None):
    """
    学習対象のカードを取得（ユーザーごと）

    優先順位:
    1. 復習期限が過ぎたカード（古い順）
    2. 新規カード（作成順）
    """
    now = timezone.now()

    # 復習期限が過ぎたカード（このユーザーのCardStateで判定）
    due_cards = list(
        Card.objects.filter(
            deck=deck,
            card_states__user=user,
            card_states__next_review__lte=now
        ).order_by("card_states__next_review")
    )

    # 新規カード（このユーザーのCardStateがないカード）
    cards_with_state = CardState.objects.filter(
        card__deck=deck,
        user=user
    ).values_list("card_id", flat=True)

    new_cards = list(
        Card.objects.filter(deck=deck)
        .exclude(pk__in=cards_with_state)
        .order_by("created_at")
    )

    # 結合（復習カード優先）
    cards = due_cards + new_cards

    if limit:
        cards = cards[:limit]

    return cards


@login_required
def study_session(request, deck_pk):
    """学習セッション開始"""
    deck = get_object_or_404(Deck, pk=deck_pk, user=request.user)

    # 学習対象カードを取得（ユーザーごと）
    cards = get_study_cards(deck, request.user)

    if not cards:
        # 学習するカードがない場合
        return render(request, "study/no_cards.html", {"deck": deck})

    # 最初のカードにリダイレクト
    return redirect("study:card", deck_pk=deck.pk, card_pk=cards[0].pk)


@login_required
def study_card(request, deck_pk, card_pk):
    """カード学習画面"""
    deck = get_object_or_404(Deck, pk=deck_pk, user=request.user)
    card = get_object_or_404(Card, pk=card_pk, deck=deck)

    # 学習対象カードを取得（進捗表示用・ユーザーごと）
    cards = get_study_cards(deck, request.user)

    # 現在のカードのインデックスを取得
    card_ids = [c.pk for c in cards]
    if card.pk in card_ids:
        current_index = card_ids.index(card.pk) + 1
    else:
        current_index = 1

    total_cards = len(cards)

    # FSRSサービスで次回復習間隔を取得（ユーザーごと）
    service = FSRSService()
    intervals = service.get_next_review_intervals(card, request.user)

    # セッション開始時刻を記録（回答時間計測用）
    if "study_start_time" not in request.session:
        request.session["study_start_time"] = timezone.now().isoformat()

    # カード表示開始時刻を記録
    request.session["card_start_time"] = timezone.now().isoformat()

    context = {
        "deck": deck,
        "card": card,
        "current_index": current_index,
        "total_cards": total_cards,
        "intervals": intervals,
        "show_answer": request.GET.get("show") == "answer",
    }

    return render(request, "study/study_card.html", context)


@login_required
@require_POST
def answer_card(request, deck_pk, card_pk):
    """カード回答処理"""
    deck = get_object_or_404(Deck, pk=deck_pk, user=request.user)
    card = get_object_or_404(Card, pk=card_pk, deck=deck)

    # 評価を取得
    rating_str = request.POST.get("rating")
    try:
        rating = int(rating_str)
        if rating not in [1, 2, 3, 4]:
            raise ValueError("Invalid rating")
    except (TypeError, ValueError):
        return redirect("study:card", deck_pk=deck.pk, card_pk=card.pk)

    # 回答時間を計算（ミリ秒）
    duration = 0
    card_start_time = request.session.get("card_start_time")
    if card_start_time:
        from datetime import datetime
        start = datetime.fromisoformat(card_start_time)
        now = timezone.now()
        if timezone.is_naive(start):
            start = timezone.make_aware(start)
        duration = int((now - start).total_seconds() * 1000)

    # FSRSで復習を記録（ユーザーごと）
    service = FSRSService()
    service.review_card(card, request.user, rating, duration=duration)

    # 次のカードを取得（ユーザーごと）
    cards = get_study_cards(deck, request.user)

    if not cards:
        # 全カード学習完了
        # セッション情報をクリア
        if "study_start_time" in request.session:
            del request.session["study_start_time"]
        if "card_start_time" in request.session:
            del request.session["card_start_time"]
        return redirect("study:complete", deck_pk=deck.pk)

    # 次のカードへ
    return redirect("study:card", deck_pk=deck.pk, card_pk=cards[0].pk)


@login_required
def study_complete(request, deck_pk):
    """学習完了画面"""
    deck = get_object_or_404(Deck, pk=deck_pk, user=request.user)

    # 今日の学習統計（ユーザーごと）
    today = timezone.now().date()
    today_reviews = ReviewLog.objects.filter(
        card__deck=deck,
        user=request.user,
        review_time__date=today
    )

    stats = {
        "total_reviews": today_reviews.count(),
        "again_count": today_reviews.filter(rating=ReviewLog.Rating.AGAIN).count(),
        "hard_count": today_reviews.filter(rating=ReviewLog.Rating.HARD).count(),
        "good_count": today_reviews.filter(rating=ReviewLog.Rating.GOOD).count(),
        "easy_count": today_reviews.filter(rating=ReviewLog.Rating.EASY).count(),
    }

    context = {
        "deck": deck,
        "stats": stats,
    }

    return render(request, "study/complete.html", context)
