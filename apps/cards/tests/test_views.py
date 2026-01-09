"""
カードビューのテスト
"""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from apps.decks.models import Deck
from apps.cards.models import Card


@pytest.mark.django_db
class TestCardCreateView:
    """カード作成ビューのテスト"""

    def test_card_create_page_loads(self, client):
        """カード作成ページが正常に読み込まれることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        client.force_login(user)

        response = client.get(reverse("cards:card_create", args=[deck.pk]))
        assert response.status_code == 200
        assert "カード追加" in response.content.decode()

    def test_card_create_success(self, client):
        """カード作成が成功することをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        client.force_login(user)

        data = {
            "front": "新しい質問",
            "back": "新しい答え",
        }
        response = client.post(reverse("cards:card_create", args=[deck.pk]), data)

        assert response.status_code == 302
        assert Card.objects.filter(deck=deck, front="新しい質問").exists()

    def test_card_create_other_user_deck(self, client):
        """他ユーザーのデッキにカードを追加できないことをテスト"""
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
        deck = Deck.objects.create(user=user1, name="user1のデッキ")
        client.force_login(user2)

        response = client.get(reverse("cards:card_create", args=[deck.pk]))
        assert response.status_code == 404


@pytest.mark.django_db
class TestCardDetailView:
    """カード詳細ビューのテスト"""

    def test_card_detail_page_loads(self, client):
        """カード詳細ページが正常に読み込まれることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")
        client.force_login(user)

        response = client.get(reverse("cards:card_detail", args=[card.pk]))
        assert response.status_code == 200
        assert "質問" in response.content.decode()

    def test_card_detail_other_user(self, client):
        """他ユーザーのカードにアクセスできないことをテスト"""
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
        deck = Deck.objects.create(user=user1, name="user1のデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")
        client.force_login(user2)

        response = client.get(reverse("cards:card_detail", args=[card.pk]))
        assert response.status_code == 404


@pytest.mark.django_db
class TestCardUpdateView:
    """カード編集ビューのテスト"""

    def test_card_update_page_loads(self, client):
        """カード編集ページが正常に読み込まれることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")
        client.force_login(user)

        response = client.get(reverse("cards:card_edit", args=[card.pk]))
        assert response.status_code == 200
        assert "カード編集" in response.content.decode()

    def test_card_update_success(self, client):
        """カード編集が成功することをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="旧質問", back="旧答え")
        client.force_login(user)

        data = {
            "front": "新質問",
            "back": "新答え",
        }
        response = client.post(reverse("cards:card_edit", args=[card.pk]), data)

        assert response.status_code == 302
        card.refresh_from_db()
        assert card.front == "新質問"
        assert card.back == "新答え"

    def test_card_update_other_user(self, client):
        """他ユーザーのカードを編集できないことをテスト"""
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
        deck = Deck.objects.create(user=user1, name="user1のデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")
        client.force_login(user2)

        response = client.get(reverse("cards:card_edit", args=[card.pk]))
        assert response.status_code == 403


@pytest.mark.django_db
class TestCardDeleteView:
    """カード削除ビューのテスト"""

    def test_card_delete_page_loads(self, client):
        """カード削除確認ページが正常に読み込まれることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")
        client.force_login(user)

        response = client.get(reverse("cards:card_delete", args=[card.pk]))
        assert response.status_code == 200
        assert "削除しますか" in response.content.decode()

    def test_card_delete_success(self, client):
        """カード削除が成功することをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        card = Card.objects.create(deck=deck, front="削除されるカード", back="答え")
        card_pk = card.pk
        client.force_login(user)

        response = client.post(reverse("cards:card_delete", args=[card_pk]))

        assert response.status_code == 302
        assert not Card.objects.filter(pk=card_pk).exists()

    def test_card_delete_other_user(self, client):
        """他ユーザーのカードを削除できないことをテスト"""
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
        deck = Deck.objects.create(user=user1, name="user1のデッキ")
        card = Card.objects.create(deck=deck, front="質問", back="答え")
        client.force_login(user2)

        response = client.post(reverse("cards:card_delete", args=[card.pk]))
        assert response.status_code == 403
        assert Card.objects.filter(pk=card.pk).exists()
