@echo off
title CodeSentinel AI Server
color 0B
echo ========================================================
echo   Starting CodeSentinel AI Web Platform ⭐
echo ========================================================
echo.

cd /d "%~dp0"
python standalone_server.py
if %errorlevel% neq 0 (
    py standalone_server.py
)
pause
