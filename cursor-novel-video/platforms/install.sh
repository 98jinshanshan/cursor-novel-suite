#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-.agents/skills}"
mkdir -p "$DEST"
cp -R "$ROOT/skills/"* "$DEST/"
echo "Installed to $DEST"
