"""
デッキビューのテスト
"""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from apps.decks.models import Deck


@pytest.mark.django_db
class TestDeckListView:
    """デッキ一覧ビューのテスト"""

    def test_deck_list_requires_login(self, client):
        """未ログイン時にリダイレクトされることをテスト"""
        response = client.get(reverse("decks:deck_list"))
        assert response.status_code == 302
        assert "login" in response.url

    def test_deck_list_page_loads(self, client):
        """デッキ一覧ページが正常に読み込まれることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        client.force_login(user)

        response = client.get(reverse("decks:deck_list"))
        assert response.status_code == 200
        assert "デッキ一覧" in response.content.decode()

    def test_deck_list_shows_user_decks(self, client):
        """ユーザー自身のデッキのみ表示されることをテスト"""
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
        deck1 = Deck.objects.create(user=user1, name="user1のデッキ")
        Deck.objects.create(user=user2, name="user2のデッキ")

        client.force_login(user1)
        response = client.get(reverse("decks:deck_list"))

        assert "user1のデッキ" in response.content.decode()
        assert "user2のデッキ" not in response.content.decode()


@pytest.mark.django_db
class TestDeckCreateView:
    """デッキ作成ビューのテスト"""

    def test_deck_create_page_loads(self, client):
        """デッキ作成ページが正常に読み込まれることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        client.force_login(user)

        response = client.get(reverse("decks:deck_create"))
        assert response.status_code == 200
        assert "新規デッキ作成" in response.content.decode()

    def test_deck_create_success(self, client):
        """デッキ作成が成功することをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        client.force_login(user)

        data = {
            "name": "新しいデッキ",
            "description": "テスト用デッキです",
        }
        response = client.post(reverse("decks:deck_create"), data)

        assert response.status_code == 302
        assert Deck.objects.filter(user=user, name="新しいデッキ").exists()

    def test_deck_create_duplicate_name(self, client):
        """重複デッキ名でエラーになることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        Deck.objects.create(user=user, name="既存デッキ")
        client.force_login(user)

        data = {
            "name": "既存デッキ",
            "description": "",
        }
        response = client.post(reverse("decks:deck_create"), data)

        assert response.status_code == 200  # フォームエラーで再表示
        assert Deck.objects.filter(user=user, name="既存デッキ").count() == 1


@pytest.mark.django_db
class TestDeckDetailView:
    """デッキ詳細ビューのテスト"""

    def test_deck_detail_page_loads(self, client):
        """デッキ詳細ページが正常に読み込まれることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        client.force_login(user)

        response = client.get(reverse("decks:deck_detail", args=[deck.pk]))
        assert response.status_code == 200
        assert "テストデッキ" in response.content.decode()

    def test_deck_detail_other_user(self, client):
        """他ユーザーのデッキにアクセスできないことをテスト"""
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

        response = client.get(reverse("decks:deck_detail", args=[deck.pk]))
        assert response.status_code == 404


@pytest.mark.django_db
class TestDeckUpdateView:
    """デッキ編集ビューのテスト"""

    def test_deck_update_page_loads(self, client):
        """デッキ編集ページが正常に読み込まれることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        client.force_login(user)

        response = client.get(reverse("decks:deck_edit", args=[deck.pk]))
        assert response.status_code == 200
        assert "デッキ編集" in response.content.decode()

    def test_deck_update_success(self, client):
        """デッキ編集が成功することをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="旧デッキ名")
        client.force_login(user)

        data = {
            "name": "新デッキ名",
            "description": "更新された説明",
        }
        response = client.post(reverse("decks:deck_edit", args=[deck.pk]), data)

        assert response.status_code == 302
        deck.refresh_from_db()
        assert deck.name == "新デッキ名"
        assert deck.description == "更新された説明"

    def test_deck_update_other_user(self, client):
        """他ユーザーのデッキを編集できないことをテスト"""
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

        response = client.get(reverse("decks:deck_edit", args=[deck.pk]))
        assert response.status_code == 403


@pytest.mark.django_db
class TestDeckDeleteView:
    """デッキ削除ビューのテスト"""

    def test_deck_delete_page_loads(self, client):
        """デッキ削除確認ページが正常に読み込まれることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="テストデッキ")
        client.force_login(user)

        response = client.get(reverse("decks:deck_delete", args=[deck.pk]))
        assert response.status_code == 200
        assert "削除しますか" in response.content.decode()

    def test_deck_delete_success(self, client):
        """デッキ削除が成功することをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        deck = Deck.objects.create(user=user, name="削除されるデッキ")
        deck_pk = deck.pk
        client.force_login(user)

        response = client.post(reverse("decks:deck_delete", args=[deck_pk]))

        assert response.status_code == 302
        assert not Deck.objects.filter(pk=deck_pk).exists()

    def test_deck_delete_other_user(self, client):
        """他ユーザーのデッキを削除できないことをテスト"""
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

        response = client.post(reverse("decks:deck_delete", args=[deck.pk]))
        assert response.status_code == 403
        assert Deck.objects.filter(pk=deck.pk).exists()
