@echo off
title Aisha — Mumzworld AI Copilot
color 0A

echo.
echo  ================================================
echo   Aisha — Universal AI Shopping Copilot
echo   Mumzworld Prototype
echo  ================================================
echo.

REM Check if Ollama is installed
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Ollama is not installed or not in PATH.
    echo  Please install it from: https://ollama.com
    echo.
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python is not installed or not in PATH.
    echo  Please install it from: https://python.org
    echo.
    pause
    exit /b 1
)

echo  [1/4] Installing Python dependencies...
pip install -r requirements.txt --quiet
echo       Done.
echo.

echo  [2/4] Pulling Phi-3 model (skipped if already downloaded)...
ollama pull phi3
echo       Done.
echo.

echo  [3/4] Starting Ollama server in the background...
start "Ollama Server" /min ollama serve
timeout /t 3 /nobreak >nul
echo       Ollama is running at http://localhost:11434
echo.

echo  [4/4] Starting Aisha Flask app...
echo       Open your browser at: http://localhost:5000
echo.
echo  ================================================
echo   Press Ctrl+C in this window to stop the app.
echo  ================================================
echo.

python app.py
pause
