@echo off
echo Setting up WinTweaks...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.10+.
    pause
    exit /b 1
)
python -m pip install --upgrade pip
echo Setup complete.
pause