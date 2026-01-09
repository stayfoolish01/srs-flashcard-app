"""
学習機能ビューのテスト
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User

from apps.decks.models import Deck
from apps.cards.models import Card
from apps.study.models import CardState, ReviewLog


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="otheruser",
        email="other@example.com",
        password="testpass123"
    )


@pytest.fixture
def deck(user):
    return Deck.objects.create(user=user, name="テストデッキ")


@pytest.fixture
def card(deck):
    return Card.objects.create(deck=deck, front="質問", back="答え")


@pytest.mark.django_db
class TestStudySession:
    """学習セッションビューのテスト"""

    def test_study_session_requires_login(self, client, deck):
        """未ログインユーザーはログインページにリダイレクト"""
        response = client.get(reverse("study:session", args=[deck.pk]))
        assert response.status_code == 302
        assert "login" in response.url

    def test_study_session_no_cards(self, client, user, deck):
        """カードがない場合はno_cardsページを表示"""
        client.force_login(user)
        response = client.get(reverse("study:session", args=[deck.pk]))
        assert response.status_code == 200
        assert "study/no_cards.html" in [t.name for t in response.templates]

    def test_study_session_with_cards(self, client, user, deck, card):
        """カードがある場合は最初のカードにリダイレクト"""
        client.force_login(user)
        response = client.get(reverse("study:session", args=[deck.pk]))
        assert response.status_code == 302
        assert f"/study/{deck.pk}/card/{card.pk}/" in response.url

    def test_study_session_other_user_deck(self, client, other_user, deck):
        """他ユーザーのデッキにはアクセス不可"""
        client.force_login(other_user)
        response = client.get(reverse("study:session", args=[deck.pk]))
        assert response.status_code == 404


@pytest.mark.django_db
class TestStudyCard:
    """カード学習ビューのテスト"""

    def test_study_card_page_loads(self, client, user, deck, card):
        """学習カードページが正常に読み込まれる"""
        client.force_login(user)
        response = client.get(reverse("study:card", args=[deck.pk, card.pk]))
        assert response.status_code == 200
        assert "study/study_card.html" in [t.name for t in response.templates]

    def test_study_card_shows_question(self, client, user, deck, card):
        """質問（表面）が表示される"""
        client.force_login(user)
        response = client.get(reverse("study:card", args=[deck.pk, card.pk]))
        assert "質問" in response.content.decode()

    def test_study_card_show_answer(self, client, user, deck, card):
        """答え表示パラメータで裏面も表示"""
        client.force_login(user)
        response = client.get(
            reverse("study:card", args=[deck.pk, card.pk]) + "?show=answer"
        )
        assert "答え" in response.content.decode()
        assert response.context["show_answer"] is True

    def test_study_card_intervals_displayed(self, client, user, deck, card):
        """復習間隔が表示される"""
        client.force_login(user)
        response = client.get(
            reverse("study:card", args=[deck.pk, card.pk]) + "?show=answer"
        )
        # intervalsがコンテキストに含まれている
        assert "intervals" in response.context
        intervals = response.context["intervals"]
        assert ReviewLog.Rating.AGAIN in intervals
        assert ReviewLog.Rating.GOOD in intervals

    def test_study_card_other_user(self, client, other_user, deck, card):
        """他ユーザーのカードにはアクセス不可"""
        client.force_login(other_user)
        response = client.get(reverse("study:card", args=[deck.pk, card.pk]))
        assert response.status_code == 404


@pytest.mark.django_db
class TestAnswerCard:
    """カード回答ビューのテスト"""

    def test_answer_card_creates_review_log(self, client, user, deck, card):
        """回答するとReviewLogが作成される"""
        client.force_login(user)
        response = client.post(
            reverse("study:answer", args=[deck.pk, card.pk]),
            {"rating": "3"}
        )
        assert ReviewLog.objects.filter(card=card).exists()
        log = ReviewLog.objects.get(card=card)
        assert log.rating == ReviewLog.Rating.GOOD

    def test_answer_card_updates_card_state(self, client, user, deck, card):
        """回答するとCardStateが更新される"""
        client.force_login(user)
        client.post(
            reverse("study:answer", args=[deck.pk, card.pk]),
            {"rating": "3"}
        )
        # ユーザーごとのCardStateを取得
        card_state = CardState.objects.get(card=card, user=user)
        assert card_state.reps == 1

    def test_answer_card_redirects_to_next_or_complete(self, client, user, deck, card):
        """回答後は次のカードか完了ページにリダイレクト"""
        client.force_login(user)
        response = client.post(
            reverse("study:answer", args=[deck.pk, card.pk]),
            {"rating": "3"}
        )
        assert response.status_code == 302
        # カードが1枚だけなので完了ページへ
        assert "complete" in response.url

    def test_answer_card_multiple_cards(self, client, user, deck):
        """複数カードの場合は次のカードへ"""
        card1 = Card.objects.create(deck=deck, front="質問1", back="答え1")
        card2 = Card.objects.create(deck=deck, front="質問2", back="答え2")

        client.force_login(user)
        response = client.post(
            reverse("study:answer", args=[deck.pk, card1.pk]),
            {"rating": "3"}
        )
        assert response.status_code == 302
        # 次のカードへリダイレクト（card2）
        assert f"/card/{card2.pk}/" in response.url

    def test_answer_card_invalid_rating(self, client, user, deck, card):
        """無効な評価はカードページにリダイレクト"""
        client.force_login(user)
        response = client.post(
            reverse("study:answer", args=[deck.pk, card.pk]),
            {"rating": "invalid"}
        )
        assert response.status_code == 302
        assert f"/card/{card.pk}/" in response.url
        # ReviewLogは作成されていない
        assert not ReviewLog.objects.filter(card=card).exists()

    def test_answer_card_get_not_allowed(self, client, user, deck, card):
        """GETリクエストは許可されない"""
        client.force_login(user)
        response = client.get(
            reverse("study:answer", args=[deck.pk, card.pk])
        )
        assert response.status_code == 405  # Method Not Allowed


@pytest.mark.django_db
class TestStudyComplete:
    """学習完了ビューのテスト"""

    def test_study_complete_page_loads(self, client, user, deck):
        """学習完了ページが正常に読み込まれる"""
        client.force_login(user)
        response = client.get(reverse("study:complete", args=[deck.pk]))
        assert response.status_code == 200
        assert "study/complete.html" in [t.name for t in response.templates]

    def test_study_complete_shows_stats(self, client, user, deck, card):
        """学習統計が表示される"""
        # まず復習を記録
        from apps.study.services import FSRSService
        service = FSRSService()
        service.review_card(card, user, ReviewLog.Rating.GOOD)

        client.force_login(user)
        response = client.get(reverse("study:complete", args=[deck.pk]))

        stats = response.context["stats"]
        assert stats["total_reviews"] == 1
        assert stats["good_count"] == 1

    def test_study_complete_other_user(self, client, other_user, deck):
        """他ユーザーのデッキにはアクセス不可"""
        client.force_login(other_user)
        response = client.get(reverse("study:complete", args=[deck.pk]))
        assert response.status_code == 404
