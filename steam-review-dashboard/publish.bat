@echo off
cd /d "%~dp0"
python publish.py %* || py publish.py %*
pause
