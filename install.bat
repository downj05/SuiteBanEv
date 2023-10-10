@echo off
echo "creating new venv..."
python -m venv venv
echo "installing requirements..."
venv\Scripts\pip install -r requirements.txt
echo "setting version cache to latest..."
venv\Scripts\python.exe update.py --set
echo "done"
pause