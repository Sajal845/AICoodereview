@echo off
title AI Code Reviewer Server Manager
color 0A
echo ========================================================
echo   AI Code Review & Bug Detection Platform Launcher
echo ========================================================
echo.

echo Step 1: Checking Python...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python is NOT installed or not in PATH!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Step 2: Checking Node.js...
node --version
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is NOT installed or not in PATH!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo Step 3: Installing Backend Dependencies...
cd /d "%~dp0backend"
pip install -r requirements.txt

echo.
echo Step 4: Installing Frontend Dependencies...
cd /d "%~dp0frontend"
call npm install

echo.
echo ========================================================
echo   STARTING SERVERS NOW...
echo ========================================================
start "Backend - FastAPI" cmd /k "cd /d "%~dp0backend" && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
start "Frontend - Vite React" cmd /k "cd /d "%~dp0frontend" && npm run dev -- --host 127.0.0.1 --port 3000"

echo.
echo Done! Open your browser at:
echo   http://127.0.0.1:3000
echo   http://127.0.0.1:8000/docs
echo.
pause
