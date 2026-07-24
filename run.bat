@echo off
title MuleNet AI - Platform Launcher
echo ===================================================
echo           MULENET AI ENTERPRISE LAUNCHER
echo ===================================================
echo.

echo [1/5] Installing Python ML dependencies...
cd backend
call ..\\.venv\\Scripts\\pip.exe install -r requirements.txt --quiet
if errorlevel 1 (
    pip install -r requirements.txt --quiet
)
cd ..
echo      Dependencies ready.
echo.

echo [2/5] Checking for trained ML model...
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

echo [3/5] Starting FastAPI Python Backend Engine...
start "MuleNet AI Backend" cmd /k "cd /d %~dp0backend && python main.py"

echo [4/5] Starting Vite React Frontend Dev Server...
start "MuleNet AI Frontend" cmd /k "cd /d %~dp0 && npm run dev -- --port 5463"

echo [5/5] Waiting for servers to initialize...
timeout /t 5 /nobreak >nul

echo Launching MuleNet AI in default web browser...
start http://localhost:5463

echo.
echo ===================================================
echo  System Online at http://localhost:5463
echo  Backend API at  http://localhost:8000
echo  Model status:   http://localhost:8000/api/model/status
echo  Keep the spawned command windows open.
echo ===================================================
echo.
pause
