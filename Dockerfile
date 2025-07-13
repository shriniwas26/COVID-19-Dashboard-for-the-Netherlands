FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app && \
    uv sync --no-cache --no-install-project

COPY --chown=app:app . .

USER app

# Expose port
EXPOSE 8080

# Run the application with Gunicorn
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "covid_dashboard_nl:server"]

