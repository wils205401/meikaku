#!/bin/bash
echo "Setting up Meikaku App..."

cd backend
echo "Setting up backend..."
uv sync

cd ../frontend
echo "Setting up frontend..."
npm install

cd ..
echo "Setup complete!"
echo "To start the backend, run 'uv run' in the backend directory."
echo "To start the frontend, run 'npx expo start' in the frontend directory."