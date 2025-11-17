@echo off
REM Windows Setup Script for Reddit Automation System
REM Run this script to perform initial setup

echo ================================================================================
echo REDDIT AUTOMATION SYSTEM - WINDOWS SETUP
echo ================================================================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.9+ from python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
echo [OK] Python found
python --version
echo.

REM Check pip installation
echo Checking pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip not found! Reinstall Python with pip included
    pause
    exit /b 1
)
echo [OK] pip found
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo [SKIP] Virtual environment already exists
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo [OK] pip upgraded
echo.

REM Install dependencies
echo Installing dependencies (this may take a few minutes)...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo Try running: pip install -r requirements.txt manually
    pause
    exit /b 1
)
echo [OK] All dependencies installed
echo.

REM Check Tesseract OCR
echo Checking Tesseract OCR...
tesseract --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Tesseract OCR not found!
    echo.
    echo Tesseract is required for OSK calibration.
    echo.
    echo Download from: https://github.com/UB-Mannheim/tesseract/wiki
    echo Install to: C:\Program Files\Tesseract-OCR
    echo Add to PATH: C:\Program Files\Tesseract-OCR
    echo.
    echo Continue anyway? (y/n^)
    set /p continue=
    if /i not "%continue%"=="y" exit /b 1
) else (
    echo [OK] Tesseract OCR found
    tesseract --version
)
echo.

REM Create .env file if it doesn't exist
echo Setting up environment file...
if exist .env (
    echo [SKIP] .env already exists
) else (
    copy .env.example .env
    echo [OK] .env created from template
    echo.
    echo [ACTION REQUIRED] Edit .env file with your API keys:
    echo   - ANTHROPIC_API_KEY=your-api-key-here
    echo   - REDIS_PASSWORD=your-password
    echo.
    echo Opening .env in notepad...
    timeout /t 2 >nul
    notepad .env
)
echo.

REM Create directories
echo Creating required directories...
if not exist logs mkdir logs
if not exist screenshots mkdir screenshots
echo [OK] Directories created
echo.

REM Check Redis (optional)
echo Checking Redis server...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Redis not running or not installed
    echo.
    echo Redis is optional but recommended for state management.
    echo.
    echo Download from: https://github.com/tporadowski/redis/releases
    echo After installation, run: redis-server.exe
    echo.
) else (
    echo [OK] Redis is running
)
echo.

REM Summary
echo ================================================================================
echo SETUP COMPLETE!
echo ================================================================================
echo.
echo Next steps:
echo   1. Make sure you edited .env with your Anthropic API key
echo   2. Run calibration: python calibrate_osk.py
echo   3. Run tests: python manual_reddit_test.py
echo   4. Start automation: python main.py
echo.
echo ================================================================================
echo.

REM Ask to run calibration
echo Would you like to run OSK calibration now? (y/n^)
set /p run_calibration=
if /i "%run_calibration%"=="y" (
    echo.
    echo Starting OSK calibration...
    python calibrate_osk.py
)

echo.
echo Setup script complete!
pause
