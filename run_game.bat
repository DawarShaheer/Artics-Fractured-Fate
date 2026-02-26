@echo off
title Kael Arctis: The Unraveling
echo Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in your PATH. 
    echo Please install Python 3 from python.org to play.
    pause
    exit /b
)

echo Starting Kael Arctis...
python main.py
pause
