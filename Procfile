release: ENVIRONMENT=production python manage.py migrate --noinput
web: gunicorn --workers 2 --bind 0.0.0.0:$PORT --timeout 120 core.wsgi:application
