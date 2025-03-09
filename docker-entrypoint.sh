#!/bin/sh

# Wait for the database to be ready
echo "Waiting for database to start..."
sleep 5

# Run Alembic migrations
echo "Running migrations..."
alembic upgrade head

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
