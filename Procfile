release: ENVIRONMENT=production python manage.py migrate --noinput
web: ENVIRONMENT=production python manage.py migrate && gunicorn --workers 3 --worker-class sync --bind 0.0.0.0:$PORT --timeout 120 --max-requests 1000 --max-requests-jitter 100 core.wsgi:application
