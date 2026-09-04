@echo off
echo ==========================================
echo Starting CallSense AI Full-Stack App...
echo ==========================================

echo [1/2] Starting FastAPI Backend on port 8000...
start "CallSense Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn main:app --reload"

echo [2/2] Starting React Frontend on port 3000...
start "CallSense Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are launching in separate windows!
echo Once they start, open http://localhost:3000 in your browser.
echo.
