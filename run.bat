@echo off
title MuleNet AI - Platform Launcher
echo ===================================================
echo           MULENET AI ENTERPRISE LAUNCHER
echo ===================================================
echo.

echo [1/6] Setting up Python Environment...
if not exist ".venv\Scripts\activate.bat" (
    echo      Creating virtual environment...
    python -m venv .venv
)
call .venv\Scripts\activate.bat

echo [2/6] Installing Python ML dependencies...
cd backend
pip install -r requirements.txt --quiet
cd ..
echo      Backend dependencies ready.
echo.

echo [3/6] Installing Frontend Node dependencies...
if not exist "node_modules\" (
    echo      Running npm install...
    call npm install
) else (
    echo      node_modules found. Skipping full install.
)
echo      Frontend dependencies ready.
echo.

echo [4/6] Checking for trained ML model...
if not exist "backend\models\best_version.txt" (
    echo      No model found. Running first-time training pipeline...
    echo      This may take 3-8 minutes. Please wait...
    cd backend
    python -m ml.training_pipeline --skip-hpo
    cd ..
    echo      Training complete.
) else (
    echo      Trained model found. Skipping training.
)
echo.

echo [5/6] Starting FastAPI Python Backend Engine...
start "MuleNet AI Backend" cmd /k "cd /d %~dp0backend && call ..\.venv\Scripts\activate.bat && python main.py"

echo [6/6] Starting Vite React Frontend Dev Server...
start "MuleNet AI Frontend" cmd /k "cd /d %~dp0 && npm run dev -- --port 5463"

echo Waiting for servers to initialize...
timeout /t 5 /nobreak >nul

echo Launching MuleNet AI in default web browser...
start http://localhost:5463

echo.
echo ===================================================
echo  System Online at http://localhost:5463
echo  Backend API at  http://127.0.0.1:8000
echo  Model status:   http://127.0.0.1:8000/api/model/status
echo  Keep the spawned command windows open.
echo ===================================================
echo.
pause
