# Use official Python runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=core.settings

# Set work directory
WORKDIR /app

# Install system dependencies for PostgreSQL client
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from parent directory and install
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Export environment variables from .env file at container startup
# Create entrypoint script that loads .env if it exists
RUN echo '#!/bin/bash\n\
set -a\n\
[ -f .env ] && . ./.env\n\
set +a\n\
exec "$@"' > /entrypoint.sh && \
chmod +x /entrypoint.sh

# Collect static files (ignore errors if STATIC_ROOT not configured)
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Set entrypoint to load environment variables
ENTRYPOINT ["/entrypoint.sh"]

# Run migrations and start Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn --workers 4 --worker-class sync --bind 0.0.0.0:$PORT --timeout 60 core.wsgi:application"]
