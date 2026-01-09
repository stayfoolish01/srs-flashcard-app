"""
学習モデルのテスト
"""

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from apps.decks.models import Deck
from apps.cards.models import Card
from apps.study.models import CardState, ReviewLog


@pytest.mark.django_db
class TestCardState:
    """CardStateモデルのテストクラス"""

    def test_create_card_state(self):
        """CardStateが正常に作成できることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")
        card_state = CardState.objects.create(card=card, user=user)

        assert card_state.card == card
        assert card_state.user == user
        assert card_state.state == CardState.State.NEW
        assert card_state.stability == 0.0
        assert card_state.difficulty == 0.0
        assert card_state.reps == 0
        assert card_state.lapses == 0

    def test_card_state_str(self):
        """__str__メソッドが正しく動作することをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")
        card_state = CardState.objects.create(card=card, user=user)

        assert "質問" in str(card_state)
        assert "testuser" in str(card_state)
        assert "新規" in str(card_state)

    def test_card_state_is_due(self):
        """is_dueプロパティが正しく動作することをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")

        # 過去の日時を設定
        card_state = CardState.objects.create(
            card=card,
            user=user,
            next_review=timezone.now() - timezone.timedelta(hours=1)
        )
        assert card_state.is_due is True

        # 未来の日時を設定
        card_state.next_review = timezone.now() + timezone.timedelta(hours=1)
        card_state.save()
        assert card_state.is_due is False

    def test_card_state_cascade_delete(self):
        """カード削除時にCardStateも削除されることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")
        CardState.objects.create(card=card, user=user)

        card_id = card.id
        card.delete()

        assert not CardState.objects.filter(card_id=card_id).exists()


@pytest.mark.django_db
class TestReviewLog:
    """ReviewLogモデルのテストクラス"""

    def test_create_review_log(self):
        """ReviewLogが正常に作成できることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")

        review_log = ReviewLog.objects.create(
            card=card,
            user=user,
            rating=ReviewLog.Rating.GOOD,
            state=CardState.State.NEW,
            stability=0.0,
            difficulty=0.0,
            elapsed_days=0,
            scheduled_days=1,
            duration=5000,
        )

        assert review_log.card == card
        assert review_log.user == user
        assert review_log.rating == ReviewLog.Rating.GOOD
        assert review_log.duration == 5000

    def test_review_log_str(self):
        """__str__メソッドが正しく動作することをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")

        review_log = ReviewLog.objects.create(
            card=card,
            user=user,
            rating=ReviewLog.Rating.EASY,
            state=CardState.State.NEW,
            stability=0.0,
            difficulty=0.0,
        )

        assert "質問" in str(review_log)
        assert "簡単" in str(review_log)

    def test_review_log_ordering(self):
        """復習履歴が新しい順にソートされることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")

        log1 = ReviewLog.objects.create(
            card=card,
            user=user,
            rating=ReviewLog.Rating.AGAIN,
            state=CardState.State.NEW,
            stability=0.0,
            difficulty=0.0,
        )
        log2 = ReviewLog.objects.create(
            card=card,
            user=user,
            rating=ReviewLog.Rating.GOOD,
            state=CardState.State.LEARNING,
            stability=1.0,
            difficulty=5.0,
        )

        logs = list(card.review_logs.all())
        assert logs[0] == log2  # 新しい方が先
        assert logs[1] == log1
