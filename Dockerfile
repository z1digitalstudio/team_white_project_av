# ========================================
# STAGE 1: BUILDER (discarded after)
# ========================================
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

# ========================================
# STAGE 2: RUNTIME (final image)
# ========================================
FROM python:3.12-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=ProyectoAlvaroValero.settings \
    PORT=8000

WORKDIR /app

# Install runtime dependencies (solo librerías, no headers ni dev)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    libpng16-16 \
    libfreetype6 \
    libpq5 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (simplificado)
RUN groupadd -r django && useradd -r -g django django

# Copy Python dependencies from builder
COPY --from=builder /root/.local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /root/.local/bin /usr/local/bin

# Copy application code
COPY --chown=django:django . .
RUN chmod -R 755 /app

# Switch to non-root user
USER django

EXPOSE 8000

# Command - Run migrations and then start server
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && python init_superuser.py && echo 'Starting waitress...' && waitress-serve --host=0.0.0.0 --port=${PORT:-8000} ProyectoAlvaroValero.wsgi:application"]