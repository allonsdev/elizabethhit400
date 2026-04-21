#!/bin/bash

# --- CONFIG ---
PROJECT_DIR="$(dirname "$0")"  # assumes script is in your project root
PORT=8000
URL="http://localhost:$PORT"

# --- START DJANGO ---
cd "$PROJECT_DIR" || exit 1

echo "Starting Django on $URL ..."
python manage.py runserver $PORT &
DJANGO_PID=$!

# --- WAIT FOR SERVER TO BE READY ---
echo "Waiting for server..."
for i in {1..20}; do
  if curl -s "$URL" > /dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

# --- OPEN IN CHROME ---
echo "Opening in Chrome..."
open -a "Google Chrome" "$URL"

echo "Django is running (PID $DJANGO_PID). Press Ctrl+C to stop."

# --- KEEP SCRIPT ALIVE, KILL DJANGO ON EXIT ---
trap "echo 'Stopping Django...'; kill $DJANGO_PID" EXIT
wait $DJANGO_PID