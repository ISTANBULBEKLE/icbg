#!/bin/bash

# Function to kill processes on exit
cleanup() {
    echo ""
    echo "Stopping processes..."
    if [ -n "$BACKEND_PID" ]; then
        echo "Killing Backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ -n "$FRONTEND_PID" ]; then
        echo "Killing Frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null
    fi
    # Also try to kill any lingering uvicorn/next processes started by this script
    pkill -P $$
    exit
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM EXIT

echo "Starting Backend..."
cd backend
source venv/bin/activate
# Start uvicorn in background
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

echo "Starting Frontend..."
cd frontend
# Start next dev in background
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"

echo "Application started. Press Ctrl+C to stop."

# Wait for any process to exit
wait
