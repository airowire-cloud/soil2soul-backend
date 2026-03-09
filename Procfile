release: ENVIRONMENT=production python manage.py migrate --noinput
web: ENVIRONMENT=production gunicorn --workers 2 --worker-class sync --bind 0.0.0.0:$PORT --timeout 120 --log-level debug core.wsgi:application
