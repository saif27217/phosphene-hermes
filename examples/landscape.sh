#!/bin/bash
# High-quality landscape video
# Usage: ./landscape.sh [prompt]

BASE_URL="https://macbook-pro.tailc4e23e.ts.net:8443"
PROMPT="${1:-Cinematic aerial drone shot of a coastal cliff at golden hour, waves crashing below, volumetric light through sea mist, photorealistic, ARRI Alexa}"

echo "Submitting high-quality landscape video..."
echo "Prompt: $PROMPT"

curl -sSk -X POST \
  -F "mode=t2v" \
  -F "prompt=$PROMPT" \
  -F "negative_prompt=cartoon, anime, cgi, low quality, blurry, text, watermark" \
  -F "width=1280" \
  -F "height=704" \
  -F "frames=121" \
  -F "steps=8" \
  -F "quality=balanced" \
  -F "accel=off" \
  -F "upscale=fit_720p" \
  -F "upscale_method=lanczos" \
  -F "temporal_mode=native" \
  -F "cfg_scale=3.0" \
  -F "teacache_thresh=1.8" \
  -F "stage1_steps=10" \
  -F "stage2_steps=3" \
  "$BASE_URL/queue/add" | python3 -m json.tool

echo ""
echo "Job submitted. Monitor with: ./monitor.sh"
