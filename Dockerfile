FROM python:3.12-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=ProyectoAlvaroValero.settings \
    PORT=8000

WORKDIR /app

# Install system dependencies 
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    libpq-dev \
    libjpeg62-turbo \
    libpng16-16 \
    libfreetype6 \
    libpq5 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN groupadd -r django && useradd -r -g django django

# Copy application code
COPY --chown=django:django . .
RUN chmod -R 755 /app

# Switch to non-root user
USER django

EXPOSE 8000

# Command - Run migrations and then start server
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && python init_superuser.py && waitress-serve --host=0.0.0.0 --port=${PORT:-8000} ProyectoAlvaroValero.wsgi:application"]