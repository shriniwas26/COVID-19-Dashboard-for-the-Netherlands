FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
EXPOSE 8080

# Clean up apt cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install uv
RUN pip install -U pip && pip install --no-cache-dir 'uv<1.0.0'

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app

USER appuser

COPY --chown=appuser:appuser ./uv.lock ./pyproject.toml ./

RUN uv sync

COPY --chown=appuser:appuser . .

# Run the application with Gunicorn
CMD ["bash", "start.sh"]
