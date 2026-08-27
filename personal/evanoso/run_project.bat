@echo off
echo ========================================================
echo   ESPADA Banking System - Launching Evanoso Application
echo ========================================================
echo.

REM 1. Check if MySQL is running
echo [*] Checking MySQL service...
powershell -Command "if (-not (Test-NetConnection -ComputerName 127.0.0.1 -Port 3306 -InformationLevel Quiet)) { Write-Host '[*] Starting MySQL daemon...'; Start-Process 'C:\xampp\mysql\bin\mysqld.exe' -ArgumentList '--standalone' -WindowStyle Hidden; Start-Sleep -Seconds 3 }"

REM 2. Start Backend Server
echo [*] Starting FastAPI Backend on http://127.0.0.1:5002 ...
start "Evanoso Banking API (FastAPI)" cmd /k "cd /d %~dp0appserver && python -m uvicorn app.main:app --host 127.0.0.1 --port 5002 --reload"

REM 3. Start Frontend Client
echo [*] Starting Vite Frontend on http://127.0.0.1:9005 ...
start "Evanoso Banking Frontend (Vite/Quasar)" cmd /k "cd /d %~dp0appclient && npm run dev -- --host 127.0.0.1 --port 9005"

echo.
echo ========================================================
echo   Application Started!
echo   - Web App URL:      http://127.0.0.1:9005
echo   - API Swagger Docs: http://127.0.0.1:5002/docs
echo   - Test Accounts (Password: Password123!):
echo       * Admin:    admin
echo       * Staff:    staff
echo       * Customer: customer
echo ========================================================
