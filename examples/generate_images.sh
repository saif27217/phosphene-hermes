#!/usr/bin/env bash
#
# generate_images.sh — convenience wrapper around scripts/image_gen.py
# Generates the curated psychiatry / mental-health 3:4 image set via FLUX.1 [dev].
#
# Prerequisites (one of):
#   A) fal_client installed + logged in:  pip install fal-client && fal-client login
#   B) FAL_KEY exported in env:           export FAL_KEY=*****
#
# Usage:
#   ./examples/generate_images.sh                 # generate the curated set
#   ./examples/generate_images.sh --seed 42       # deterministic set
#   ./examples/generate_images.sh --prompts prompts/custom.tsv
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

OUT="${OUT_DIR:-generated_images}"
PROMPTS_FILE="${PROMPTS_FILE:-prompts/psychiatry.tsv}"
SEED_FLAG=""
while [ $# -gt 0 ]; do
  case "$1" in
    --seed) SEED_FLAG="--seed $2"; shift 2 ;;
    --prompts) PROMPTS_FILE="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

echo "==> Phosphene-Hermes FLUX image generation"
echo "    prompts : $PROMPTS_FILE"
echo "    out     : $OUT"
echo "    backend : auto (fal_client -> requests)"

python3 scripts/image_gen.py \
  --prompts "$PROMPTS_FILE" \
  --out "$OUT" \
  --width 768 --height 1024 \
  $SEED_FLAG

echo "==> Done. See $OUT/manifest.json"
