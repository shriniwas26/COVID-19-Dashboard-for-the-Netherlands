set -euo pipefail

uv run gunicorn --bind 0.0.0.0:8080 --workers 1 --timeout 10 --max-requests 100 --max-requests-jitter 10 --worker-class sync covid_dashboard_nl:server
