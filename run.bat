@echo off
echo Starting PayFlow Infrastructure...

if not exist "backend" (
    echo Error: backend directory not found.
    pause
    exit /b
)

if not exist "backend\venv" (
    echo Warning: backend virtual environment not found in backend\venv.
    echo Trying to start with system python...
    start cmd /k "cd backend && python -m uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000"
) else (
    start cmd /k "cd backend && .\venv\Scripts\python.exe -m uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000"
)

echo Backend starting on http://127.0.0.1:8000

echo Waiting for backend to initialize...
timeout /t 3 /nobreak > nul

if exist "frontend" (
    start cmd /k "cd frontend && npm run dev"
    echo Frontend starting on http://localhost:3000
) else (
    echo Error: frontend directory not found.
)

echo.
echo All systems are being initialized. Please wait a few seconds before refreshing your browser.
