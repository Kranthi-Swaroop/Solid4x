#!/bin/bash
echo "Starting Solid4x System..."

# Start Backend
cd backend && python -m uvicorn app.main:app --reload --port 8000 &

# Start Frontend
cd ../frontend && npm run dev &

echo "System is starting up."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
wait
