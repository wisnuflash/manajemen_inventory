#!/bin/sh
set -e

# Run database migrations if enabled (default: 1)
if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
    echo "==> Running database migrations..."
    python manage.py migrate --noinput
fi

# Collect static files if enabled (default: 1)
if [ "${COLLECT_STATIC:-1}" = "1" ]; then
    echo "==> Collecting static files..."
    python manage.py collectstatic --noinput
fi

# Execute the main container command (replaces PID 1 for proper signal handling)
exec "$@"
