@echo off
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
python main.py --input examples/input --config config.json
pause
