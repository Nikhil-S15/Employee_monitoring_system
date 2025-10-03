#!/bin/bash
# Start backend in background
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Documentation: http://localhost:8000/docs"

# Handle script termination
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM
wait
