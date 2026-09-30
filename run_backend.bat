@echo off
echo ===================================================
echo  AI Code Review Platform - Backend Launcher
echo ===================================================
cd /d %~dp0backend
echo Checking Python installation...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH! Please install Python 3.10+.
    pause
    exit /b 1
)

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] pip install had an issue, attempting startup anyway...
)

echo Starting FastAPI Uvicorn Server...
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
