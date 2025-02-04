@echo off
setlocal

REM Activate the virtual environment
call venv\Scripts\activate

REM Run the Python application
python src\collections_app.py

REM Capture the exit code of the Python application
set "EXIT_CODE=%ERRORLEVEL%"

REM Deactivate the virtual environment
call deactivate

REM Display the exit code
echo Python application exited with code %EXIT_CODE%.

REM Prompt the user to press Enter to continue
echo Press ENTER to continue...
pause >nul

endlocal
