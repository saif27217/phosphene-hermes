#!/usr/bin/env bash
#
# generate_local_images.sh — run the LOCAL Phosphene (Mac) FLUX image workflow.
#
# Drives Sak's MacBook Pro (Apple Silicon, Tailscale) Phosphene endpoint,
# which runs FLUX via mflux. Images come out 1280x720 and are cropped to
# exact 3:4 (768x1024) by scripts/local_image_gen.py.
#
# Prereqs:
#   - Mac reachable on Tailscale at the BASE_URL below
#   - Python + Pillow:  pip install pillow
#   (no API key needed — LAN/self-signed cert is accepted by the script)
#
# Usage:
#   ./examples/generate_local_images.sh                      # curated set
#   ./examples/generate_local_images.sh --prompt "..." --name foo
#   BASE_URL=https://other.tailscale.host:8443 ./examples/generate_local_images.sh
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BASE_URL="${BASE_URL:-https://macbook-pro.tailc4e23e.ts.net:8443}"
OUT="${OUT_DIR:-generated_images}"
PROMPTS_FILE="${PROMPTS_FILE:-prompts/psychiatry_local.tsv}"
EXTRA=()
while [ $# -gt 0 ]; do
  case "$1" in
    --prompt) EXTRA+=("--prompt" "$2"); shift 2 ;;
    --name)   EXTRA+=("--name" "$2"); shift 2 ;;
    --prompts) PROMPTS_FILE="$2"; shift 2 ;;
    --out)    OUT="$2"; shift 2 ;;
    --base-url) BASE_URL="$2"; shift 2 ;;
    *) shift ;;
  esac
done

echo "==> LOCAL Phosphene image generation"
echo "    base_url : $BASE_URL"
echo "    prompts  : ${PROMPTS_FILE:-<single>}"
echo "    out      : $OUT"

python3 scripts/local_image_gen.py \
  --base-url "$BASE_URL" \
  --out "$OUT" \
  --width 768 --height 1024 \
  "${EXTRA[@]:-}" \
  ${PROMPTS_FILE:+--prompts "$PROMPTS_FILE"}

echo "==> Done. See $OUT/manifest.local.json"
