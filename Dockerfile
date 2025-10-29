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
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --user -r requirements.txt

# ========================================
# STAGE 2: RUNTIME (final image)
# ========================================
FROM python:3.12-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=ProyectoAlvaroValero.settings

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    libpng16-16 \
    libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user FIRST
RUN groupadd -r django && useradd -r -g django -m -d /home/django django

# Copy Python dependencies from builder to system location
COPY --from=builder /root/.local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /root/.local/bin /usr/local/bin

# Copy application code
COPY --chown=django:django . .

# Set ownership and permissions
RUN chown -R django:django /app && \
    chmod -R 755 /app

# Switch to non-root user
USER django

# Expose port
EXPOSE 8000

# Command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]