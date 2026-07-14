#!/bin/bash
# Batch generation from prompts file
# Usage: ./batch-prompt.sh prompts.txt

BASE_URL="https://macbook-pro.tailc4e23e.ts.net:8443"
PROMPTS_FILE="${1:-prompts.txt}"

if [ ! -f "$PROMPTS_FILE" ]; then
  echo "Error: Prompts file not found: $PROMPTS_FILE"
  echo "Create a file with one prompt per line."
  exit 1
fi

echo "Submitting batch from $PROMPTS_FILE..."

PROMPTS=$(cat "$PROMPTS_FILE" | tr '\n' '\n')

curl -sSk -X POST \
  -F "batch=$PROMPTS" \
  "$BASE_URL/queue/batch" | python3 -m json.tool

echo ""
echo "Batch submitted. Monitor with: ./monitor.sh"
