@echo off

REM Activate the virtual environment
set /p="Activating virtual environment ..." <nul
call venv\Scripts\activate.bat
echo OK

echo Virtual environment activated
echo Launching application...

REM Run the Python app

python SynologyLLM.py %*
set app_result=%errorlevel%

pause >nul

exit /b 0
