#!/bin/bash
# Portrait video
# Usage: ./portrait.sh [prompt]

BASE_URL="https://macbook-pro.tailc4e23e.ts.net:8443"
PROMPT="${1:-A person walking through a sunlit garden, soft bokeh background, cinematic lighting}"

echo "Submitting portrait video..."
echo "Prompt: $PROMPT"

curl -sSk -X POST \
  -F "mode=t2v" \
  -F "prompt=$PROMPT" \
  -F "negative_prompt=blurry, low quality, text, watermark, distorted face" \
  -F "width=576" \
  -F "height=1024" \
  -F "frames=121" \
  -F "steps=8" \
  -F "quality=balanced" \
  -F "accel=off" \
  -F "upscale=fit_720p" \
  -F "upscale_method=lanczos" \
  -F "temporal_mode=native" \
  -F "cfg_scale=3.0" \
  -F "teacache_thresh=1.8" \
  "$BASE_URL/queue/add" | python3 -m json.tool

echo ""
echo "Job submitted. Monitor with: ./monitor.sh"
