#!/bin/bash

# Azure App Service startup script for Django

# Navigate to app directory
cd /home/site/wwwroot

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start Gunicorn
gunicorn --workers 4 --worker-class sync --bind 0.0.0.0:8000 soil_soul_project.wsgi:application
