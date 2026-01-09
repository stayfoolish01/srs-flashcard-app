"""
Deckモデルのテスト
"""

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError

from apps.decks.models import Deck


@pytest.mark.django_db
class TestDeck:
    """Deckモデルのテストクラス"""

    def test_create_deck(self):
        """Deckが正常に作成できることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(
            user=user,
            name="テストデッキ",
            description="テスト用のデッキです"
        )

        assert deck.user == user
        assert deck.name == "テストデッキ"
        assert deck.description == "テスト用のデッキです"

    def test_deck_str(self):
        """__str__メソッドが正しく動作することをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="英単語")

        assert str(deck) == "英単語"

    def test_deck_unique_name_per_user(self):
        """同一ユーザー内でデッキ名が重複できないことをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        Deck.objects.create(user=user, name="英単語")

        with pytest.raises(IntegrityError):
            Deck.objects.create(user=user, name="英単語")

    def test_deck_same_name_different_users(self):
        """異なるユーザーは同じデッキ名を使えることをテスト"""
        user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass123"
        )
        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpass123"
        )

        deck1 = Deck.objects.create(user=user1, name="英単語")
        deck2 = Deck.objects.create(user=user2, name="英単語")

        assert deck1.name == deck2.name
        assert deck1.user != deck2.user

    def test_deck_card_count_empty(self):
        """カードがない場合のcard_countが0であることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")

        assert deck.card_count == 0

    def test_deck_ordering(self):
        """デッキが更新日時の降順でソートされることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck1 = Deck.objects.create(user=user, name="デッキ1")
        deck2 = Deck.objects.create(user=user, name="デッキ2")
        deck3 = Deck.objects.create(user=user, name="デッキ3")

        # deck1を更新
        deck1.description = "更新しました"
        deck1.save()

        decks = list(Deck.objects.filter(user=user))
        assert decks[0] == deck1  # 最後に更新されたdeck1が最初

    def test_deck_cascade_delete(self):
        """ユーザー削除時にデッキも削除されることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        Deck.objects.create(user=user, name="テストデッキ")

        user_id = user.id
        user.delete()

        assert not Deck.objects.filter(user_id=user_id).exists()
