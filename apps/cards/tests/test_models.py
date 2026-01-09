"""
Cardモデルのテスト
"""

import pytest
from django.contrib.auth.models import User

from apps.decks.models import Deck
from apps.cards.models import Card


@pytest.mark.django_db
class TestCard:
    """Cardモデルのテストクラス"""

    def test_create_card(self):
        """Cardが正常に作成できることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(
            deck=deck,
            front="質問",
            back="答え"
        )

        assert card.deck == deck
        assert card.front == "質問"
        assert card.back == "答え"

    def test_card_str_short(self):
        """短いテキストの__str__が正しく動作することをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="短い質問", back="答え")

        assert str(card) == "短い質問"

    def test_card_str_long(self):
        """長いテキストの__str__が切り詰められることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        long_text = "あ" * 50
        card = Card.objects.create(deck=deck, front=long_text, back="答え")

        assert str(card) == long_text[:30] + "..."

    def test_card_is_new(self):
        """新規カード判定が正しく動作することをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")

        assert card.is_new is True

    def test_card_cascade_delete(self):
        """デッキ削除時にカードも削除されることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        Card.objects.create(deck=deck, front="質問", back="答え")

        deck_id = deck.id
        deck.delete()

        assert not Card.objects.filter(deck_id=deck_id).exists()

    def test_deck_card_count(self):
        """デッキのcard_countがカード作成後正しくカウントされることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")

        assert deck.card_count == 0

        Card.objects.create(deck=deck, front="質問1", back="答え1")
        assert deck.card_count == 1

        Card.objects.create(deck=deck, front="質問2", back="答え2")
        assert deck.card_count == 2

    def test_card_ordering(self):
        """カードが作成日時の降順でソートされることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card1 = Card.objects.create(deck=deck, front="質問1", back="答え1")
        card2 = Card.objects.create(deck=deck, front="質問2", back="答え2")
        card3 = Card.objects.create(deck=deck, front="質問3", back="答え3")

        cards = list(deck.cards.all())
        assert cards[0] == card3  # 最後に作成されたカードが最初
        assert cards[1] == card2
        assert cards[2] == card1
