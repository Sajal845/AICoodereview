@echo off
echo ===================================================
echo  AI Code Review Platform - Frontend Launcher
echo ===================================================
cd /d %~dp0frontend
echo Checking Node/npm installation...
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js / npm is not installed or not in PATH! Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo Installing frontend npm packages...
call npm install
if %errorlevel% neq 0 (
    echo [WARNING] npm install had an issue, attempting startup anyway...
)

echo Starting Vite Dev Server...
call npm run dev
pause
