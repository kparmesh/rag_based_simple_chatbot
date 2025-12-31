#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."

# Wait for PostgreSQL to be ready using timeout and connection attempt
until python -c "import psycopg2; psycopg2.connect(host='db', port=5432, user='postgres', password='pass', dbname='rag_chatbot')" 2>/dev/null; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done

echo "PostgreSQL is ready!"

# Run database migrations
echo "Running database migrations..."
cd /app
python -c "from backend.db.session import init_db; init_db()"

echo "Starting backend server..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

