# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        python3-dev \
        sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . /app/

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Change ownership of the application directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Collect static files after migrations
RUN python manage.py migrate --noinput
RUN python manage.py collectstatic --noinput

# Expose port 8000 for the Django application
EXPOSE 8000

# Run the Django development server by default
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]