# Docker Setup for Django Inventory Management App

This project includes Docker configuration files to run the Django application in containers.

## Prerequisites

- Docker Desktop (for Windows/Mac) or Docker Engine (for Linux)
- Docker Compose (included with Docker Desktop)

## Quick Start

### Using Docker Compose (Recommended)

1. Build and start the containers:
```bash
docker-compose up --build
```

2. The application will be accessible at: `http://localhost:8000`

### Using Dockerfile Only

1. Build the image:
```bash
docker build -t inventory-app .
```

2. Run the container:
```bash
docker run -p 8000:8000 inventory-app
```

## Environment Variables

The application uses a `.env` file for configuration. Make sure your `.env` file is in the project root.

## Production Setup

A production-ready Dockerfile is included as `Dockerfile.prod` which uses Gunicorn as the WSGI server:

```bash
docker build -f Dockerfile.prod -t inventory-app:prod .
docker run -p 8000:8000 inventory-app:prod
```

## Notes

- The application uses SQLite as the default database, stored as `db.sqlite3` in the project root
- Static files are collected during the build process
- Media files are stored in the `media` directory
- The development server is used for the default Dockerfile
- The production Dockerfile uses Gunicorn as the WSGI server