"""
UserProfileモデルのテスト
"""

import pytest
from django.contrib.auth.models import User

from apps.accounts.models import UserProfile


@pytest.mark.django_db
class TestUserProfile:
    """UserProfileモデルのテストクラス"""

    def test_create_user_profile(self):
        """UserProfileが正常に作成できることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        profile = UserProfile.objects.create(user=user)

        assert profile.user == user
        assert profile.timezone == "Asia/Tokyo"
        assert profile.daily_new_cards == 20

    def test_user_profile_str(self):
        """__str__メソッドが正しく動作することをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        profile = UserProfile.objects.create(user=user)

        assert str(profile) == "testuserのプロフィール"

    def test_user_profile_defaults(self):
        """デフォルト値が正しく設定されることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        profile = UserProfile.objects.create(user=user)

        assert profile.timezone == "Asia/Tokyo"
        assert profile.daily_new_cards == 20

    def test_user_profile_custom_values(self):
        """カスタム値が正しく保存されることをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        profile = UserProfile.objects.create(
            user=user,
            timezone="UTC",
            daily_new_cards=50
        )

        assert profile.timezone == "UTC"
        assert profile.daily_new_cards == 50

    def test_user_profile_related_name(self):
        """related_nameが正しく動作することをテスト"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        profile = UserProfile.objects.create(user=user)

        assert user.profile == profile
