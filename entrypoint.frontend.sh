#!/bin/bash
set -e

echo "Waiting for backend to be ready..."

# Wait for backend to be ready
until curl -s http://backend:8000/ > /dev/null 2>&1; do
    echo "Backend is unavailable - sleeping"
    sleep 5
done

echo "Backend is ready!"

echo "Starting frontend server..."
exec streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0

