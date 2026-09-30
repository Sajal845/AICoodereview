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

echo.
echo Step 2: Adding all source code files...
git add .

echo.
echo Step 3: Creating initial commit...
git commit -m "Initial commit: AI Code Review & Bug Detection Platform ⭐"

echo.
echo ========================================================
echo Git repository initialized and committed locally!
echo.
echo Next Steps to publish to GitHub:
echo 1. Go to https://github.com/new and create a new repository
echo    (e.g., named 'ai-code-reviewer')
echo 2. Copy the two commands shown by GitHub and run them:
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/ai-code-reviewer.git
echo    git push -u origin main
echo ========================================================
pause
