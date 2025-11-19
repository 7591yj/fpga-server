#!/usr/bin/env bash
set -euo pipefail

DB_PATH="/opt/fpga_app/config/jobs.db"
SCHEMA_PATH="/opt/fpga_app/config/schema.sql"

mkdir -p "$(dirname "$DB_PATH")"

if [[ ! -f "$DB_PATH" ]]; then
  echo "Creating new jobs database..."
  sqlite3 "$DB_PATH" <"$SCHEMA_PATH"
  # Match ownership of schema file
  OWNER_USER=$(stat -c '%U' "$SCHEMA_PATH")
  OWNER_GROUP=$(stat -c '%G' "$SCHEMA_PATH")
  chown "$OWNER_USER":"$OWNER_GROUP" "$DB_PATH"

  echo "Database ownership set to $OWNER_USER:$OWNER_GROUP"
else
  echo "Database already exists: $DB_PATH"
fi
