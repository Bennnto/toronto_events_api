#!/bin/bash
set -e

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Start the application based on the CMD passed from fly.toml
echo "Starting application..."
exec "$@"
