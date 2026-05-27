# PayFlow Gateway - Start Both Backend & Frontend
# Run this script from the "next gateway" root directory

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "    PayFlow Gateway - Starting Services     " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Start Backend (FastAPI on port 8000)
Write-Host "[1/2] Starting Backend (port 8000)..." -ForegroundColor Yellow
$backendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; .\venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000" -PassThru
Write-Host "  Backend PID: $($backendJob.Id)" -ForegroundColor Green

Start-Sleep -Seconds 3

# Start Frontend (Next.js on port 3000)
Write-Host "[2/2] Starting Frontend (port 3000)..." -ForegroundColor Yellow
$frontendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev" -PassThru
Write-Host "  Frontend PID: $($frontendJob.Id)" -ForegroundColor Green

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  All services started successfully!        " -ForegroundColor Green
Write-Host "  Backend:  http://127.0.0.1:8000            " -ForegroundColor White
Write-Host "  Frontend: http://localhost:3000            " -ForegroundColor White
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
