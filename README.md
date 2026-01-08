# SRS Flashcard App

Anki風の間隔反復学習（Spaced Repetition System）を実装したWebアプリケーション。
FSRS v4アルゴリズムによる科学的な復習スケジューリングで、効率的な記憶定着を支援します。

## 特徴

- 🧠 **FSRS v4アルゴリズム**: 最新の科学的根拠に基づいた間隔反復学習
- 👥 **マルチユーザー対応**: 各ユーザーが独自のデッキとカードを管理
- 🎨 **モダンなUI**: Tailwind CSSによる美しく使いやすいインターフェース
- 📱 **レスポンシブデザイン**: デスクトップ、タブレット、モバイルに完全対応
- 🖼️ **画像対応**: フラッシュカードに画像を添付可能
- ⌨️ **キーボードショートカット**: 効率的な学習をサポート

## 技術スタック

### バックエンド
- **Python**: 3.11+
- **Django**: 5.0+
- **Database**: SQLite (開発), PostgreSQL対応可能
- **FSRS**: fsrs-rs-python (Rust実装のPythonバインディング)

### フロントエンド
- **Template Engine**: Django Templates
- **CSS Framework**: Tailwind CSS 3.x
- **JavaScript**: Vanilla JS + HTMX
- **Icons**: Heroicons

## プロジェクト構成

```
srs-flashcard-app/
├── README.md                 # このファイル
├── REQUIREMENTS.md           # 要件定義書
├── TECHNICAL_SPEC.md         # 技術仕様書
├── MVP_ROADMAP.md            # 開発ロードマップ
├── requirements.txt          # Python依存パッケージ
├── manage.py                 # Django管理コマンド
├── config/                   # プロジェクト設定
├── apps/                     # Djangoアプリケーション
│   ├── accounts/            # ユーザー認証・管理
│   ├── decks/               # デッキ管理
│   ├── cards/               # カード管理
│   ├── study/               # 学習機能（FSRS実装）
│   └── dashboard/           # ダッシュボード
├── static/                   # 静的ファイル
├── media/                    # ユーザーアップロード
└── templates/                # 共通テンプレート
```

## セットアップ手順

### 前提条件
- Python 3.11以上
- pip (Pythonパッケージマネージャー)
- Git

### インストール

1. **リポジトリのクローン**
```bash
git clone <repository-url>
cd srs-flashcard-app
```

2. **仮想環境の作成と有効化**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **依存パッケージのインストール**
```bash
pip install -r requirements.txt
```

4. **環境変数の設定**
```bash
# .env.exampleをコピーして.envを作成
cp .env.example .env

# .envファイルを編集してSECRET_KEYなどを設定
```

5. **データベースのマイグレーション**
```bash
python manage.py migrate
```

6. **スーパーユーザーの作成**
```bash
python manage.py createsuperuser
```

7. **静的ファイルの収集**
```bash
python manage.py collectstatic
```

8. **開発サーバーの起動**
```bash
python manage.py runserver
```

ブラウザで http://127.0.0.1:8000 にアクセスしてください。

## 使い方

### 1. アカウント作成
- トップページから「新規登録」をクリック
- メールアドレスとパスワードを入力

### 2. デッキ作成
- ダッシュボードから「新しいデッキ」をクリック
- デッキ名と説明を入力

### 3. カード追加
- デッキを選択して「カードを追加」
- 表面（質問）と裏面（答え）を入力
- 必要に応じて画像を添付

### 4. 学習開始
- ダッシュボードから「学習開始」をクリック
- カードの表面を確認後、「答えを表示」
- 4段階で自己評価：
  - **Again（もう一度）**: 完全に忘れていた
  - **Hard（難しい）**: 思い出すのに苦労した
  - **Good（良い）**: 思い出せた
  - **Easy（簡単）**: 即座に思い出せた

### キーボードショートカット
- `Space`: 答えを表示
- `1`: Again
- `2`: Hard
- `3`: Good
- `4`: Easy

## 開発ロードマップ

### MVP (v1.0.0) - 10週間
- [x] 要件定義・技術仕様策定
- [ ] Phase 0: 環境セットアップ (Week 1)
- [ ] Phase 1: ユーザー認証 (Week 2)
- [ ] Phase 2: デッキ管理 (Week 3)
- [ ] Phase 3: カード管理 (Week 4-5)
- [ ] Phase 4: FSRS v4実装 (Week 5-6)
- [ ] Phase 5: 学習機能 (Week 6-7)
- [ ] Phase 6: ダッシュボード (Week 8)
- [ ] Phase 7: テスト・デバッグ (Week 9)
- [ ] Phase 8: リリース (Week 10)

詳細は [MVP_ROADMAP.md](MVP_ROADMAP.md) を参照してください。

### 将来の機能 (Phase 2+)
- タグ機能
- カードのインポート/エクスポート
- 学習統計グラフ
- 穴埋め（Cloze）カード
- 音声添付
- デッキ共有

## ドキュメント

- [REQUIREMENTS.md](REQUIREMENTS.md) - 要件定義書
- [TECHNICAL_SPEC.md](TECHNICAL_SPEC.md) - 技術仕様書
- [MVP_ROADMAP.md](MVP_ROADMAP.md) - 開発ロードマップ

## テスト

```bash
# すべてのテストを実行
pytest

# カバレッジ付きで実行
pytest --cov=apps

# 特定のアプリのテストのみ実行
pytest apps/study/tests/
```

## コントリビューション

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 参考資料

- [FSRS Algorithm](https://github.com/open-spaced-repetition/fsrs4anki/wiki) - FSRS v4アルゴリズムの詳細
- [Django Documentation](https://docs.djangoproject.com/) - Django公式ドキュメント
- [Anki](https://apps.ankiweb.net/) - オリジナルのAnkiアプリケーション
- [SuperMemo](https://www.supermemo.com/) - 間隔反復学習の元祖

## お問い合わせ

質問や提案がある場合は、Issueを作成してください。

---

**開発状況**: MVP開発中 🚧

**バージョン**: 0.1.0-alpha
