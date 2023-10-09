@echo off
pushd %~dp0
REM Set the path to the virtual environment's Python executable
set VENV_DIR=%~dp0\venv
set PYTHON_EXECUTABLE=%VENV_DIR%\Scripts\python.exe

REM Check if the virtual environment exists
if not exist "%VENV_DIR%" (
    echo Virtual environment not found in %VENV_DIR%
    exit /b 1
)

REM Activate the virtual environment
call "%VENV_DIR%\Scripts\activate"

REM Run main.py from the current directory
"%PYTHON_EXECUTABLE%" main.py
pause