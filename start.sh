set +e
uv run python update_data.py

set -e
uv run gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 10 covid_dashboard_nl:server
