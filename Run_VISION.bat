@echo off
title VISION AI - Initializing...
color 0b
cls
echo.
echo    =============================================
echo       VISION AI - OFFLINE INTELLIGENCE SYSTEM
echo    =============================================
echo.
echo    [+] Ghost Mode Active...
echo    [+] Check System Tray if window closes...
echo.

:: Set current directory
cd /d "%~dp0"

:: Run Python script using virtual environment
C:\Users\hr_894\Projects\.venv\Scripts\python.exe vision_ai.py

:: Pause only if error
if %ERRORLEVEL% NEQ 0 pause