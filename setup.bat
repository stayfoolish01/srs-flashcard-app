@echo off
chcp 65001 >nul
echo ========================================
echo SRS Flashcard App - Auto Setup
echo ========================================
echo.

REM Check Python version
echo [1/8] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed.
    echo.
    echo Please install Python 3.13 or higher:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
python --version
echo.

REM Create virtual environment
echo [2/8] Creating Python virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping.
) else (
    python -m venv venv
    echo Virtual environment created.
)
echo.

REM Activate virtual environment
echo [3/8] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Upgrade pip
echo [4/8] Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo [5/8] Installing Python dependencies...
pip install -r requirements.txt
echo.

REM Create .env file
echo [6/8] Creating environment file...
if exist .env (
    echo .env file already exists. Skipping.
) else (
    copy .env.example .env
    echo .env file created.
    echo.
    echo IMPORTANT: Please change SECRET_KEY in .env file!
    echo Run this command to generate a random key:
    echo python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
)
echo.

REM Check Node.js and install packages
echo [7/8] Installing Node.js packages...
where node >nul 2>&1
if errorlevel 1 (
    echo WARNING: Node.js is not installed.
    echo Node.js 18+ is required for Tailwind CSS.
    echo https://nodejs.org/
    echo.
    echo Skipping...
) else (
    node --version
    if exist node_modules (
        echo node_modules already exists. Skipping.
    ) else (
        call npm install
    )
)
echo.

REM Done
echo [8/8] Setup complete!
echo.
echo ========================================
echo Next steps:
echo ========================================
echo.
echo 1. Change SECRET_KEY in .env file
echo.
echo 2. Initialize Django project:
echo    django-admin startproject config .
echo.
echo 3. Run database migration:
echo    python manage.py migrate
echo.
echo 4. Create superuser:
echo    python manage.py createsuperuser
echo.
echo 5. Start development server:
echo    python manage.py runserver
echo.
echo 6. Build Tailwind CSS (in another terminal):
echo    npm run watch:css
echo.
echo ========================================
echo.
pause