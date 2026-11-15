#!/bin/sh
set -e

echo "============================================================"
echo " Starting IT Announcement Application (Container Mode)       "
echo "============================================================"

DB_FILE="${SQLITE_PATH:-/app/db.sqlite3}"
echo "[Entrypoint] Database target: $DB_FILE"

# 1. Ensure database file has read/write permissions for container and host user
if [ -f "$DB_FILE" ]; then
    chmod 666 "$DB_FILE" || true
fi

# 2. Ensure media directory exists and has permissions
MEDIA_DIR="/app/media"
if [ ! -d "$MEDIA_DIR" ]; then
    mkdir -p "$MEDIA_DIR"
fi
chmod 777 "$MEDIA_DIR" || true

# 3. Apply database migrations to target database
echo "[Entrypoint] Applying database migrations..."
python manage.py migrate --noinput

# 4. Collect static assets for WhiteNoise
echo "[Entrypoint] Collecting static files..."
python manage.py collectstatic --noinput

echo "============================================================"
echo " Initialization complete. Starting Gunicorn server...      "
echo "============================================================"
exec "$@"
