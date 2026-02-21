#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Emplacement demandé pour la base SQLite sur votre Mac.
export RUNNING_CLUB_DB_PATH="/Users/ymusset/Library/CloudStorage/GoogleDrive-yo.musset@gmail.com/Mon Drive/1 Drive Perso/4 - Sites web/inscriptions courses/running_club.db"
mkdir -p "$(dirname "$RUNNING_CLUB_DB_PATH")"

echo "[run] Lancement du site sur http://localhost:8000"
echo "[run] Base SQLite: $RUNNING_CLUB_DB_PATH"
python3 app.py
