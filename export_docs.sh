#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Dossier Google Drive local (Mac) demandé.
DEFAULT_DOCS_DIR="/Users/ymusset/Library/CloudStorage/GoogleDrive-yo.musset@gmail.com/Mon Drive/1 Drive Perso/4 - Sites web/inscriptions courses"
DOCS_TARGET_DIR="${DOCS_TARGET_DIR:-$DEFAULT_DOCS_DIR}"

mkdir -p "$DOCS_TARGET_DIR"

cp README.md "$DOCS_TARGET_DIR/README-inscriptions-courses.md"
cp docs/guide-utilisateur.md "$DOCS_TARGET_DIR/guide-utilisateur-inscriptions-courses.md"

echo "[ok] Documentation exportée dans : $DOCS_TARGET_DIR"
