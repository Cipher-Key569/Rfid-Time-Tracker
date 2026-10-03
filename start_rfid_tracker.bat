@echo off
cd /d C:\Users\Keyona\rfid_time_tracker

echo ========================================
echo       RFID TIME TRACKER
echo ========================================
echo Starting dashboard...
echo Starting RFID listener...
echo ========================================

start "RFID Dashboard" cmd /k "py -3.14 -m uvicorn dashboard:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

start "RFID Listener" cmd /k "py -3.14 rfid_listener.py"

echo.
echo RFID Time Tracker started.
echo Dashboard: http://127.0.0.1:8000
echo.