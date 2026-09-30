@echo off
echo =======================================================
echo   Starting AI Code Review & Bug Detection Platform ⭐
echo =======================================================
echo.

start "AI Code Reviewer - Backend" cmd /c "%~dp0run_backend.bat"
start "AI Code Reviewer - Frontend" cmd /c "%~dp0run_frontend.bat"

echo Both launchers triggered in separate windows!
echo - Backend URL: http://127.0.0.1:8000
echo - Frontend URL: http://localhost:3000
echo.
pause
