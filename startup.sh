#!/bin/bash

# Navigate to the app directory
cd /home/site/wwwroot

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput 2>/dev/null || true

# Run migrations
python manage.py migrate

# Start Gunicorn
gunicorn --workers 4 --worker-class sync --bind 0.0.0.0:8000 core.wsgi:application
