"""
認証フォームのテスト
"""

import pytest
from django.contrib.auth.models import User

from apps.accounts.forms import SignUpForm, LoginForm, UserUpdateForm
from apps.accounts.models import UserProfile


@pytest.mark.django_db
class TestSignUpForm:
    """新規登録フォームのテスト"""

    def test_valid_signup_form(self):
        """有効なデータでフォームが検証されることをテスト"""
        form = SignUpForm(data={
            "username": "testuser",
            "email": "test@example.com",
            "password1": "testpass123!",
            "password2": "testpass123!",
        })
        assert form.is_valid()

    def test_signup_form_password_mismatch(self):
        """パスワード不一致でエラーになることをテスト"""
        form = SignUpForm(data={
            "username": "testuser",
            "email": "test@example.com",
            "password1": "testpass123!",
            "password2": "differentpass!",
        })
        assert not form.is_valid()
        assert "password2" in form.errors

    def test_signup_form_duplicate_email(self):
        """重複メールアドレスでエラーになることをテスト"""
        User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="testpass123"
        )

        form = SignUpForm(data={
            "username": "newuser",
            "email": "existing@example.com",
            "password1": "testpass123!",
            "password2": "testpass123!",
        })
        assert not form.is_valid()
        assert "email" in form.errors

    def test_signup_form_required_fields(self):
        """必須フィールドが空の場合エラーになることをテスト"""
        form = SignUpForm(data={})
        assert not form.is_valid()
        assert "username" in form.errors
        assert "email" in form.errors
        assert "password1" in form.errors
        assert "password2" in form.errors


@pytest.mark.django_db
class TestLoginForm:
    """ログインフォームのテスト"""

    def test_valid_login_form(self):
        """有効なデータでフォームが検証されることをテスト"""
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        form = LoginForm(data={
            "username": "testuser",
            "password": "testpass123",
        })
        assert form.is_valid()

    def test_login_form_required_fields(self):
        """必須フィールドが空の場合エラーになることをテスト"""
        form = LoginForm(data={})
        assert not form.is_valid()
        assert "username" in form.errors
        assert "password" in form.errors


@pytest.mark.django_db
class TestUserUpdateForm:
    """ユーザー更新フォームのテスト"""

    def test_valid_update_form(self):
        """有効なデータでフォームが検証されることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        profile = UserProfile.objects.create(user=user)

        form = UserUpdateForm(
            data={
                "email": "newemail@example.com",
                "timezone": "UTC",
                "daily_new_cards": 30,
            },
            instance=user,
            profile=profile,
        )
        assert form.is_valid()

    def test_update_form_saves_profile(self):
        """プロフィールデータが正しく保存されることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        profile = UserProfile.objects.create(user=user)

        form = UserUpdateForm(
            data={
                "email": "newemail@example.com",
                "timezone": "UTC",
                "daily_new_cards": 50,
            },
            instance=user,
            profile=profile,
        )
        assert form.is_valid()
        form.save()

        profile.refresh_from_db()
        assert profile.timezone == "UTC"
        assert profile.daily_new_cards == 50

    def test_update_form_duplicate_email(self):
        """他のユーザーと同じメールアドレスでエラーになることをテスト"""
        User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123"
        )

        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        profile = UserProfile.objects.create(user=user)

        form = UserUpdateForm(
            data={
                "email": "other@example.com",
                "timezone": "Asia/Tokyo",
                "daily_new_cards": 20,
            },
            instance=user,
            profile=profile,
        )
        assert not form.is_valid()
        assert "email" in form.errors
