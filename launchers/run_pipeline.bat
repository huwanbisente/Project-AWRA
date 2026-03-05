@echo off
:: Get the directory where this script is located
cd /d "%~dp0"

:: Activate the virtual environment
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment not found at .venv\Scripts\activate.bat
    pause
    exit /b 1
)

:: Run the pipeline script
python run_pipeline.py

:: Deactivate (optional, but good practice if running in a shared shell, 
:: though script usually ends here)
if exist .venv\Scripts\deactivate.bat (
    call .venv\Scripts\deactivate.bat
)
