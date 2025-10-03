#!/bin/bash
echo "Stopping all services..."
pkill -f "uvicorn main:app"
pkill -f "npm run dev"
echo "All services stopped"
