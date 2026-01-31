#!/usr/bin/env bash
set -e
set -x

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec uvicorn --reload app.main:app --host 0.0.0.0 --port 8000

# COMMENT ABOVE AND UNCOMMENT BELOW FOR DEPLOYMENT
# exec fastapi run --workers 4 app/main.py
