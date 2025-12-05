#!/usr/bin/env bash
set -euo pipefail
TEMPLATE=/etc/alertmanager/config.yml.tpl
OUT=/etc/alertmanager/config.yml
if [ ! -f "$TEMPLATE" ]; then
  echo "Missing template $TEMPLATE"
  exit 1
fi
envsubst < "$TEMPLATE" > "$OUT"
chmod 600 "$OUT"
exec /bin/alertmanager --config.file="$OUT" --storage.path=/alertmanager
