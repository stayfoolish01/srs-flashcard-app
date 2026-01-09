"""
認証ビューのテスト
"""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from apps.accounts.models import UserProfile


@pytest.mark.django_db
class TestSignUpView:
    """新規登録ビューのテスト"""

    def test_signup_page_loads(self, client):
        """新規登録ページが正常に読み込まれることをテスト"""
        response = client.get(reverse("accounts:signup"))
        assert response.status_code == 200
        assert "新規登録" in response.content.decode()

    def test_signup_success(self, client):
        """新規登録が成功することをテスト"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "testpass123!",
            "password2": "testpass123!",
        }
        response = client.post(reverse("accounts:signup"), data)

        # リダイレクトされることを確認
        assert response.status_code == 302

        # ユーザーが作成されていることを確認
        assert User.objects.filter(username="newuser").exists()

        # UserProfileも作成されていることを確認
        user = User.objects.get(username="newuser")
        assert UserProfile.objects.filter(user=user).exists()

    def test_signup_password_mismatch(self, client):
        """パスワード不一致でエラーになることをテスト"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "testpass123!",
            "password2": "differentpass!",
        }
        response = client.post(reverse("accounts:signup"), data)

        # ページが再表示されることを確認
        assert response.status_code == 200
        assert User.objects.filter(username="newuser").exists() is False

    def test_signup_duplicate_email(self, client):
        """重複メールアドレスでエラーになることをテスト"""
        # 既存ユーザー作成
        User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="testpass123"
        )

        data = {
            "username": "newuser",
            "email": "existing@example.com",
            "password1": "testpass123!",
            "password2": "testpass123!",
        }
        response = client.post(reverse("accounts:signup"), data)

        # ページが再表示されることを確認
        assert response.status_code == 200
        assert User.objects.filter(username="newuser").exists() is False


@pytest.mark.django_db
class TestLoginView:
    """ログインビューのテスト"""

    def test_login_page_loads(self, client):
        """ログインページが正常に読み込まれることをテスト"""
        response = client.get(reverse("accounts:login"))
        assert response.status_code == 200
        assert "ログイン" in response.content.decode()

    def test_login_success(self, client):
        """ログインが成功することをテスト"""
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        data = {
            "username": "testuser",
            "password": "testpass123",
        }
        response = client.post(reverse("accounts:login"), data)

        # リダイレクトされることを確認
        assert response.status_code == 302

    def test_login_invalid_credentials(self, client):
        """無効な認証情報でエラーになることをテスト"""
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        data = {
            "username": "testuser",
            "password": "wrongpassword",
        }
        response = client.post(reverse("accounts:login"), data)

        # ページが再表示されることを確認
        assert response.status_code == 200


@pytest.mark.django_db
class TestLogoutView:
    """ログアウトビューのテスト"""

    def test_logout_success(self, client):
        """ログアウトが成功することをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        client.force_login(user)

        response = client.post(reverse("accounts:logout"))

        # リダイレクトされることを確認
        assert response.status_code == 302


@pytest.mark.django_db
class TestProfileView:
    """プロフィールビューのテスト"""

    def test_profile_requires_login(self, client):
        """未ログイン時にリダイレクトされることをテスト"""
        response = client.get(reverse("accounts:profile"))
        assert response.status_code == 302
        assert "login" in response.url

    def test_profile_page_loads(self, client):
        """プロフィールページが正常に読み込まれることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        UserProfile.objects.create(user=user)
        client.force_login(user)

        response = client.get(reverse("accounts:profile"))
        assert response.status_code == 200
        assert "プロフィール" in response.content.decode()


@pytest.mark.django_db
class TestProfileEditView:
    """プロフィール編集ビューのテスト"""

    def test_profile_edit_requires_login(self, client):
        """未ログイン時にリダイレクトされることをテスト"""
        response = client.get(reverse("accounts:profile_edit"))
        assert response.status_code == 302
        assert "login" in response.url

    def test_profile_edit_page_loads(self, client):
        """プロフィール編集ページが正常に読み込まれることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        UserProfile.objects.create(user=user)
        client.force_login(user)

        response = client.get(reverse("accounts:profile_edit"))
        assert response.status_code == 200
        assert "プロフィール編集" in response.content.decode()

    def test_profile_edit_success(self, client):
        """プロフィール編集が成功することをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        UserProfile.objects.create(user=user)
        client.force_login(user)

        data = {
            "email": "newemail@example.com",
            "timezone": "UTC",
            "daily_new_cards": 30,
        }
        response = client.post(reverse("accounts:profile_edit"), data)

        # リダイレクトされることを確認
        assert response.status_code == 302

        # データが更新されていることを確認
        user.refresh_from_db()
        user.profile.refresh_from_db()
        assert user.email == "newemail@example.com"
        assert user.profile.timezone == "UTC"
        assert user.profile.daily_new_cards == 30


@pytest.mark.django_db
class TestHomeRedirect:
    """ホームリダイレクトのテスト"""

    def test_home_redirect_unauthenticated(self, client):
        """未ログイン時にログインページにリダイレクトされることをテスト"""
        response = client.get(reverse("home"))
        assert response.status_code == 302
        assert "login" in response.url

    def test_home_redirect_authenticated(self, client):
        """ログイン時にデッキ一覧ページにリダイレクトされることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        client.force_login(user)

        response = client.get(reverse("home"))
        assert response.status_code == 302
        assert "decks" in response.url
