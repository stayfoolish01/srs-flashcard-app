"""
デッキフォームのテスト
"""

import pytest
from django.contrib.auth.models import User

from apps.decks.forms import DeckForm
from apps.decks.models import Deck


@pytest.mark.django_db
class TestDeckForm:
    """DeckFormのテストクラス"""

    def test_valid_deck_form(self):
        """有効なデータでフォームが検証されることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        form = DeckForm(
            data={
                "name": "新しいデッキ",
                "description": "テスト用のデッキです",
            },
            user=user,
        )
        assert form.is_valid()

    def test_deck_form_name_required(self):
        """デッキ名が必須であることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        form = DeckForm(
            data={
                "name": "",
                "description": "",
            },
            user=user,
        )
        assert not form.is_valid()
        assert "name" in form.errors

    def test_deck_form_description_optional(self):
        """説明が任意であることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        form = DeckForm(
            data={
                "name": "デッキ名のみ",
                "description": "",
            },
            user=user,
        )
        assert form.is_valid()

    def test_deck_form_duplicate_name(self):
        """同一ユーザー内で重複デッキ名がエラーになることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        Deck.objects.create(user=user, name="既存デッキ")

        form = DeckForm(
            data={
                "name": "既存デッキ",
                "description": "",
            },
            user=user,
        )
        assert not form.is_valid()
        assert "name" in form.errors

    def test_deck_form_edit_same_name_allowed(self):
        """編集時に自分自身の名前は許可されることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="既存デッキ")

        form = DeckForm(
            data={
                "name": "既存デッキ",
                "description": "説明を追加",
            },
            user=user,
            instance=deck,
        )
        assert form.is_valid()

    def test_deck_form_different_user_same_name(self):
        """異なるユーザーは同じ名前を使えることをテスト"""
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
        Deck.objects.create(user=user1, name="共通名")

        form = DeckForm(
            data={
                "name": "共通名",
                "description": "",
            },
            user=user2,
        )
        assert form.is_valid()
