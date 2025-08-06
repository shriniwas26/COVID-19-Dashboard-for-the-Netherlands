FROM python:3.13-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MALLOC_ARENA_MAX=2
EXPOSE 8080

# Install build dependencies, curl for healthcheck, and uv
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip install -U pip && \
    pip install --no-cache-dir 'uv>0.8.0,<0.9.0'

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app

USER appuser

COPY --chown=appuser:appuser ./uv.lock ./pyproject.toml ./

RUN uv sync --no-cache --verbose

COPY --chown=appuser:appuser . .

# Make start.sh executable
RUN chmod +x start.sh

# Run the application with Gunicorn
CMD ["bash", "start.sh"]
