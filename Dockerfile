FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
EXPOSE 8080

# Install uv
RUN pip install --no-cache-dir uv

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app

USER appuser

COPY --chown=appuser:appuser ./uv.lock ./pyproject.toml ./

RUN uv sync --no-install-project

COPY --chown=appuser:appuser . .

# Run the application with Gunicorn
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "covid_dashboard_nl:server"]

