#!/bin/bash
# Quick test video — minimal settings for fastest generation
# Usage: ./quick-test.sh [prompt]

BASE_URL="https://macbook-pro.tailc4e23e.ts.net:8443"
PROMPT="${1:-A single white sphere slowly rotating in dark void}"

echo "Submitting quick test video..."
echo "Prompt: $PROMPT"

curl -sSk -X POST \
  -F "mode=t2v" \
  -F "prompt=$PROMPT" \
  -F "width=480" \
  -F "height=480" \
  -F "frames=37" \
  -F "steps=4" \
  -F "quality=quick" \
  -F "accel=turbo" \
  -F "upscale=off" \
  -F "temporal_mode=native" \
  -F "cfg_scale=3.0" \
  -F "teacache_thresh=1.8" \
  -F "stage1_steps=4" \
  -F "stage2_steps=2" \
  "$BASE_URL/queue/add" | python3 -m json.tool

echo ""
echo "Job submitted. Monitor with: ./monitor.sh"
