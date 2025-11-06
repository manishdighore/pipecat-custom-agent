@echo off
echo ========================================
echo Pipecat Voice Agent Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)
echo.

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo [3/4] Installing dependencies...
pip install -r requirements.txt
echo.

echo [4/4] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo.
    echo ========================================
    echo IMPORTANT: Edit .env file and add your Azure credentials:
    echo - AZURE_SPEECH_API_KEY
    echo - AZURE_SPEECH_REGION
    echo ========================================
) else (
    echo .env file already exists.
)
echo.

echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your Azure credentials
echo 2. Run: python main.py
echo 3. Open browser to: http://localhost:8000/client
echo.
pause
