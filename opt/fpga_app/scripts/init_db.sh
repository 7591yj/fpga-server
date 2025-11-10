#!/usr/bin/env bash
set -euo pipefail

DB_PATH="/opt/fpga_app/config/jobs.db"
SCHEMA_PATH="/opt/fpga_app/config/schema.sql"

mkdir -p "$(dirname "$DB_PATH")"

if [[ ! -f "$DB_PATH" ]]; then
  echo "Creating new jobs database..."
  sqlite3 "$DB_PATH" <"$SCHEMA_PATH"
else
  echo "Database already exists: $DB_PATH"
fi
