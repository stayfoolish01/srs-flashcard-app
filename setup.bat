@echo off
echo ========================================
echo SRS Flashcard App - 自動セットアップ
echo ========================================
echo.

REM Pythonのバージョン確認
echo [1/8] Pythonのバージョン確認中...
python --version >nul 2>&1
if errorlevel 1 (
    echo エラー: Pythonがインストールされていません。
    echo.
    echo Python 3.11以上をインストールしてください:
    echo https://www.python.org/downloads/
    echo.
    echo インストール時に「Add Python to PATH」にチェックを入れてください。
    pause
    exit /b 1
)
python --version
echo.

REM 仮想環境の作成
echo [2/8] Python仮想環境を作成中...
if exist venv (
    echo 仮想環境は既に存在します。スキップします。
) else (
    python -m venv venv
    echo 仮想環境を作成しました。
)
echo.

REM 仮想環境の有効化
echo [3/8] 仮想環境を有効化中...
call venv\Scripts\activate.bat
echo.

REM pipのアップグレード
echo [4/8] pipをアップグレード中...
python -m pip install --upgrade pip
echo.

REM 依存パッケージのインストール
echo [5/8] Python依存パッケージをインストール中...
pip install -r requirements.txt
echo.

REM .envファイルの作成
echo [6/8] 環境変数ファイルを作成中...
if exist .env (
    echo .envファイルは既に存在します。スキップします。
) else (
    copy .env.example .env
    echo .envファイルを作成しました。
    echo.
    echo 重要: .envファイルのSECRET_KEYを変更してください！
    echo 以下のコマンドでランダムなキーを生成できます:
    echo python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
)
echo.

REM Node.jsの確認とパッケージインストール
echo [7/8] Node.jsパッケージをインストール中...
where node >nul 2>&1
if errorlevel 1 (
    echo 警告: Node.jsがインストールされていません。
    echo Tailwind CSSを使用するにはNode.js 18以上が必要です。
    echo https://nodejs.org/
    echo.
    echo スキップして続行します...
) else (
    node --version
    if exist node_modules (
        echo node_modulesは既に存在します。スキップします。
    ) else (
        call npm install
    )
)
echo.

REM 完了メッセージ
echo [8/8] セットアップ完了！
echo.
echo ========================================
echo 次のステップ:
echo ========================================
echo.
echo 1. .envファイルのSECRET_KEYを変更してください
echo.
echo 2. Djangoプロジェクトを初期化:
echo    django-admin startproject config .
echo.
echo 3. データベースマイグレーション:
echo    python manage.py migrate
echo.
echo 4. スーパーユーザー作成:
echo    python manage.py createsuperuser
echo.
echo 5. 開発サーバー起動:
echo    python manage.py runserver
echo.
echo 6. Tailwind CSSビルド（別ターミナル）:
echo    npm run watch:css
echo.
echo ========================================
echo.
pause
