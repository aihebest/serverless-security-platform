@echo off
SETLOCAL

:: Check if Python is accessible
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found in PATH
    echo Adding Python to PATH...
    set "PATH=%PATH%;C:\Users\admin\AppData\Local\Programs\Python\Python39;C:\Users\admin\AppData\Local\Programs\Python\Python39\Scripts"
)

:: Remove existing venv if it exists
if exist .venv (
    echo Removing existing virtual environment...
    rmdir /s /q .venv
)

:: Create new virtual environment
echo Creating new virtual environment...
"C:\Users\admin\AppData\Local\Programs\Python\Python39\python.exe" -m venv .venv

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

:: Upgrade pip and install basic tools
echo Upgrading pip and installing basic tools...
python -m pip install --upgrade pip setuptools wheel

:: Install requirements
echo Installing base requirements...
pip install -r requirements/base.txt

echo Installing development requirements...
pip install -r requirements/dev.txt

echo Environment setup complete!
echo To activate the virtual environment, use:
echo     .venv\Scripts\activate.bat

ENDLOCAL