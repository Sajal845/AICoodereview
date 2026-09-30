@echo off
title Push Project to GitHub
color 0B
echo ========================================================
echo   Pushing AI Code Reviewer Project to GitHub
echo ========================================================
echo.

cd /d "%~dp0"

echo Step 1: Initializing Git repository...
git init
git branch -M main

echo.
echo Step 2: Adding all project source files...
git add .

echo.
echo Step 3: Creating commit...
git commit -m "Initial commit: AI Code Review & Bug Detection Platform ⭐"

echo.
echo ========================================================
echo Please enter your GitHub Repository URL below.
echo Example: https://github.com/YourUsername/ai-code-reviewer.git
echo ========================================================
echo.

set /p REPO_URL="Paste your GitHub Repo URL here: "

if "%REPO_URL%"=="" (
    echo Error: No URL entered. Please run again when you have created your repo at https://github.com/new
    pause
    exit /b 1
)

echo.
echo Linking remote origin...
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%

echo.
echo Pushing code to GitHub...
git push -u origin main

echo.
echo ========================================================
echo SUCCESS! Your code has been pushed to GitHub!
echo ========================================================
pause
