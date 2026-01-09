# SRS Flashcard App - 技術仕様書

## 技術スタック

### バックエンド
- **言語**: Python 3.13（推奨）
- **フレームワーク**: Django 5.2 LTS（長期サポート版）
- **データベース**: SQLite (開発環境), PostgreSQL (本番環境対応)
- **FSRS実装**: fsrs 6.x（Python実装）

### フロントエンド
- **テンプレートエンジン**: Django Templates
- **CSSフレームワーク**: Tailwind CSS 3.x
- **JavaScript**: Vanilla JS + HTMX (動的UI用)
- **アイコン**: Heroicons または Font Awesome

### 開発ツール
- **パッケージ管理**: pip + requirements.txt（または Poetry）
- **リンター**: Flake8, Black
- **フォーマッター**: Black, isort
- **テスト**: pytest, pytest-django
- **バージョン管理**: Git

---

## プロジェクト構造

```
srs-flashcard-app/
├── manage.py
├── requirements.txt
├── README.md
├── REQUIREMENTS.md
├── TECHNICAL_SPEC.md
├── .gitignore
├── .env.example
│
├── config/                      # プロジェクト設定
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── accounts/                # ユーザー認証・管理
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── tests/
│   │   └── templates/
│   │       └── accounts/
│   │
│   ├── decks/                   # デッキ管理
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── tests/
│   │   └── templates/
│   │       └── decks/
│   │
│   ├── cards/                   # カード管理
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── tests/
│   │   └── templates/
│   │       └── cards/
│   │
│   ├── study/                   # 学習機能
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── services.py          # FSRS アルゴリズム実装
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── tests/
│   │   └── templates/
│   │       └── study/
│   │
│   └── dashboard/               # ダッシュボード
│       ├── __init__.py
│       ├── views.py
│       ├── urls.py
│       ├── tests/
│       └── templates/
│           └── dashboard/
│
├── static/
│   ├── css/
│   │   └── styles.css          # Tailwind出力先
│   ├── js/
│   │   └── main.js
│   └── images/
│
├── media/                       # ユーザーアップロード画像
│   └── cards/
│       └── images/
│
└── templates/
    ├── base.html
    ├── navbar.html
    └── components/
```

---

## データベース設計

### ER図概要

```
User (Django標準)
  ├─ 1:N ─ Deck
  └─ 1:N ─ CardState

Deck
  └─ 1:N ─ Card

Card
  ├─ 1:N ─ CardState
  └─ 1:N ─ ReviewLog

CardState
  └─ 1:N ─ ReviewLog
```

### テーブル定義

#### 1. User (Django標準 auth.User を拡張)
```python
# Django標準のUserモデルを使用
# カスタムフィールドが必要な場合はUserProfileで拡張

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    timezone = models.CharField(max_length=50, default='Asia/Tokyo')
    daily_new_cards = models.IntegerField(default=20)  # 1日の新規カード上限
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 2. Deck (デッキ)
```python
class Deck(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', '-created_at']),
        ]

    def __str__(self):
        return self.name
```

#### 3. Card (カード)
```python
class Card(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='cards')
    front = models.TextField()  # 表面（質問）
    back = models.TextField()   # 裏面（答え）
    image = models.ImageField(upload_to='cards/images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['deck', '-created_at']),
        ]

    def __str__(self):
        return f"{self.front[:50]}..."
```

#### 4. CardState (カード学習状態)
```python
from enum import IntEnum

class CardStatus(IntEnum):
    NEW = 0          # 新規
    LEARNING = 1     # 学習中
    REVIEW = 2       # 復習中
    RELEARNING = 3   # 再学習中

class CardState(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='states')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='card_states')

    # FSRS パラメータ
    status = models.IntegerField(
        choices=[(s.value, s.name) for s in CardStatus],
        default=CardStatus.NEW
    )
    difficulty = models.FloatField(default=0.0)      # 難易度 (0-10)
    stability = models.FloatField(default=0.0)       # 記憶の安定性（日数）
    retrievability = models.FloatField(default=0.0)  # 想起可能性 (0-1)

    # スケジューリング
    due = models.DateTimeField()                     # 次回復習日時
    last_review = models.DateTimeField(null=True, blank=True)

    # 統計
    reps = models.IntegerField(default=0)            # 復習回数
    lapses = models.IntegerField(default=0)          # 忘却回数

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['card', 'user']]
        indexes = [
            models.Index(fields=['user', 'due']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.card.front[:30]} - {self.user.username}"
```

#### 5. ReviewLog (学習履歴)
```python
from enum import IntEnum

class Rating(IntEnum):
    AGAIN = 1   # もう一度
    HARD = 2    # 難しい
    GOOD = 3    # 良い
    EASY = 4    # 簡単

class ReviewLog(models.Model):
    card_state = models.ForeignKey(CardState, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        choices=[(r.value, r.name) for r in Rating]
    )

    # 復習時の状態スナップショット
    review_duration = models.IntegerField()          # 学習時間（秒）
    scheduled_days = models.FloatField()             # 次回までの予定日数
    elapsed_days = models.FloatField()               # 前回からの経過日数

    # FSRS パラメータのスナップショット
    difficulty = models.FloatField()
    stability = models.FloatField()

    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-reviewed_at']
        indexes = [
            models.Index(fields=['card_state', '-reviewed_at']),
        ]
```

---

## FSRS v4 アルゴリズム実装

### 実装アプローチ

1. **ライブラリ選択**: `fsrs-rs-python` を使用
   - Rust実装で高速
   - Pythonバインディングで簡単に統合
   - FSRS v4仕様に完全準拠

2. **カスタムサービス層**: `apps/study/services.py`
   ```python
   from fsrs import FSRS, Card as FSRSCard, Rating
   from datetime import datetime, timezone

   class FSRSService:
       def __init__(self):
           self.fsrs = FSRS()

       def schedule_card(self, card_state, rating):
           """
           カードの評価に基づいて次回復習をスケジューリング
           """
           # CardStateからFSRSCardへ変換
           fsrs_card = self._to_fsrs_card(card_state)

           # FSRSアルゴリズムで計算
           now = datetime.now(timezone.utc)
           scheduling_cards = self.fsrs.repeat(fsrs_card, now)

           # 評価に応じた結果を取得
           result = self._get_result_by_rating(scheduling_cards, rating)

           # CardStateを更新
           self._update_card_state(card_state, result)

           return card_state

       def _to_fsrs_card(self, card_state):
           """CardState → FSRSCard 変換"""
           return FSRSCard(
               difficulty=card_state.difficulty,
               stability=card_state.stability,
               due=card_state.due,
               reps=card_state.reps,
               lapses=card_state.lapses,
           )

       def _get_result_by_rating(self, scheduling_cards, rating):
           """評価に応じた結果を取得"""
           rating_map = {
               Rating.AGAIN: scheduling_cards.again,
               Rating.HARD: scheduling_cards.hard,
               Rating.GOOD: scheduling_cards.good,
               Rating.EASY: scheduling_cards.easy,
           }
           return rating_map[rating]

       def _update_card_state(self, card_state, result):
           """FSRS結果でCardStateを更新"""
           card_state.difficulty = result.card.difficulty
           card_state.stability = result.card.stability
           card_state.due = result.card.due
           card_state.reps = result.card.reps
           card_state.lapses = result.card.lapses
           card_state.last_review = datetime.now(timezone.utc)
   ```

### FSRS デフォルトパラメータ

```python
# config/settings.py

FSRS_PARAMETERS = {
    'w': [  # 17個の重みパラメータ（FSRS v4デフォルト）
        0.4, 0.6, 2.4, 5.8, 4.93, 0.94, 0.86, 0.01, 1.49, 0.14, 0.94, 2.18, 0.05,
        0.34, 1.26, 0.29, 2.61
    ],
    'request_retention': 0.9,  # 目標想起率 90%
    'maximum_interval': 36500,  # 最大間隔 100年
    'enable_fuzz': True,        # ファジング有効化
}
```

---

## API設計（内部ビュー）

### URL構造

```python
# config/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('decks/', include('apps.decks.urls')),
    path('cards/', include('apps.cards.urls')),
    path('study/', include('apps.study.urls')),
]
```

### 主要ビュー

#### Dashboard
```python
# apps/dashboard/urls.py
urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
]
```

#### Decks
```python
# apps/decks/urls.py
urlpatterns = [
    path('', DeckListView.as_view(), name='deck-list'),
    path('create/', DeckCreateView.as_view(), name='deck-create'),
    path('<int:pk>/', DeckDetailView.as_view(), name='deck-detail'),
    path('<int:pk>/edit/', DeckUpdateView.as_view(), name='deck-update'),
    path('<int:pk>/delete/', DeckDeleteView.as_view(), name='deck-delete'),
]
```

#### Cards
```python
# apps/cards/urls.py
urlpatterns = [
    path('deck/<int:deck_id>/', CardListView.as_view(), name='card-list'),
    path('deck/<int:deck_id>/create/', CardCreateView.as_view(), name='card-create'),
    path('<int:pk>/', CardDetailView.as_view(), name='card-detail'),
    path('<int:pk>/edit/', CardUpdateView.as_view(), name='card-update'),
    path('<int:pk>/delete/', CardDeleteView.as_view(), name='card-delete'),
]
```

#### Study
```python
# apps/study/urls.py
urlpatterns = [
    path('deck/<int:deck_id>/', StudySessionView.as_view(), name='study-session'),
    path('card/<int:card_id>/review/', ReviewCardView.as_view(), name='review-card'),
]
```

---

## フロントエンド設計

### Tailwind CSS設定

```javascript
// tailwind.config.js
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
```

### ベーステンプレート

```django
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}SRS Flashcard App{% endblock %}</title>
    <link href="{% static 'css/styles.css' %}" rel="stylesheet">
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    {% block extra_head %}{% endblock %}
</head>
<body class="bg-gray-50">
    {% include 'navbar.html' %}

    <main class="container mx-auto px-4 py-8">
        {% if messages %}
            {% for message in messages %}
                <div class="mb-4 p-4 rounded-lg {% if message.tags == 'error' %}bg-red-100 text-red-700{% else %}bg-green-100 text-green-700{% endif %}">
                    {{ message }}
                </div>
            {% endfor %}
        {% endif %}

        {% block content %}{% endblock %}
    </main>

    <script src="{% static 'js/main.js' %}"></script>
    {% block extra_scripts %}{% endblock %}
</body>
</html>
```

### 学習画面のインタラクティブ機能

```javascript
// static/js/main.js

// キーボードショートカット
document.addEventListener('DOMContentLoaded', () => {
    const studyCard = document.getElementById('study-card');
    if (studyCard) {
        document.addEventListener('keydown', (e) => {
            if (e.key === ' ') {
                e.preventDefault();
                document.getElementById('show-answer-btn')?.click();
            }
            if (e.key === '1') document.querySelector('[data-rating="1"]')?.click();
            if (e.key === '2') document.querySelector('[data-rating="2"]')?.click();
            if (e.key === '3') document.querySelector('[data-rating="3"]')?.click();
            if (e.key === '4') document.querySelector('[data-rating="4"]')?.click();
        });
    }
});

// 画像プレビュー
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('image-preview').src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}
```

---

## セキュリティ対策

### 1. 認証・認可
- Django標準の認証システムを使用
- `@login_required` デコレータで全ページを保護
- オブジェクトレベルの権限チェック（ユーザーは自分のデッキのみアクセス可能）

### 2. CSRF対策
- Django標準のCSRF保護を有効化
- すべてのフォームに `{% csrf_token %}` を含める

### 3. XSS対策
- Djangoテンプレートの自動エスケープを使用
- ユーザー入力を `|safe` フィルタで使用しない
- Markdownレンダリングはサニタイズ済みライブラリを使用

### 4. SQL Injection対策
- Django ORMを使用（生SQLは避ける）
- パラメータ化されたクエリを使用

### 5. ファイルアップロード対策
```python
# config/settings.py
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB

# カスタムバリデータ
from django.core.exceptions import ValidationError

def validate_image_file(file):
    ext = file.name.split('.')[-1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(f'Unsupported file extension: {ext}')
    if file.size > MAX_UPLOAD_SIZE:
        raise ValidationError('File size exceeds 5MB')
```

---

## パフォーマンス最適化

### 1. データベースクエリ最適化
```python
# select_related / prefetch_related を使用
decks = Deck.objects.filter(owner=request.user)\
    .prefetch_related('cards')\
    .annotate(
        total_cards=Count('cards'),
        due_cards=Count('cards__states', filter=Q(cards__states__due__lte=timezone.now()))
    )
```

### 2. キャッシュ戦略
```python
# config/settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# ビューでのキャッシュ使用例
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # 5分キャッシュ
def deck_stats(request, deck_id):
    # ...
```

### 3. 静的ファイルの最適化
- Tailwind CSSのプロダクションビルド（未使用クラスの削除）
- 画像の遅延読み込み（lazy loading）
- CDNの使用（将来的に）

---

## テスト戦略

### 1. 単体テスト
```python
# apps/study/tests/test_services.py
import pytest
from apps.study.services import FSRSService
from apps.cards.models import Card, CardState

@pytest.mark.django_db
class TestFSRSService:
    def test_schedule_card_with_good_rating(self, user, card):
        service = FSRSService()
        card_state = CardState.objects.create(
            card=card,
            user=user,
            due=timezone.now()
        )

        new_state = service.schedule_card(card_state, Rating.GOOD)

        assert new_state.reps == 1
        assert new_state.due > timezone.now()
```

### 2. 統合テスト
```python
# apps/study/tests/test_views.py
from django.test import TestCase, Client
from django.contrib.auth.models import User

class StudySessionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_study_session_shows_due_cards(self):
        # テストコード
        pass
```

### 3. E2Eテスト（将来実装）
- Playwright または Selenium を使用
- 主要なユーザーフローをテスト

---

## デプロイメント

### ローカル開発環境セットアップ

```bash
# 1. リポジトリクローン
git clone <repository-url>
cd srs-flashcard-app

# 2. 仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 依存パッケージインストール
pip install -r requirements.txt

# 4. 環境変数設定
cp .env.example .env
# .envファイルを編集

# 5. データベースマイグレーション
python manage.py migrate

# 6. スーパーユーザー作成
python manage.py createsuperuser

# 7. 静的ファイル収集
python manage.py collectstatic

# 8. Tailwind CSSビルド
npm run build:css

# 9. 開発サーバー起動
python manage.py runserver
```

### 環境変数（.env.example）

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (本番環境)
# DATABASE_URL=postgresql://user:password@localhost:5432/srs_db

# Media Files
MEDIA_ROOT=media/
MEDIA_URL=/media/

# Email (将来実装)
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@example.com
# EMAIL_HOST_PASSWORD=your-password
```

---

## 今後の技術的改善

### Phase 2
- Django REST Framework 導入（API化）
- Celery導入（非同期タスク処理）
- Redis導入（キャッシュ・セッション管理）

### Phase 3
- PostgreSQL全文検索（カード検索の高速化）
- Elasticsearch導入（高度な検索機能）
- WebSocket対応（リアルタイム更新）

### Phase 4
- GraphQL API（Apollo）
- マイクロサービス化（学習エンジン分離）
- Docker Kubernetes デプロイ

---

**この技術仕様書はMVP開発を前提とし、必要に応じてアップデートされます。**