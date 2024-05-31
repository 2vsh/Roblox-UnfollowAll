@echo off
:: Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python before running this script.
    pause
    exit /b
)

:: Upgrade pip
python -m pip install --upgrade pip

:: Install required packages
pip install -r requirements.txt

echo Requirements have been installed.
pause
