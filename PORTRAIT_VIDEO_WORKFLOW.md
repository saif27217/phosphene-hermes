# Portrait Video Workflow

Generate portrait-oriented videos (3:4 or 9:16) using Phosphene's LTX model on Apple Silicon.

## Quick Start

```bash
# Submit portrait video job
curl -sSk -X POST \
  -d "mode=t2v" \
  -d "prompt=A contemplative psychiatrist sitting in a warm, softly lit office" \
  -d "width=576" \
  -d "height=768" \
  -d "frames=37" \
  -d "quality=balanced" \
  "https://macbook-pro.tailc4e23e.ts.net:8443/queue/add"

# Monitor
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/status
```

## Portrait Resolutions

| Ratio | Width | Height | Frames | Duration | Use Case |
|-------|-------|--------|--------|----------|----------|
| 3:4 | 576 | 768 | 37 | ~1.5s | Quick portrait |
| 3:4 | 576 | 768 | 121 | ~5s | Standard portrait |
| 3:4 | 768 | 1024 | 121 | ~5s | High-res portrait |
| 9:16 | 576 | 1024 | 37 | ~1.5s | Mobile portrait |
| 9:16 | 576 | 1024 | 121 | ~5s | Standard mobile |
| 9:16 | 432 | 768 | 121 | ~5s | Small mobile |

## Quality Presets

| Quality | Steps | Time (37 frames) | Time (121 frames) |
|---------|-------|------------------|-------------------|
| `quick` | 4 | ~30s | ~2 min |
| `balanced` | 8 | ~105s | ~5 min |
| `standard` | 8 | ~105s | ~5 min |
| `high` | 16+ | ~3 min | ~8 min |

## Complete API Parameters

```bash
curl -sSk -X POST \
  -d "mode=t2v" \
  -d "prompt=YOUR_PROMPT_HERE" \
  -d "negative_prompt=cartoon, anime, cgi, low quality, blurry, text, watermark" \
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
  -d "enhance=false" \
  -d "hdr=false" \
  -d "loras=[]" \
  "https://macbook-pro.tailc4e23e.ts.net:8443/queue/add"
```

### Parameter Reference

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `mode` | `t2v`, `i2v`, `keyframe`, `extend` | `t2v` | Generation mode |
| `prompt` | string | required | Video description |
| `negative_prompt` | string | `""` | Things to avoid |
| `width` | int | 1024 | Output width |
| `height` | int | 576 | Output height |
| `frames` | int | 121 | Number of frames (24fps) |
| `steps` | int | 8 | Diffusion steps |
| `quality` | `quick`, `balanced`, `standard`, `high` | `balanced` | Quality preset |
| `accel` | `off`, `boost`, `turbo` | `off` | Acceleration mode |
| `upscale` | `off`, `fit_720p`, `x2` | `fit_720p` | Upscaling |
| `temporal_mode` | `native`, `fps12_interp24` | `native` | Frame interpolation |
| `cfg_scale` | float | 3.0 | Classifier-free guidance |
| `teacache_thresh` | float | 1.8 | TeaCache threshold |
| `seed` | int | -1 | Random seed (-1=random) |

## Frame Calculation

Formula: `frames = (seconds × 24) + 1`

| Duration | Frames |
|----------|--------|
| 1.5s | 37 |
| 2s | 49 |
| 3s | 73 |
| 5s | 121 |
| 10s | 241 |

## Generation Modes

### Text-to-Video (t2v)
```bash
-d "mode=t2v"
-d "prompt=A person walking through a sunlit garden"
```

### Image-to-Video (i2v)
```bash
# First upload image
curl -sSk -X POST -F "file=@image.png" https://macbook-pro.tailc4e23e.ts.net:8443/upload

# Then submit
-d "mode=i2v"
-d "prompt=The scene comes to life"
-d "image=/path/to/uploaded.png"
```

### Keyframe Interpolation (keyframe)
```bash
-d "mode=keyframe"
-d "start_image=/path/to/start.png"
-d "end_image=/path/to/end.png"
```

### Extend Video (extend)
```bash
-d "mode=extend"
-d "video_path=/path/to/video.mp4"
-d "extend_frames=6"
-d "extend_direction=after"
```

## Acceleration Modes

| Mode | Value | Speed | Quality |
|------|-------|-------|---------|
| Exact | `off` | Normal | Best |
| Boost | `boost` | ~1.5x | Good |
| Turbo | `turbo` | ~2x | Acceptable |

## Upscaling

| Mode | Value | Description |
|------|-------|-------------|
| Off | `off` | No upscaling |
| 720p | `fit_720p` | Scale to fit 720p |
| 2x | `x2` | Double resolution |

Methods: `lanczos` (standard), `pipersr` (AI super-resolution)

## Audio Options

| Mode | Value | Description |
|------|-------|-------------|
| Joint Audio | `i2v` | LTX generates audio synced with visual |
| External Audio | `i2v_clean_audio` | Mux external audio file |
| No Music | `no_music=true` | Suppress music |
| No Voice | `no_voice=true` | Suppress voice |

## Prompt Templates

### Portrait - Professional
```
A [profession] in a [setting], [action/pose], [lighting], [style].
[details about environment], [camera angle], [lens].
```

### Portrait - Emotional
```
A person [emotion] in a [setting], [lighting description],
[background details], [photography style], [camera settings].
```

### Portrait - Environmental
```
A [subject] in [environment], surrounded by [details],
[time of day], [weather/atmosphere], [style reference].
```

## Monitoring

### Poll Status
```bash
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/status | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data['running']:
    c = data['current']
    p = c.get('progress', {})
    print(f'{p.get(\"phase_label\",\"?\")} {p.get(\"pct\",0)}% ETA: {p.get(\"eta_sec\",0):.0f}s')
else:
    print('Idle')
"
```

### Background Monitor
```bash
while true; do
  STATUS=$(curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/status 2>/dev/null)
  if echo "$STATUS" | grep -q '"running":false'; then
    echo "DONE"
    break
  fi
  PHASE=$(echo "$STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); c=d.get('current'); p=c.get('progress',{}) if c else {}; print(f'{p.get(\"phase_label\",\"?\")} {p.get(\"pct\",0)}%')" 2>/dev/null)
  echo "[$(date +%H:%M:%S)] $PHASE"
  sleep 10
done
```

## Download

### Get Output URL
```bash
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/status | python3 -c "
import sys, json
data = json.load(sys.stdin)
for o in data.get('outputs', []):
    print(f'{o[\"name\"]} ({o[\"size_mb\"]:.1f}MB) — https://macbook-pro.tailc4e23e.ts.net:8443{o[\"url\"]}')
"
```

### Download File
```bash
curl -sSk -o output.mp4 "DOWNLOAD_URL"
```

## Results

### Our Test Run

```
Job:       j-19f5f9cbb48-005
Status:    ✅ done
Time:      105s (1.75 min)
Output:    a_contemplative_psychiatrist_sitting_in_a_2.mp4
Size:      155KB
Mode:      t2v
Settings:  576×768, 37 frames, balanced quality
```

### Performance

| Setting | Value |
|---------|-------|
| Resolution | 576×768 (3:4) |
| Frames | 37 (~1.5s) |
| Quality | Balanced (8 steps) |
| Acceleration | Off (exact) |
| Generation Time | 105s |
| File Size | 155KB |

## Pitfalls

1. **FormData vs URL-encoded**: Use `-d` (URL-encoded), not `-F` (multipart)
2. **Default params**: Omitting fields uses server defaults (1024×576, 121 frames)
3. **Portrait dimensions**: Height > Width for portrait orientation
4. **Frame count**: Must be `8k+1` (37, 49, 73, 121, etc.)
5. **Server busy**: Large model downloads can block all endpoints

## Files Created

```
phosphene-hermes/
├── PORTRAIT_VIDEO_WORKFLOW.md             # This file
├── PORTRAIT_IMAGE_FROM_VIDEO_WORKFLOW.md  # Image extraction workflow
├── LANDSCAPE_VIDEO_WORKFLOW.md            # Landscape workflow
├── README.md
├── skills/
│   └── phosphene-hermes.md
├── examples/
└── scripts/
```
