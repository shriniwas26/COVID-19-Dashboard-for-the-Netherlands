#!/bin/bash
set -euo pipefail

# Run with Gunicorn for production stability
uv run gunicorn \
    --bind 0.0.0.0:8080 \
    --workers 2 \
    --timeout 15 \
    --keep-alive 10 \
    --max-requests 100 \
    --max-requests-jitter 100 \
    --worker-connections 100 \
    --worker-class sync \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    covid_dashboard_nl:app
