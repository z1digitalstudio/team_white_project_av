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

# Corrected library names for runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    libpng16-16 \
    libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r django && useradd -r -g django django

# Copy dependencies from builder
COPY --from=builder /root/.local /home/django/.local

# Copy application code
COPY --chown=django:django . .

# Set ownership and permissions for application code
RUN chown -R django:django /app && \
    chmod -R 755 /app

# Switch to non-root user
USER django

# Update PATH for non-root user
ENV PATH=/home/django/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]