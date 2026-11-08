#!/usr/bin/env bash
set -e

echo "==================================================="
echo "Setting up BusinessPulse AI (Full Stack)"
echo "==================================================="

cd backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Starting Backend server in background..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ../frontend
echo "Installing Node frontend dependencies..."
npm install
echo "Starting Frontend Development Server..."
npm run dev

kill $BACKEND_PID
