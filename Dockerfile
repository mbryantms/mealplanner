# Family Meal Planner Dockerfile
# Multi-stage build for production

# Stage 1: Build frontend assets
FROM node:20-alpine AS frontend

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY tailwind.config.js ./
COPY static/css/input.css ./static/css/
COPY templates/ ./templates/
COPY apps/ ./apps/

RUN npm run build:css

# Stage 2: Python application
FROM python:3.12-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    STATIC_ROOT=/app/staticfiles

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY config/ ./config/
COPY apps/ ./apps/
COPY templates/ ./templates/
COPY static/ ./static/
COPY manage.py ./

# Copy built frontend assets from frontend stage
COPY --from=frontend /app/static/css/output.css ./static/css/output.css

# Create directories and non-root user
RUN mkdir -p /app/staticfiles /app/media \
    && useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app

USER appuser

# Collect static files to /app/staticfiles
RUN uv run python manage.py collectstatic --noinput

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--worker-class", "gthread", "--access-logfile", "-", "--error-logfile", "-"]
