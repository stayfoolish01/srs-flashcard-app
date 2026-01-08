# セットアップガイド

このドキュメントでは、SRS Flashcard Appの開発環境をセットアップする手順を説明します。

## 前提条件

以下のソフトウェアがインストールされている必要があります：

- **Python 3.11以上** - [公式サイト](https://www.python.org/downloads/)からダウンロード
- **Node.js 18以上** - [公式サイト](https://nodejs.org/)からダウンロード（Tailwind CSS用）
- **Git** - バージョン管理用

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/stayfoolish01/srs-flashcard-app.git
cd srs-flashcard-app
```

### 2. Python仮想環境の作成

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

仮想環境がアクティブになると、プロンプトに `(venv)` が表示されます。

### 3. Pythonパッケージのインストール

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Node.jsパッケージのインストール（Tailwind CSS用）

```bash
npm install
```

### 5. 環境変数の設定

`.env.example`をコピーして`.env`ファイルを作成します：

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

`.env`ファイルを開いて、`SECRET_KEY`を変更してください：

```bash
# Djangoのシークレットキーを生成
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

生成されたキーを`.env`ファイルの`SECRET_KEY`に設定します。

### 6. Djangoプロジェクトの初期化

#### データベースのマイグレーション

```bash
python manage.py migrate
```

#### スーパーユーザーの作成

```bash
python manage.py createsuperuser
```

プロンプトに従って、ユーザー名、メールアドレス、パスワードを入力してください。

#### 静的ファイルの収集

```bash
python manage.py collectstatic --noinput
```

### 7. Tailwind CSSのビルド

開発中は、別のターミナルでTailwind CSSのwatchモードを起動します：

```bash
npm run watch:css
```

これにより、HTMLやテンプレートファイルの変更を監視し、自動的にCSSを再ビルドします。

本番用にビルドする場合：

```bash
npm run build:css
```

### 8. 開発サーバーの起動

```bash
python manage.py runserver
```

ブラウザで http://127.0.0.1:8000 にアクセスしてください。

## ディレクトリ構成

セットアップ後のディレクトリ構造：

```
srs-flashcard-app/
├── venv/                     # Python仮想環境（gitignore済み）
├── node_modules/             # Node.jsパッケージ（gitignore済み）
├── config/                   # Djangoプロジェクト設定
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/                     # Djangoアプリケーション
│   ├── accounts/
│   ├── decks/
│   ├── cards/
│   ├── study/
│   └── dashboard/
├── static/                   # 静的ファイル
│   ├── src/
│   │   └── input.css        # Tailwind CSS入力ファイル
│   ├── css/
│   │   └── styles.css       # ビルド済みCSS
│   └── js/
├── media/                    # ユーザーアップロード（gitignore済み）
├── templates/                # 共通テンプレート
│   └── base.html
├── db.sqlite3                # データベース（gitignore済み）
├── manage.py
├── requirements.txt
├── package.json
└── tailwind.config.js
```

## 開発ワークフロー

### 通常の開発作業

1. **仮想環境の有効化**
   ```bash
   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

2. **Tailwind CSSのwatchモード起動**（別ターミナル）
   ```bash
   npm run watch:css
   ```

3. **開発サーバー起動**
   ```bash
   python manage.py runserver
   ```

4. **コード編集** - お好みのエディタで編集

5. **ブラウザで確認** - http://127.0.0.1:8000

### マイグレーションの作成と適用

モデルを変更した場合：

```bash
# マイグレーションファイルの作成
python manage.py makemigrations

# マイグレーションの適用
python manage.py migrate
```

### テストの実行

```bash
# すべてのテスト実行
pytest

# カバレッジ付き
pytest --cov=apps

# 特定のアプリのテスト
pytest apps/study/tests/
```

### コード品質チェック

```bash
# フォーマット
black .

# インポートソート
isort .

# リント
flake8
```

## トラブルシューティング

### Python仮想環境が作成できない

**エラー**: `python -m venv venv` が失敗する

**解決策**:
- Python 3.11以上がインストールされているか確認
- Windowsの場合、`py -3.11 -m venv venv`を試す

### pipのインストールが失敗する

**エラー**: `pip install -r requirements.txt` でエラー

**解決策**:
```bash
# pipをアップグレード
pip install --upgrade pip

# キャッシュをクリア
pip cache purge

# 再試行
pip install -r requirements.txt
```

### Tailwind CSSがビルドされない

**エラー**: `npm run watch:css` が動作しない

**解決策**:
```bash
# node_modulesを削除して再インストール
rm -rf node_modules package-lock.json  # macOS/Linux
# または
rmdir /s node_modules && del package-lock.json  # Windows

npm install
```

### データベースマイグレーションエラー

**エラー**: `python manage.py migrate` でエラー

**解決策**:
```bash
# データベースをリセット（開発環境のみ）
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### ポート8000が既に使用中

**エラー**: `That port is already in use.`

**解決策**:
```bash
# 別のポートで起動
python manage.py runserver 8001

# または、既存のプロセスを終了
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

## 次のステップ

セットアップが完了したら：

1. [REQUIREMENTS.md](REQUIREMENTS.md)で要件を確認
2. [TECHNICAL_SPEC.md](TECHNICAL_SPEC.md)で技術仕様を理解
3. [MVP_ROADMAP.md](MVP_ROADMAP.md)で開発計画を確認
4. [GitHub Issues](https://github.com/stayfoolish01/srs-flashcard-app/issues)でタスクを確認

## ヘルプ

問題が解決しない場合は、[GitHub Issues](https://github.com/stayfoolish01/srs-flashcard-app/issues)で質問してください。
