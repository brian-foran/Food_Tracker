@echo off
echo Starting Food App Server...
echo.
cd /d "%~dp0"

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the server
python server.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Error occurred! Press any key to exit...
    pause >nul
)
