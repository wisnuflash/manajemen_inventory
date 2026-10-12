# ==============================================================================
# Multi-stage Dockerfile for Django Inventory Management (Production Ready)
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build dependencies & virtual environment
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build tools and C-header libraries for compiling Python wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------------------------
# Stage 2: Minimal Production Runtime
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS runner

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000 \
    GUNICORN_WORKERS=3 \
    GUNICORN_THREADS=2 \
    GUNICORN_TIMEOUT=60

WORKDIR /app

# Install runtime shared libraries only (no compiler tools in final image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create a dedicated non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser -u 1001 -d /app appuser

# Prepare directories for static files, media uploads, and SQLite database
RUN mkdir -p /app/staticfiles /app/media \
    && chown -R appuser:appuser /app

# Copy application source code with non-root ownership
COPY --chown=appuser:appuser . /app/

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user for security hardening
USER appuser

# Pre-collect static files during build
RUN python manage.py collectstatic --noinput

# Expose default application port
EXPOSE 8000

# Container healthcheck using Python standard library
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:' + '${PORT:-8000}' + '/').read()" || exit 1

# Entrypoint to handle migrations and static files at startup
ENTRYPOINT ["/app/entrypoint.sh"]

# Start production WSGI server with Gunicorn
CMD ["sh", "-c", "exec gunicorn inventori.wsgi:application --bind 0.0.0.0:${PORT} --workers ${GUNICORN_WORKERS} --threads ${GUNICORN_THREADS} --timeout ${GUNICORN_TIMEOUT} --access-logfile - --error-logfile -"]