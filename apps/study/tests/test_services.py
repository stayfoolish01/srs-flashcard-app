"""
FSRSサービスのテスト
"""

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from apps.decks.models import Deck
from apps.cards.models import Card
from apps.study.models import CardState, ReviewLog
from apps.study.services import FSRSService


@pytest.mark.django_db
class TestFSRSService:
    """FSRSServiceのテストクラス"""

    def test_get_or_create_card_state_new(self):
        """新規カードのCardState作成をテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")

        service = FSRSService()
        card_state = service.get_or_create_card_state(card, user)

        assert card_state.card == card
        assert card_state.user == user
        assert card_state.state == CardState.State.NEW

    def test_get_or_create_card_state_existing(self):
        """既存のCardStateを取得するテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")

        # 既存のCardStateを作成
        existing_state = CardState.objects.create(
            card=card,
            user=user,
            state=CardState.State.REVIEW,
            stability=5.0,
            difficulty=5.0,
        )

        service = FSRSService()
        card_state = service.get_or_create_card_state(card, user)

        assert card_state.pk == existing_state.pk
        assert card_state.state == CardState.State.REVIEW

    def test_review_card_again(self):
        """'もう一度'評価での復習をテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")

        service = FSRSService()
        card_state = service.review_card(card, user, ReviewLog.Rating.AGAIN)

        assert card_state.reps == 1
        assert card_state.last_review is not None

        # ReviewLogが作成されていることを確認
        assert ReviewLog.objects.filter(card=card, user=user).count() == 1
        log = ReviewLog.objects.get(card=card, user=user)
        assert log.rating == ReviewLog.Rating.AGAIN

    def test_review_card_good(self):
        """'良い'評価での復習をテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")

        service = FSRSService()
        card_state = service.review_card(card, user, ReviewLog.Rating.GOOD)

        assert card_state.reps == 1
        assert card_state.stability > 0  # 安定性が増加
        # ReviewLogが作成されていることを確認
        assert ReviewLog.objects.filter(card=card, user=user, rating=ReviewLog.Rating.GOOD).exists()

    def test_review_card_easy(self):
        """'簡単'評価での復習をテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")

        service = FSRSService()
        card_state = service.review_card(card, user, ReviewLog.Rating.EASY)

        assert card_state.reps == 1
        # Easyは最も長い間隔になる
        assert card_state.stability > 0

    def test_review_card_multiple_times(self):
        """複数回復習をテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")

        service = FSRSService()

        # 1回目: Good
        card_state = service.review_card(card, user, ReviewLog.Rating.GOOD)
        assert card_state.reps == 1

        # 2回目: Good
        card_state = service.review_card(card, user, ReviewLog.Rating.GOOD)
        assert card_state.reps == 2

        # 3回目: Easy
        card_state = service.review_card(card, user, ReviewLog.Rating.EASY)
        assert card_state.reps == 3

        # ReviewLogが3件作成されていることを確認
        assert ReviewLog.objects.filter(card=card, user=user).count() == 3

    def test_review_card_with_duration(self):
        """回答時間付きの復習をテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")

        service = FSRSService()
        service.review_card(card, user, ReviewLog.Rating.GOOD, duration=5000)

        log = ReviewLog.objects.get(card=card, user=user)
        assert log.duration == 5000

    def test_get_next_review_intervals(self):
        """次回復習間隔の取得をテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")

        service = FSRSService()
        intervals = service.get_next_review_intervals(card, user)

        # 4つの評価すべてに間隔が設定されている
        assert ReviewLog.Rating.AGAIN in intervals
        assert ReviewLog.Rating.HARD in intervals
        assert ReviewLog.Rating.GOOD in intervals
        assert ReviewLog.Rating.EASY in intervals

        # すべて文字列
        for interval in intervals.values():
            assert isinstance(interval, str)

    def test_format_interval(self):
        """間隔フォーマットをテスト"""
        service = FSRSService()

        assert service._format_interval(30) == "30秒"
        assert service._format_interval(120) == "2分"
        assert service._format_interval(7200) == "2時間"
        assert service._format_interval(86400) == "1日"
        assert service._format_interval(86400 * 7) == "7日"
        assert service._format_interval(86400 * 60) == "2ヶ月"
