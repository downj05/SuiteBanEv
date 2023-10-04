@echo off

:: Store the current working directory
set "CURRENT_DIR=%CD%"

:: Change the directory to where main.py is located
cd /d "SuitBanEv"

:: Activate the virtual environment
call "venv\Scripts\activate"

:: Run main.py with any provided arguments
python "main.py" %*

:: Deactivate the virtual environment
call deactivate

:: Change back to the original directory
cd /d "%CURRENT_DIR%"

:: Exit the batch script
exit /b 0
