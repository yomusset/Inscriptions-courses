#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Les tests utilisent une base locale temporaire au projet.
export RUNNING_CLUB_DB_PATH="$PWD/running_club.db"
DB_FILE="$RUNNING_CLUB_DB_PATH"
BACKUP_FILE=""

if [[ -f "$DB_FILE" ]]; then
  BACKUP_FILE="${DB_FILE}.bak.$$"
  cp "$DB_FILE" "$BACKUP_FILE"
fi

python3 -m py_compile app.py

rm -f "$DB_FILE"
python3 app.py >/tmp/running-site-smoke.log 2>&1 &
SERVER_PID=$!
cleanup() {
  kill "$SERVER_PID" >/dev/null 2>&1 || true
  rm -f "$DB_FILE"
  if [[ -n "$BACKUP_FILE" && -f "$BACKUP_FILE" ]]; then
    mv "$BACKUP_FILE" "$DB_FILE"
  fi
}
trap cleanup EXIT

sleep 1

curl -fsS http://localhost:8000/ >/dev/null
curl -fsS http://localhost:8000/coureurs >/dev/null
curl -fsS http://localhost:8000/courses >/dev/null
curl -fsS http://localhost:8000/inscriptions >/dev/null
curl -fsS http://localhost:8000/synthese >/dev/null

curl -fsS -o /dev/null -X POST http://localhost:8000/runners \
  -d 'first_name=Test&last_name=Runner&email=test.runner%40mail.com&birth_date=1999-01-01'

curl -fsS -o /dev/null -X POST http://localhost:8000/races \
  -d 'name=Course+Test&city=Paris&race_date=2026-06-01&distance_km=10'

curl -fsS -o /dev/null -X POST http://localhost:8000/registrations \
  -d 'runner_id=1&race_id=1'

curl -fsS http://localhost:8000/synthese | rg -q 'Test Runner|Course Test'

echo "[ok] Smoke test réussi"
