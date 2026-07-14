# Portrait Image from Video Workflow

Generate a portrait image by creating a video with LTX and extracting the best frame. Uses already-downloaded models — no new model downloads required.

## Why This Approach?

- **LTX (20GB)** is already downloaded for video generation
- **Image engines** (Ideogram 4, Qwen Edit, HiDream) each need 24GB+ separate download
- Extracting a frame from a video gives a high-quality image with zero additional downloads
- Works immediately without waiting for model downloads

## Architecture

```
Prompt → LTX Video (576×768, 37 frames) → ffmpeg → Single Frame (JPG)
```

## Step 1: Submit Portrait Video Job

```bash
curl -sSk -X POST \
  -d "mode=t2v" \
  -d "prompt=A contemplative psychiatrist sitting in a warm, softly lit office, deep in thought, surrounded by books on psychology and mental health. Natural window light, shallow depth of field, photorealistic portrait, professional and empathetic atmosphere. Warm earth tones, leather chair, organized desk with journals. Documentary-style photography, 85mm portrait lens." \
  -d "negative_prompt=cartoon, anime, cgi, 3d render, low quality, blurry, deformed, extra fingers, text, watermark, logo, subtitle" \
  -d "width=576" \
  -d "height=768" \
  -d "frames=37" \
  -d "steps=8" \
  -d "quality=balanced" \
  -d "accel=off" \
  -d "upscale=off" \
  -d "temporal_mode=native" \
  -d "cfg_scale=3.0" \
  -d "teacache_thresh=1.8" \
  -d "stage1_steps=10" \
  -d "stage2_steps=3" \
  -d "seed=-1" \
  "https://macbook-pro.tailc4e23e.ts.net:8443/queue/add"

# Response: {"ok": true, "id": "j-xxxxxxxxxxxx-001"}
```

### Key Parameters for Portrait Image

| Parameter | Value | Why |
|-----------|-------|-----|
| `width` | 576 | Portrait width |
| `height` | 768 | Portrait height (3:4 ratio) |
| `frames` | 37 | Minimum frames (~1.5s) — just need one good frame |
| `quality` | `balanced` | Good quality without excessive time |
| `upscale` | `off` | Don't upscale — we'll extract a single frame |
| `steps` | 8 | Standard quality |

### Resolution Options for Portrait

| Ratio | Width | Height | Use Case |
|-------|-------|--------|----------|
| 3:4 | 576 | 768 | Standard portrait |
| 3:4 | 768 | 1024 | High-res portrait |
| 9:16 | 576 | 1024 | Mobile portrait |
| 9:16 | 432 | 768 | Small mobile |

## Step 2: Monitor Job

```bash
while true; do
  STATUS=$(curl -sSk --max-time 30 https://macbook-pro.tailc4e23e.ts.net:8443/status 2>/dev/null)
  if echo "$STATUS" | grep -q '"running":false\|"running": false'; then
    echo "DONE"
    echo "$STATUS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
h = data['history'][0]
print(f'Job: {h[\"id\"]}')
print(f'Status: {h[\"status\"]}')
print(f'Elapsed: {h[\"elapsed_sec\"]:.0f}s')
for o in data.get('outputs', []):
    print(f'File: {o[\"name\"]} ({o[\"size_mb\"]:.1f}MB)')
"
    break
  fi
  PHASE=$(echo "$STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); c=d.get('current'); p=c.get('progress',{}) if c else {}; print(f'{p.get(\"phase_label\",\"?\")} {p.get(\"pct\",0)}%')" 2>/dev/null)
  echo "[$(date +%H:%M:%S)] $PHASE"
  sleep 10
done
```

## Step 3: Download Video

```bash
# Get download URL from status
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/status | python3 -c "
import sys, json
data = json.load(sys.stdin)
for o in data.get('outputs', []):
    if 'contemplative' in o['name']:
        print(f'https://macbook-pro.tailc4e23e.ts.net:8443{o[\"url\"]}')
"

# Download
curl -sSk -o /tmp/portrait_video.mp4 "DOWNLOAD_URL"
```

## Step 4: Extract Best Frame

```bash
# Extract frame 18 (middle of 37 frames) for best quality
ffmpeg -i /tmp/portrait_video.mp4 -vf "select=eq(n\,18)" -vframes 1 /tmp/portrait_frame.jpg -y

# Or extract first frame
ffmpeg -i /tmp/portrait_video.mp4 -vframes 1 /tmp/portrait_frame_first.jpg -y

# Or extract last frame
ffmpeg -i /tmp/portrait_video.mp4 -vf "select=eq(n\,36)" -vframes 1 /tmp/portrait_frame_last.jpg -y
```

### Frame Selection Strategy

| Frame | Command | Use Case |
|-------|---------|----------|
| Middle (18) | `select=eq(n\,18)` | Best overall quality |
| First (0) | `-vframes 1` | Quick preview |
| Last (36) | `select=eq(n\,36)` | End state |
| Random | `select=not(mod(n\,5))` | Multiple frames |

## Step 5: Deliver to Discord

```bash
# Include MEDIA: path in response
MEDIA:/tmp/portrait_frame.jpg
```

## Results

### Our Test Run

```
Job:       j-19f5f9cbb48-005
Status:    ✅ done
Time:      105s (1.75 min)
Output:    a_contemplative_psychiatrist_sitting_in_a_2.mp4
Size:      155KB
Mode:      t2v (text-to-video)
Settings:  576×768, 37 frames, balanced quality
Frame:     31KB JPG extracted
```

### All Outputs

1. `a_contemplative_psychiatrist_sitting_in_a_2.mp4` — 0.2MB (portrait)
2. `a_contemplative_psychiatrist_sitting_in_a.mp4` — 0.2MB (portrait)
3. `a_cinematic_atmospheric_scene_2_720p.mp4` — 1.8MB (landscape)
4. `a_psychiatrist_sits_across_from_a_up2x.mp4` — 5.4MB
5. `psychiatrist_taking_therapy_warm_comfortable_scene_v720p.mp4` — 2.3MB
6. `a_cinematic_atmospheric_scene_720p.mp4` — 1.3MB

## Prompt Engineering for Portrait Images

### Psychiatry/Mental Health Themes

```
A contemplative psychiatrist sitting in a warm, softly lit office, deep in thought,
surrounded by books on psychology and mental health. Natural window light, shallow
depth of field, photorealistic portrait, professional and empathetic atmosphere.
Warm earth tones, leather chair, organized desk with journals. Documentary-style
photography, 85mm portrait lens.
```

### Negative Prompt (Anti-Artifact)

```
cartoon, anime, cgi, 3d render, low quality, blurry, deformed, extra fingers,
text, watermark, logo, subtitle
```

### Other Portrait Themes

| Theme | Prompt Keywords |
|-------|-----------------|
| Professional | corporate office, business attire, confident pose |
| Creative | artist studio, colorful background, expressive |
| Academic | library, books, intellectual atmosphere |
| Medical | clinical setting, white coat, stethoscope |
| Therapeutic | comfortable couch, warm lighting, empathetic |

## Key Learnings

1. **FormData requirement**: Use `-d` (URL-encoded), not `-F` (multipart) for Phosphene
2. **Portrait dimensions**: 576×768 for 3:4, 576×1024 for 9:16
3. **Frame extraction**: Middle frame (18 of 37) typically has best quality
4. **File sizes**: Portrait videos are much smaller (155KB vs 1.8MB for landscape)
5. **Generation time**: ~105s for portrait vs ~394s for landscape

## Files Created

```
phosphene-hermes/
├── PORTRAIT_IMAGE_FROM_VIDEO_WORKFLOW.md  # This file
├── PORTRAIT_VIDEO_WORKFLOW.md             # Video-focused workflow
├── LANDSCAPE_VIDEO_WORKFLOW.md            # Landscape workflow
├── README.md
├── skills/
│   └── phosphene-hermes.md
├── examples/
└── scripts/
```
