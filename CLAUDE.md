# CLAUDE.md

このファイルは、Claude Codeがこのリポジトリで作業する際のガイダンスを提供します。

## プロジェクト概要

**SRS Flashcard App** - FSRS v4アルゴリズムを使用したAnki風の間隔反復学習Webアプリケーション。

### 主要な特徴
- マルチユーザー対応（各ユーザーが独自のデッキを管理）
- FSRS v4による科学的な復習スケジューリング
- 画像対応のフラッシュカード
- レスポンシブデザイン（モバイル対応）

## 技術スタック

| カテゴリ | 技術 | バージョン |
|---------|------|----------|
| 言語 | Python | 3.13 |
| フレームワーク | Django | 5.2 LTS |
| データベース | SQLite（開発）/ PostgreSQL（本番） | - |
| フロントエンド | Django Templates + HTMX | - |
| CSS | Tailwind CSS | 3.x |
| SRSアルゴリズム | fsrs | 6.x |
| 認証 | Django標準認証 | - |

## プロジェクト構造

```
srs-flashcard-app/
├── config/                 # Djangoプロジェクト設定
│   ├── settings.py        # 設定ファイル
│   ├── urls.py            # ルートURL設定
│   └── wsgi.py            # WSGI設定
├── apps/                   # Djangoアプリケーション
│   ├── accounts/          # ユーザー認証
│   ├── decks/             # デッキ管理
│   ├── cards/             # カード管理
│   ├── study/             # 学習機能・FSRS実装
│   └── dashboard/         # ダッシュボード
├── templates/              # 共通テンプレート
│   └── base.html
├── static/                 # 静的ファイル
│   ├── css/
│   └── js/
├── media/                  # ユーザーアップロード
├── venv/                   # 仮想環境（gitignore）
└── requirements.txt        # Python依存パッケージ
```

## 開発コマンド

### 仮想環境の有効化
```bash
# Windows (cmd)
venv\Scripts\activate.bat

# Windows (PowerShell) - 要実行ポリシー変更
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1
```

### Djangoコマンド
```bash
# 開発サーバー起動
python manage.py runserver

# マイグレーション作成
python manage.py makemigrations

# マイグレーション適用
python manage.py migrate

# スーパーユーザー作成
python manage.py createsuperuser

# 新しいアプリ作成
python manage.py startapp <アプリ名>
```

### Tailwind CSS
```bash
# 開発時（監視モード）
npm run watch:css

# 本番用ビルド
npm run build:css
```

### テスト
```bash
# 全テスト実行
pytest

# カバレッジ付き
pytest --cov=apps

# 特定アプリのテスト
pytest apps/study/tests/
```

## コーディング規約

### Djangoアプリ
- すべてのアプリは `apps/` ディレクトリに配置
- 各アプリに `urls.py`, `forms.py`, `tests/` を作成
- クラスベースビュー（CBV）を優先的に使用
- 認証が必要なビューには `@login_required` デコレータを使用

### モデル
- すべてのモデルに `created_at` と `updated_at` フィールドを追加
- `__str__` メソッドを必ず定義
- ForeignKeyには `related_name` を指定
- 頻繁にクエリされるフィールドにはインデックスを追加

### テンプレート
- すべてのページは `base.html` を継承
- `{% block %}`, `{% include %}` を活用
- スタイリングにはTailwind CSSクラスを使用
- 動的な操作にはHTMXを使用（hx-get, hx-post等）

### URL設計
- 名前付きURL: `path('', view, name='view-name')`
- アプリごとに `apps/<アプリ>/urls.py` でURLをグループ化
- `config/urls.py` でアプリURLをインクルード

### フォーム
- 可能な限りDjango ModelFormを使用
- Tailwind CSSクラスはウィジェット経由で適用

## FSRS実装

FSRSアルゴリズムは `apps/study/services.py` に実装。

### 主要モデル
- `CardState`: FSRSパラメータを保存（難易度、安定性、次回復習日）
- `ReviewLog`: 復習履歴を記録（統計用）

### 評価スケール（4段階）
| 値 | 名前 | 説明 |
|----|------|------|
| 1 | Again（もう一度） | 完全に忘れていた |
| 2 | Hard（難しい） | 思い出すのに苦労した |
| 3 | Good（良い） | 思い出せた |
| 4 | Easy（簡単） | 即座に思い出せた |

## 認証システム

Django標準認証を使用：
- `django.contrib.auth` のUserモデル
- `@login_required` デコレータで保護
- セッションベース認証

## ローカライゼーション

- **主要言語**: 日本語
- **UIテキスト**: 日本語で記述
- **日付形式**: YYYY年MM月DD日
- **タイムゾーン**: Asia/Tokyo

## 関連ドキュメント

- [REQUIREMENTS.md](REQUIREMENTS.md) - 要件定義書
- [TECHNICAL_SPEC.md](TECHNICAL_SPEC.md) - 技術仕様書
- [MVP_ROADMAP.md](MVP_ROADMAP.md) - 開発ロードマップ
- [SETUP.md](SETUP.md) - セットアップ手順

## GitHub Issues

開発はGitHub Issuesで管理：
- Issue #1: Phase 0 - 環境セットアップ ✅完了
- Issue #2: Phase 1 - ユーザー認証
- Issue #3: Phase 2 - デッキ管理
- Issue #4: Phase 3 - カード管理
- Issue #5: Phase 4 - FSRS実装
- Issue #6: Phase 5 - 学習機能
- Issue #7: Phase 6 - ダッシュボード

## 重要な注意事項

1. **仮想環境を必ず有効化** - Djangoコマンド実行前に
2. **モデル変更後はマイグレーション** - `makemigrations` → `migrate`
3. **Django ORMを使用** - 生SQLは避ける
4. **セキュリティベストプラクティス** - CSRFトークン、パスワードハッシュ化等
5. **コミット前にテスト** - 影響範囲のpytestを実行
6. **日本語でコメント・ドキュメント** - UIテキストも日本語