@echo off
echo ===================================================
echo Setting up BusinessPulse AI (Full Stack)
echo ===================================================

cd backend
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)
echo Activating virtual environment...
call venv\Scripts\activate
echo Installing Python backend dependencies...
pip install -r requirements.txt

echo Starting Backend Server in background...
start cmd /k "venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

cd ..\frontend
echo Installing Node frontend dependencies...
call npm install
echo Starting Frontend Development Server...
npm run dev
