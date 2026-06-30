@echo off
REM Better Agent - Windows launcher (the macOS counterpart is run.sh).
REM Binds 127.0.0.1 only; serves the prebuilt frontend/dist from :8000.
REM Path-independent: derives its own location, so the repo can live
REM anywhere. Open the desktop shortcut that points here.
title Better Agent

set "ROOT=%~dp0"
cd /d "%ROOT%backend"

:: ── Kill any previous instance on port 8000 ──────────────────────────
echo Stopping previous instance on port 8000...
for /f "tokens=5" %%P in ('netstat -ano 2^>nul ^| findstr /R "TCP.*:8000.*LISTENING"') do (
    taskkill /F /PID %%P >nul 2>&1
)
timeout /t 2 /nobreak >nul

:: ── Start backend ─────────────────────────────────────────────────────
echo Starting Better Agent backend on http://127.0.0.1:8000 ...
start "Better Agent Backend" /B ".venv\Scripts\uvicorn.exe" main:app --host 127.0.0.1 --port 8000

:: ── Wait for backend to be ready (poll /health up to 30s) ─────────────
echo Waiting for backend...
set /a tries=0
:wait_loop
timeout /t 1 /nobreak >nul
set /a tries+=1
curl -sf http://127.0.0.1:8000/health >nul 2>&1
if %errorlevel%==0 goto ready
if %tries% lss 30 goto wait_loop
echo Warning: backend did not respond within 30s, opening browser anyway.
goto open_browser

:ready
echo Backend is ready.

:open_browser
echo Opening browser...
start "" "http://127.0.0.1:8000"

:: ── Keep window open so logs are visible ─────────────────────────────
echo.
echo Better Agent is running. Press any key to stop.
pause >nul
taskkill /F /FI "WINDOWTITLE eq Better Agent Backend" >nul 2>&1
