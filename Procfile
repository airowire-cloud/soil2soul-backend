web: python manage.py migrate && gunicorn --workers 4 --worker-class sync --bind 0.0.0.0:$PORT --timeout 60 core.wsgi:application
