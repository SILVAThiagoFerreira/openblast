@echo off
REM Sobe o webapp do REPORT SISMOGRAFIA em http://127.0.0.1:5057
cd /d "%~dp0"
python -m webapp.server %*
