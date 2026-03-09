#!/bin/bash
set -e

# Detect app directory
if [ -d "/home/site/wwwroot" ]; then
    APP_DIR="/home/site/wwwroot"
elif [ -d "/app" ]; then
    APP_DIR="/app"
else
    APP_DIR="$(cd "$(dirname "$0")" && pwd)"
fi

cd "$APP_DIR"
echo "Running from: $APP_DIR"

# Detect python
if command -v python3 &>/dev/null; then
    PYTHON=python3
    PIP=pip3
elif command -v python &>/dev/null; then
    PYTHON=python
    PIP=pip
else
    echo "ERROR: Python not found!"
    exit 1
fi

echo "Using Python: $($PYTHON --version)"

# Install dependencies
$PIP install --upgrade pip
$PIP install -r requirements.txt

# Collect static files
$PYTHON manage.py collectstatic --noinput 2>/dev/null || true

# Run migrations
$PYTHON manage.py migrate --noinput

# Start Gunicorn
PORT=${PORT:-8000}
$PYTHON -m gunicorn --workers 3 --worker-class sync --bind 0.0.0.0:$PORT --timeout 120 core.wsgi:application
