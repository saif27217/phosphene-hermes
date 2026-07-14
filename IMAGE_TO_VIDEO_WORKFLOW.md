# Image → Video Workflow

Generate portrait videos from reference images using Phosphene's LTX model. **This is the only mode that avoids LTX 2.3's random text artifacts.**

## Why Image → Video?

LTX 2.3 has a known training data pollution issue — the model generates random Vietnamese text/logos in text-to-video mode regardless of prompt, seed, or settings. **Image → Video (`mode=i2v`) is the only workaround** that produces clean output.

**Important:** Even with `mode=i2v`, the last ~5-10 frames may still have text artifacts. **Solution:** Generate extra frames and trim the end.

## Quick Start

```bash
# 1. Find a free image from Pexels/Unsplash
curl -sL -o reference.jpg "https://images.pexels.com/photos/7176321/pexels-photo-7176321.jpeg?auto=compress&cs=tinysrgb&w=800"

# 2. Upload to Phosphene
curl -sSk -X POST -F "image=@reference.jpg" "https://macbook-pro.tailc4e23e.ts.net:8443/upload"
# → {"ok": true, "path": "/path/to/uploaded.jpg"}

# 3. Generate video
curl -sSk -X POST \
  -d "mode=i2v" \
  -d "prompt=A warm therapy session..." \
  -d "image=/path/to/uploaded.jpg" \
  -d "width=576" \
  -d "height=768" \
  -d "frames=121" \
  -d "quality=quick" \
  -d "upscale=off" \
  -d "video_skip_step=1" \
  "https://macbook-pro.tailc4e23e.ts.net:8443/queue/add"
```

## Step-by-Step Workflow

### Step 1: Find Reference Image

**Sources (free, no attribution required):**
- **Pexels**: `https://www.pexels.com/search/[query]/`
- **Unsplash**: `https://unsplash.com/s/photos/[query]`

**Download directly:**
```bash
# Pexels - therapy session
curl -sL -o reference.jpg "https://images.pexels.com/photos/7176321/pexels-photo-7176321.jpeg?auto=compress&cs=tinysrgb&w=800"

# Pexels - psychiatrist consultation
curl -sL -o reference.jpg "https://images.pexels.com/photos/7176317/pexels-photo-7176317.jpeg?auto=compress&cs=tinysrgb&w=800"

# Pexels - counseling session
curl -sL -o reference.jpg "https://images.pexels.com/photos/7176319/pexels-photo-7176319.jpeg?auto=compress&cs=tinysrgb&w=800"
```

**Image requirements:**
- Clear subject (person, scene, object)
- Good lighting
- Simple composition
- Resolution: 600-800px width recommended

### Step 2: Verify Image (Optional)

```bash
# Check image dimensions
identify reference.jpg

# Or use Python
python3 -c "
from PIL import Image
img = Image.open('reference.jpg')
print(f'Size: {img.size}')
print(f'Mode: {img.mode}')
"
```

### Step 3: Upload to Phosphene

```bash
# Upload with correct field name ('image', not 'file')
curl -sSk --max-time 30 -X POST -F "image=@reference.jpg" \
  "https://macbook-pro.tailc4e23e.ts.net:8443/upload"

# Response: {"ok": true, "path": "/Users/apple/pinokio/api/phosphene.git/panel_uploads/XXXXX_reference.jpg"}
```

### Step 4: Generate Video

```bash
# Portrait 3:4 (recommended)
curl -sSk --max-time 30 -X POST \
  -d "mode=i2v" \
  -d "prompt=A warm, comfortable therapy session. The therapist listens attentively while the client speaks. Natural window light, photorealistic, documentary style." \
  -d "negative_prompt=cartoon, anime, cgi, 3d render, low quality, blurry, text, watermark" \
  -d "image=/path/to/uploaded.jpg" \
  -d "width=576" \
  -d "height=768" \
  -d "frames=121" \
  -d "steps=8" \
  -d "quality=quick" \
  -d "accel=off" \
  -d "upscale=off" \
  -d "temporal_mode=native" \
  -d "cfg_scale=3.0" \
  -d "teacache_thresh=1.8" \
  -d "stage1_steps=8" \
  -d "stage2_steps=3" \
  -d "video_skip_step=1" \
  -d "audio_skip_step=1" \
  -d "seed=-1" \
  "https://macbook-pro.tailc4e23e.ts.net:8443/queue/add"
```

## Resolution Options

| Ratio | Width | Height | Use Case |
|-------|-------|--------|----------|
| 3:4 | 576 | 768 | **Portrait (recommended)** |
| 3:4 | 768 | 1024 | High-res portrait |
| 16:9 | 1024 | 576 | Landscape |
| 1:1 | 576 | 576 | Square |
| 9:16 | 576 | 1024 | Mobile/TikTok |

## Duration / Frame Count

Formula: `frames = (seconds × 24) + 1`

| Frames | Duration | Generation Time (quick) |
|--------|----------|------------------------|
| 37 | ~1.5s | ~90s |
| 73 | ~3s | ~180s |
| 121 | ~5s | ~300s |
| 161 | ~6.7s | ~400s |
| 241 | ~10s | ~600s |

## ⚠️ Text Artifact Workaround: Generate Extra + Trim

**Problem:** Even with `mode=i2v`, the last ~5-10 frames may have text artifacts.

**Solution:** Generate extra frames, then trim the end with ffmpeg.

```bash
# 1. Generate 161 frames (want ~5s clean = 121 frames)
#    Extra 40 frames as buffer for text artifacts

# 2. Trim last 20 frames
ffmpeg -i input.mp4 -frames:v 141 -c:v libx264 -c:a copy output_trimmed.mp4 -y

# 3. Verify last frame is clean
ffmpeg -i output_trimmed.mp4 -vf "select=eq(n\,140)" -vframes 1 last_frame.jpg -y
```

**Frame buffer guide:**
| Desired Duration | Generate Frames | Trim To | Buffer |
|-----------------|-----------------|---------|--------|
| ~3s (73 frames) | 93 | 73 | 20 frames |
| ~5s (121 frames) | 141 | 121 | 20 frames |
| ~7s (161 frames) | 181 | 161 | 20 frames |
| ~10s (241 frames) | 261 | 241 | 20 frames |

## Quality Presets

| Quality | Steps | Time | Notes |
|---------|-------|------|-------|
| `quick` | 8 | ~5 min | Fastest, lower quality |
| `balanced` | 8 | ~8 min | Good balance |
| `standard` | 8 | ~8 min | Same as balanced |
| `high` | 16+ | ~15 min | Best quality (needs Q8) |

**Note**: Minimum 8 steps required. `steps=4` fails with error.

## Critical Settings

### Required for Clean Output (No Text Artifacts)

```bash
-d "mode=i2v"           # MUST use Image → Video, not t2v
-d "video_skip_step=1"  # Critical - skip processing step
-d "audio_skip_step=1"  # Critical - skip audio processing step
```

### Anti-Text Negative Prompt

```bash
-d "negative_prompt=cartoon, anime, cgi, 3d render, low quality, blurry, text, watermark"
```

### Upscaling

```bash
-d "upscale=off"        # Recommended for clean output
# OR
-d "upscale=fit_720p"   # If you need higher resolution
```

## Monitoring

### Poll Status

```bash
curl -sSk --max-time 30 https://macbook-pro.tailc4e23e.ts.net:8443/status | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
if data['running']:
    c = data['current']
    p = c.get('progress', {})
    print(f'{p.get(\"phase_label\",\"?\")} {p.get(\"pct\",0)}%')
else:
    print('Idle')
"
```

### Background Monitor

```bash
while true; do
  STATUS=$(curl -sSk --max-time 30 https://macbook-pro.tailc4e23e.ts.net:8443/status 2>/dev/null)
  if echo "$STATUS" | grep -q '"running":false\|"running": false'; then
    echo "DONE"
    break
  fi
  PHASE=$(echo "$STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); c=d.get('current'); p=c.get('progress',{}) if c else {}; print(f'{p.get(\"phase_label\",\"?\")} {p.get(\"pct\",0)}%')" 2>/dev/null)
  echo "[$(date +%H:%M:%S)] $PHASE"
  sleep 10
done
```

## Download Output

```bash
# Get latest output
curl -sSk --max-time 30 https://macbook-pro.tailc4e23e.ts.net:8443/status | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
h = data['history'][0]
print(f'Output: {h.get(\"output_path\",\"N/A\")}')
for o in data.get('outputs', []):
    print(f'File: {o[\"name\"]} ({o[\"size_mb\"]:.1f}MB)')
"

# Download file
curl -sSk -o output.mp4 "https://macbook-pro.tailc4e23e.ts.net:8443/file?path=/path/to/output.mp4"
```

## Extract Frames (for Image Output)

```bash
# Extract middle frame (best quality)
ffmpeg -i output.mp4 -vf "select=eq(n\,60)" -vframes 1 frame.jpg -y

# Extract first frame
ffmpeg -i output.mp4 -vframes 1 first_frame.jpg -y

# Extract multiple frames
ffmpeg -i output.mp4 -vf "select=eq(n\,30)" -vframes 1 frame_30.jpg -y
ffmpeg -i output.mp4 -vf "select=eq(n\,60)" -vframes 1 frame_60.jpg -y
ffmpeg -i output.mp4 -vf "select=eq(n\,90)" -vframes 1 frame_90.jpg -y
```

## Prompt Templates

**Tip:** Use the `video-prompt-enhancer` skill for cinematic prompts. See `skills/video-prompt-enhancer.md`.

### Therapy/Psychiatry (Enhanced)

```
Medium shot at eye level. A therapist in a plaid shirt sits in the foreground, pen in hand, gesturing as she speaks. Across from her, a client in a soft green sweater leans forward slightly, hands raised in expressive conversation, eyes locked on the therapist. The room has a muted purple wall, a warm lamp casting gentle light, and a small potted plant on a side table. Soft, even lighting fills the space. The camera slowly pushes in, settling on the client's face as she nods thoughtfully. Warm amber tones, shallow depth of field, film grain. Quiet, intimate, contemplative.
```

### Professional Portrait (Enhanced)

```
Close-up at eye level. A professional in their mid-30s sits in a modern office, hands clasped on the desk. Natural window light from the left illuminates their face, creating soft shadows on the right side. The camera holds perfectly still. Warm earth tones, leather chair visible in soft focus behind them. Film grain, shallow depth of field, 85mm portrait lens. Thoughtful, serene.
```

### Creative/Artistic (Enhanced)

```
Medium wide shot. An artist stands in their studio, surrounded by canvases and paint supplies. Natural light streams through large windows, casting long shadows across the wooden floor. The camera slowly pans right, revealing more of the studio as the artist turns to examine a painting. Rich saturated colors, warm golden tones. The faint sound of a brush against canvas. Creative, inspiring.
```

### Medical/Clinical (Enhanced)

```
Medium shot, slightly low angle. A doctor in a white coat sits across from a patient, clipboard in hand. Clean clinical setting with soft overhead lighting. The doctor leans forward slightly, listening intently. The camera slowly pushes in, settling on a close-up of the doctor's face as they nod thoughtfully. Cool blue tones, sterile environment, shallow depth of field. Professional, compassionate.
```

### Basic (Minimal — for quick tests)

```
A warm, comfortable therapy session. The therapist listens attentively while the client speaks. Natural window light, photorealistic, documentary style.
```

## Results

### Latest: Enhanced Prompt + Trim (✅ Best Result)

```
Job:       j-19f6035f01b-016
Status:    ✅ done
Mode:      i2v (Image → Video)
Resolution: 576×768 (3:4 portrait)
Frames:    161 generated → 141 trimmed (~5.9s clean)
Quality:   quick
Elapsed:   401s (~6.7 min)
Output:    medium_shot_at_eye_level_a_2.mp4 → trimmed
Size:      632KB (trimmed)
Reference: Pexels #7176316 (therapy session)
Prompt:    Enhanced with 6-element framework
Text artifacts: NONE (trimmed) ✓
```

### Previous: Basic Prompt

```
Job:       j-19f6014d488-014
Status:    ✅ done
Mode:      i2v (Image → Video)
Resolution: 576×768 (3:4 portrait)
Frames:    121 (~5 seconds)
Quality:   quick
Elapsed:   297s (~5 min)
Output:    a_warm_comfortable_therapy_session_the_3.mp4
Size:      1.3MB
Reference: Pexels #7176321 (therapy session)
Text artifacts: NONE ✓
```

## Troubleshooting

### Error: "steps=4 is below the 8-step minimum"

**Fix**: Use `steps=8` minimum. Q4 distilled schedule requires at least 8 steps.

### Text Artifacts Still Appearing

**Fix 1**: Ensure you're using `mode=i2v`, not `mode=t2v`. Text-to-Video mode has training data pollution.

**Fix 2**: Even with `mode=i2v`, the last ~5-10 frames may have text. Generate extra frames (e.g., 161 instead of 121) and trim the end:
```bash
ffmpeg -i input.mp4 -frames:v 141 -c:v libx264 -c:a copy output_trimmed.mp4 -y
```

**Fix 3**: Check the last frame to verify it's clean:
```bash
ffmpeg -i output_trimmed.mp4 -vf "select=eq(n\,140)" -vframes 1 last_frame.jpg -y
```

### Upload Error: "no field 'image' or 'audio'"

**Fix**: Use `-F "image=@file.jpg"`, not `-F "file=@file.jpg"`.

### Job Fails with "reference image required"

**Fix**: Ensure `image` parameter points to uploaded file path, not original URL.

## Files Created

```
phosphene-hermes/
├── IMAGE_TO_VIDEO_WORKFLOW.md      # This file
├── PORTRAIT_VIDEO_WORKFLOW.md
├── PORTRAIT_IMAGE_FROM_VIDEO_WORKFLOW.md
├── LANDSCAPE_VIDEO_WORKFLOW.md
├── README.md
├── skills/
│   ├── phosphene-hermes.md
│   └── video-prompt-enhancer.md    # Cinematic prompt framework
├── examples/
└── scripts/
```
