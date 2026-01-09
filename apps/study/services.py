"""
FSRS v4アルゴリズムを使用した学習サービス
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from django.utils import timezone
from fsrs import Scheduler, Card as FSRSCard, Rating, State

from django.contrib.auth.models import User
from apps.cards.models import Card
from .models import CardState, ReviewLog


class FSRSService:
    """FSRSアルゴリズムを使用した復習スケジューリングサービス"""

    def __init__(self):
        self.scheduler = Scheduler()

    def get_or_create_card_state(self, card: Card, user: User) -> CardState:
        """カードの学習状態を取得または作成（ユーザーごと）"""
        card_state, created = CardState.objects.get_or_create(
            card=card,
            user=user,
            defaults={
                "stability": 0.0,
                "difficulty": 0.0,
                "state": CardState.State.NEW,
                "due": timezone.now(),
                "next_review": timezone.now(),
            }
        )
        return card_state

    def _card_state_to_fsrs_card(self, card_state: CardState) -> FSRSCard:
        """CardStateをFSRSのCardオブジェクトに変換"""
        # fsrs 6.xではStateはLearning, Review, Relearningの3つ
        # NEW状態はLearning（step=0）として扱う
        state_mapping = {
            CardState.State.NEW: State.Learning,
            CardState.State.LEARNING: State.Learning,
            CardState.State.REVIEW: State.Review,
            CardState.State.RELEARNING: State.Relearning,
        }

        fsrs_state = state_mapping.get(card_state.state, State.Learning)

        # 新規カードの場合はstep=0のデフォルトカードを使用
        if card_state.state == CardState.State.NEW:
            fsrs_card = FSRSCard()
            fsrs_card.due = card_state.due
            return fsrs_card

        # 既存のカード状態を復元
        fsrs_card = FSRSCard(
            state=fsrs_state,
            stability=card_state.stability if card_state.stability > 0 else None,
            difficulty=card_state.difficulty if card_state.difficulty > 0 else None,
            due=card_state.due,
            last_review=card_state.last_review,
        )

        return fsrs_card

    def _rating_to_fsrs_rating(self, rating: int) -> Rating:
        """ReviewLog.RatingをFSRSのRatingに変換"""
        rating_mapping = {
            ReviewLog.Rating.AGAIN: Rating.Again,
            ReviewLog.Rating.HARD: Rating.Hard,
            ReviewLog.Rating.GOOD: Rating.Good,
            ReviewLog.Rating.EASY: Rating.Easy,
        }
        return rating_mapping.get(rating, Rating.Good)

    def _fsrs_state_to_card_state(self, fsrs_state: State) -> int:
        """FSRSのStateをCardState.Stateに変換"""
        # fsrs 6.xではStateはLearning, Review, Relearningの3つ
        state_mapping = {
            State.Learning: CardState.State.LEARNING,
            State.Review: CardState.State.REVIEW,
            State.Relearning: CardState.State.RELEARNING,
        }
        return state_mapping.get(fsrs_state, CardState.State.LEARNING)

    def review_card(
        self,
        card: Card,
        user: User,
        rating: int,
        duration: int = 0,
        review_time: Optional[datetime] = None
    ) -> CardState:
        """
        カードを復習してスケジュールを更新

        Args:
            card: 復習するカード
            user: 学習するユーザー
            rating: 評価 (1=Again, 2=Hard, 3=Good, 4=Easy)
            duration: 回答時間（ミリ秒）
            review_time: 復習日時（指定しない場合は現在時刻）

        Returns:
            更新されたCardState
        """
        if review_time is None:
            review_time = timezone.now()

        # CardStateを取得または作成
        card_state = self.get_or_create_card_state(card, user)

        # 復習前の状態を保存（ログ用）
        old_stability = card_state.stability
        old_difficulty = card_state.difficulty
        old_state = card_state.state

        # 経過日数を計算
        if card_state.last_review:
            elapsed_days = (review_time - card_state.last_review).total_seconds() / 86400
        else:
            elapsed_days = 0

        # FSRSで次回復習日を計算
        fsrs_card = self._card_state_to_fsrs_card(card_state)
        fsrs_rating = self._rating_to_fsrs_rating(rating)

        # 復習を実行（fsrs 6.xはタプル (Card, ReviewLog) を返す）
        result_card, _ = self.scheduler.review_card(fsrs_card, fsrs_rating, review_time)

        # 予定間隔（日数）を計算
        scheduled_days = (result_card.due - review_time).total_seconds() / 86400

        # CardStateを更新
        card_state.stability = result_card.stability or 0.0
        card_state.difficulty = result_card.difficulty or 0.0
        card_state.due = result_card.due
        card_state.next_review = result_card.due
        card_state.last_review = review_time
        card_state.state = self._fsrs_state_to_card_state(result_card.state)
        # repsとlapsesは自分で管理（fsrs 6.xのCardには存在しない）
        card_state.reps += 1
        if rating == ReviewLog.Rating.AGAIN and card_state.state in [CardState.State.REVIEW, CardState.State.RELEARNING]:
            card_state.lapses += 1
        card_state.save()

        # ReviewLogを作成
        ReviewLog.objects.create(
            card=card,
            user=user,
            rating=rating,
            state=old_state,
            stability=old_stability,
            difficulty=old_difficulty,
            elapsed_days=elapsed_days,
            scheduled_days=scheduled_days,
            review_time=review_time,
            duration=duration,
        )

        return card_state

    def get_next_review_intervals(
        self,
        card: Card,
        user: User,
        review_time: Optional[datetime] = None
    ) -> dict:
        """
        各評価に対する次回復習間隔を取得

        Args:
            card: カード
            user: 学習するユーザー
            review_time: 復習日時（指定しない場合は現在時刻）

        Returns:
            {rating: interval_str} の辞書
        """
        if review_time is None:
            review_time = timezone.now()

        card_state = self.get_or_create_card_state(card, user)
        fsrs_card = self._card_state_to_fsrs_card(card_state)

        intervals = {}

        for rating in [Rating.Again, Rating.Hard, Rating.Good, Rating.Easy]:
            # 各評価でのスケジュールを計算（fsrs 6.xはタプル (Card, ReviewLog) を返す）
            # fsrs 6.xのCardはstep, stability, difficulty, due, state, last_reviewのみ
            result_card, _ = self.scheduler.review_card(
                FSRSCard(
                    stability=fsrs_card.stability,
                    difficulty=fsrs_card.difficulty,
                    due=fsrs_card.due,
                    state=fsrs_card.state,
                    step=fsrs_card.step,
                    last_review=fsrs_card.last_review,
                ),
                rating,
                review_time
            )

            interval_seconds = (result_card.due - review_time).total_seconds()

            # 日本語の間隔文字列に変換
            rating_value = {
                Rating.Again: ReviewLog.Rating.AGAIN,
                Rating.Hard: ReviewLog.Rating.HARD,
                Rating.Good: ReviewLog.Rating.GOOD,
                Rating.Easy: ReviewLog.Rating.EASY,
            }[rating]

            intervals[rating_value] = self._format_interval(interval_seconds)

        return intervals

    def _format_interval(self, seconds: float) -> str:
        """秒数を日本語の間隔文字列に変換"""
        if seconds < 60:
            return f"{int(seconds)}秒"
        elif seconds < 3600:
            return f"{int(seconds / 60)}分"
        elif seconds < 86400:
            return f"{int(seconds / 3600)}時間"
        else:
            days = seconds / 86400
            if days < 30:
                return f"{int(days)}日"
            elif days < 365:
                return f"{int(days / 30)}ヶ月"
            else:
                return f"{days / 365:.1f}年"


# シングルトンインスタンス
fsrs_service = FSRSService()
