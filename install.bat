REM Create a venv and install the requirements
REM
REM Usage: install.bat
REM
python -m venv venv
venv\Scripts\pip install -r requirements.txt
echo "done"
pause