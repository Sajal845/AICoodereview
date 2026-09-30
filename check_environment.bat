@echo off
echo Running System Diagnostics for AI Code Reviewer Platform... > "%~dp0diagnostic.txt"
echo Date: %date% %time% >> "%~dp0diagnostic.txt"
echo. >> "%~dp0diagnostic.txt"

echo --- Checking Python --- >> "%~dp0diagnostic.txt"
python --version >> "%~dp0diagnostic.txt" 2>&1
if %errorlevel% neq 0 (
    echo Python check failed with error level %errorlevel% >> "%~dp0diagnostic.txt"
) else (
    echo Python check PASSED >> "%~dp0diagnostic.txt"
)

echo. >> "%~dp0diagnostic.txt"
echo --- Checking Node.js --- >> "%~dp0diagnostic.txt"
node --version >> "%~dp0diagnostic.txt" 2>&1
if %errorlevel% neq 0 (
    echo Node.js check failed with error level %errorlevel% >> "%~dp0diagnostic.txt"
) else (
    echo Node.js check PASSED >> "%~dp0diagnostic.txt"
)

echo. >> "%~dp0diagnostic.txt"
echo --- Checking npm --- >> "%~dp0diagnostic.txt"
call npm --version >> "%~dp0diagnostic.txt" 2>&1

echo Diagnostics completed. Output written to diagnostic.txt
