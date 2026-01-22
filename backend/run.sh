#!/usr/bin/env bash
set -e
set -x

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec fastapi run --reload --workers 4 app/main.py

# COMMENT ABOVE AND UNCOMMENT BELOW FOR DEPLOYMENT
exec fastapi run --workers 4 app/main.py
