---
name: phosphene-hermes
description: >
  Comprehensive API guide for Phosphene — an MLX-accelerated text/image-to-video generation
  engine running on Sak's MacBook Pro via Tailscale. Use this skill to submit video generation
  jobs, monitor progress, download outputs, and manage the server remotely from any Hermes session.
version: 3.2.5
host: macbook-pro.tailc4e23e.ts.net
port: 8443
base_url: https://macbook-pro.tailc4e23e.ts.net:8443
tags: video-generation, mlx, tailscale, api, phosphene, ltx
---

# Phosphene — MLX Video Generation API

## What is Phosphene?

Phosphene is a self-hosted text/image-to-video generation engine running on Apple Silicon (MLX
acceleration). It uses **LTX 2.3** (a latent video diffusion model) + **Gemma 3 12B** (text encoder)
to generate videos from prompts. It runs on Sak's MacBook Pro (64GB M-series) via Tailscale.

**Current version**: 3.2.5 (30 commits behind remote 3.2.6)
**Author**: Mr Bizarro (mrbizarro)
**License**: Open source, hosted at `phosphene.git` on the Mac

## Network Access

```
Base URL: https://macbook-pro.tailc4e23e.ts.net:8443
Protocol: HTTPS (self-signed cert — use -k with curl)
Network: Tailscale (100.x.x.x range)
```

All API calls require `-k` (insecure) flag with curl due to self-signed TLS cert.

## Generation Modes

| Mode | Button | Description | Typical Time |
|------|--------|-------------|-------------|
| `t2v` | Text | Prompt → video | 2-15 min |
| `i2v` | Image | Image + prompt → video | ~8 min |
| `keyframe` | FFLF | First/last frame interpolation | ~6 min |
| `keyframe` | Keyframes | Multi-keyframe locked beats | varies |
| `extend` | Extend | Extend existing video clip | ~16 min |
| `character` | Character | Trained face + voice | varies |

## Model Tiers (64GB MacBook Pro)

| Tier | Label | RAM | Max Dim | Q8 | Keyframe | Extend |
|------|-------|-----|---------|-----|----------|--------|
| `standard` | Comfortable | 48-79 GB | 768px (keyframe/extend) | ✅ | ✅ | ✅ |
| (other tiers may exist for smaller Macs) |

**Q8 required for**: High quality, FFLF, multi-keyframe modes.
**Q8 not present on this install** (8 safetensors files missing, 37GB total).

## Installed Models

| Key | Name | Size | Status |
|-----|------|------|--------|
| `q4` | LTX 2.3 Q4 (base, distilled) | 20 GB | ✅ Complete (6/6 files) |
| `gemma` | Gemma 3 12B (4-bit text encoder) | 6 GB | ✅ Complete (4/4 files) |
| `q8` | LTX 2.3 Q8 (high-quality) | 37 GB | ❌ Missing (0/8 files) |

## Curated LoRAs

| ID | Name | Description |
|----|------|-------------|
| `motion-track` | Motion Track Control | Lightricks IC-LoRA for motion-tracked control |
| `union-control` | Union Control | Multi-control (depth, edges, pose) combined |

## Output Presets

| Preset | Pix Fmt | CRF | Size/5s | Use Case |
|--------|---------|-----|---------|----------|
| `archival` | yuv444p | 0 | ~50 MB | Lossless, pro workflows |
| `standard` | yuv420p | 18 | ~7 MB | Default, visually lossless |
| `web` | yuv420p | 23 | ~3 MB | Mobile, bandwidth-limited |

---

## API Reference

### GET /status — Server State & Job History

Returns full server state including running job, queue, history, outputs, memory, and settings.

```bash
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/status
```

**Key fields**:
- `running` (bool) — Is a job currently generating?
- `paused` (bool) — Is the queue paused?
- `current` (object|null) — Currently running job with `progress` sub-object
- `queue` (array) — Pending jobs
- `history` (array) — Completed/failed jobs (most recent first)
- `outputs` (array) — Generated video files with download URLs
- `memory` (object) — `{total_gb, used_gb, pressure_pct, swap_gb}`
- `helper` (object) — Background process status (`alive`, `pid`, `low_memory`)
- `tier` (object) — Hardware tier info with timing estimates
- `settings` (object) — Current output settings

**Progress sub-object** (when running):
```json
{
  "phase": "setup|denoising|decoding|upscale|encode|cleanup",
  "phase_label": "Preparing|Denoising|Decoding|...",
  "pct": 85,
  "elapsed_sec": 183.5,
  "eta_sec": 407.0,
  "remaining_sec": 223.5,
  "denoise_step": 16,
  "denoise_total": 16
}
```

### POST /queue/add — Submit Generation Job

**CRITICAL**: This endpoint accepts `multipart/form-data`, NOT JSON. Use `-F` flags with curl.

```bash
curl -sSk -X POST \
  -F "mode=t2v" \
  -F "prompt=A serene mountain landscape at sunset" \
  -F "negative_prompt=blurry, low quality, text, watermark" \
  -F "width=576" \
  -F "height=1024" \
  -F "frames=121" \
  -F "steps=8" \
  -F "seed=-1" \
  -F "quality=balanced" \
  -F "accel=off" \
  -F "upscale=fit_720p" \
  -F "upscale_method=lanczos" \
  -F "temporal_mode=native" \
  -F "cfg_scale=3.0" \
  -F "teacache_thresh=1.8" \
  -F "stage1_steps=10" \
  -F "stage2_steps=3" \
  -F "enhance=false" \
  -F "hdr=false" \
  -F "loras=[]" \
  "https://macbook-pro.tailc4e23e.ts.net:8443/queue/add"
```

**Response**: `{"ok": true, "id": "j-xxxxxxxxxxxx-001"}`

#### All Job Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | string | `t2v` | `t2v`, `i2v`, `keyframe`, `extend`, `character` |
| `prompt` | string | required | Text description of desired video |
| `negative_prompt` | string | `""` | Things to avoid |
| `width` | int | 1024 | Output width in pixels |
| `height` | int | 576 | Output height in pixels |
| `frames` | int | 121 | Number of frames (24 fps) |
| `steps` | int | 8 | Diffusion denoising steps (4=quick, 8=standard) |
| `seed` | string | `-1` | Random seed (-1 = random) |
| `quality` | string | `balanced` | `quick`, `balanced`, `high` |
| `accel` | string | `off` | `off` (exact), `boost`, `turbo` |
| `upscale` | string | `fit_720p` | `off`, `x2`, `fit_720p` |
| `upscale_method` | string | `lanczos` | Upscaling algorithm |
| `temporal_mode` | string | `native` | Temporal processing mode |
| `cfg_scale` | float | 3.0 | Classifier-free guidance scale |
| `teacache_thresh` | float | 1.8 | TeaCache acceleration threshold |
| `stage1_steps` | int | 10 | First pass denoising steps |
| `stage2_steps` | int | 3 | Second pass denoising steps |
| `enhance` | bool | false | Enable enhancement pass |
| `hdr` | bool | false | HDR output mode |
| `image` | string | `""` | Path to reference image (for i2v/keyframe) |
| `start_image` | string | `""` | Start frame path (for keyframe FFLF) |
| `end_image` | string | `""` | End frame path (for keyframe FFLF) |
| `video_path` | string | `""` | Source video (for extend mode) |
| `extend_frames` | int | 6 | Frames to add when extending |
| `extend_direction` | string | `after` | `after` or `before` |
| `extend_steps` | int | 12 | Steps for extend generation |
| `extend_cfg` | float | 1.0 | CFG for extend mode |
| `keyframes_json` | string | `""` | Multi-keyframe timing data |
| `keyframes_total_frames` | string | `""` | Total frames for keyframe mode |
| `loras` | string | `[]` | JSON array of LoRA IDs |
| `session_tag` | string | `""` | Tag for grouping related jobs |
| `label` | string | null | Human-readable label |
| `stop_comfy` | bool | false | Stop ComfyUI after generation |
| `open_when_done` | bool | false | Open output folder when done |
| `bongmath_max_iter` | int | 100 | Bong math iterations |
| `video_skip_step` | int | 0 | Video skip step |
| `audio_skip_step` | int | 0 | Audio skip step |
| `stage2_image_conditioning` | string | `""` | Image conditioning for stage 2 |

#### Resolution Presets (Common)

| Use Case | Width | Height | Frames | Time |
|----------|-------|--------|--------|------|
| Quick test | 480 | 480 | 37 (~1.5s) | ~2 min |
| Portrait HD | 576 | 1024 | 121 (~5s) | ~8 min |
| Landscape HD | 1024 | 576 | 121 (~5s) | ~8 min |
| Landscape 720p | 1280 | 704 | 121 (~5s) | ~8 min |
| Max (64GB) | 768 | 768 | 121 (~5s) | ~8 min |

### POST /queue/batch — Submit Multiple Jobs

```bash
curl -sSk -X POST \
  -F "batch=prompt1\nprompt2\nprompt3" \
  "https://macbook-pro.tailc4e23e.ts.net:8443/queue/batch"
```

### POST /queue/clear — Clear All Pending Jobs

```bash
curl -sSk -X POST https://macbook-pro.tailc4e23e.ts.net:8443/queue/clear
```

### POST /queue/pause and /queue/resume — Pause/Resume Queue

```bash
curl -sSk -X POST https://macbook-pro.tailc4e23e.ts.net:8443/queue/pause
curl -sSk -X POST https://macbook-pro.tailc4e23e.ts.net:8443/queue/resume
```

### POST /stop — Cancel Current Job

```bash
curl -sSk -X POST https://macbook-pro.tailc4e23e.ts.net:8443/stop
```

### POST /stop_comfy — Stop ComfyUI Backend

```bash
curl -sSk -X POST https://macbook-pro.tailc4e23e.ts.net:8443/stop_comfy
```

### GET /outputs — List Generated Videos

```bash
curl -sSk "https://macbook-pro.tailc4e23e.ts.net:8443/outputs?limit=10&offset=0"
```

**Response fields per output**: `name`, `path`, `mtime`, `size_mb`, `elapsed_sec`, `url`, `has_sidecar`, `hidden`, `kind`

### GET /file — Download a Generated Video

Use the `url` field from `/outputs` or `/status`:

```bash
curl -sSk -o output.mp4 "https://macbook-pro.tailc4e23e.ts.net:8443/file?path=/Users/apple/pinokio/api/phosphene.git/mlx_outputs/filename.mp4&v=TIMESTAMP"
```

### GET /models — Model Status

```bash
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/models
```

Returns repos with `complete`, `present_files`, `missing_files`, `size_gb`.

### POST /models/download — Download Missing Model

```bash
curl -sSk -X POST -d "repo_key=q8" https://macbook-pro.tailc4e23e.ts.net:8443/models/download
```

### POST /models/cancel — Cancel Active Download

```bash
curl -sSk -X POST https://macbook-pro.tailc4e23e.ts.net:8443/models/cancel
```

### GET /settings — Output Settings

```bash
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/settings
```

### POST /settings — Update Settings

```bash
curl -sSk -X POST \
  -F "output_preset=web" \
  -F "memory_policy=safe" \
  "https://macbook-pro.tailc4e23e.ts.net:8443/settings"
```

### GET /characters — List Trained Characters

```bash
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/characters
```

### GET /loras — List Available LoRAs

```bash
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/loras
```

### GET /version — Server Version

```bash
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/version
```

### POST /version/pull — Update Server

```bash
curl -sSk -X POST https://macbook-pro.tailc4e23e.ts.net:8443/version/pull
```

### POST /version/check — Check for Updates

```bash
curl -sSk -X POST https://macbook-pro.tailc4e23e.ts.net:8443/version/check
```

### POST /prompt/enhance — AI-Enhance a Prompt

```bash
curl -sSk -X POST -F "prompt=A cat" https://macbook-pro.tailc4e23e.ts.net:8443/prompt/enhance
```

### GET /uploads — List Uploaded Images

```bash
curl -sSk "https://macbook-pro.tailc4e23e.ts.net:8443/uploads?limit=18"
```

### POST /upload — Upload Image

```bash
curl -sSk -X POST -F "file=@image.png" https://macbook-pro.tailc4e23e.ts.net:8443/upload
```

### POST /train/start — Start Character Training

```bash
curl -sSk -X POST \
  -F "name=MyCharacter" \
  -F "images=@bundle.zip" \
  "https://macbook-pro.tailc4e23e.ts.net:8443/train/start"
```

### GET /train/list — List Training Jobs

```bash
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/train/list
```

### GET /train/dataset — Training Dataset Status

```bash
curl -sSk "https://macbook-pro.tailc4e23e.ts.net:8443/train/dataset?job_id=JOB_ID"
```

---

## Complete Workflow Examples

### Example 1: Quick Test Video (Smallest Possible)

```bash
# Submit minimal job
curl -sSk -X POST \
  -F "mode=t2v" \
  -F "prompt=A single white sphere slowly rotating" \
  -F "width=480" \
  -F "height=480" \
  -F "frames=37" \
  -F "steps=4" \
  -F "quality=quick" \
  -F "accel=turbo" \
  -F "upscale=off" \
  "https://macbook-pro.tailc4e23e.ts.net:8443/queue/add"

# Wait 2-3 minutes, then check
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/status | python3 -m json.tool
```

### Example 2: High-Quality Landscape Video

```bash
curl -sSk -X POST \
  -F "mode=t2v" \
  -F "prompt=Cinematic aerial drone shot of a coastal cliff at golden hour, waves crashing below, volumetric light through sea mist, photorealistic, ARRI Alexa" \
  -F "negative_prompt=cartoon, anime, cgi, low quality, blurry, text, watermark" \
  -F "width=1280" \
  -F "height=704" \
  -F "frames=121" \
  -F "steps=8" \
  -F "quality=balanced" \
  -F "accel=off" \
  -F "upscale=fit_720p" \
  -F "cfg_scale=3.0" \
  "https://macbook-pro.tailc4e23e.ts.net:8443/queue/add"
```

### Example 3: Image-to-Video

```bash
# First upload an image
curl -sSk -X POST -F "file=@my_image.png" \
  "https://macbook-pro.tailc4e23e.ts.net:8443/upload"

# Then submit i2v job (use the uploaded image path from upload response)
curl -sSk -X POST \
  -F "mode=i2v" \
  -F "prompt=The scene comes to life with gentle motion" \
  -F "image=/Users/apple/pinokio/api/phosphene.git/panel_uploads/UPLOADED_FILENAME.png" \
  -F "width=576" \
  -F "height=1024" \
  -F "frames=121" \
  -F "quality=balanced" \
  "https://macbook-pro.tailc4e23e.ts.net:8443/queue/add"
```

### Example 4: Extend an Existing Video

```bash
curl -sSk -X POST \
  -F "mode=extend" \
  -F "video_path=/Users/apple/pinokio/api/phosphene.git/mlx_outputs/existing_video.mp4" \
  -F "extend_frames=6" \
  -F "extend_direction=after" \
  -F "quality=balanced" \
  "https://macbook-pro.tailc4e23e.ts.net:8443/queue/add"
```

### Example 5: Monitor Until Complete

```bash
while true; do
  STATUS=$(curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/status)
  RUNNING=$(echo "$STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin)['running'])")
  if [ "$RUNNING" = "False" ]; then
    echo "Job complete!"
    echo "$STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d['history'][0], indent=2))"
    break
  fi
  PCT=$(echo "$STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); c=d['current']; print(c['progress']['pct'] if c and c.get('progress') else '?')")
  echo "Running... ${PCT}%"
  sleep 10
done
```

### Example 6: Download All Outputs

```bash
curl -sSk "https://macbook-pro.tailc4e23e.ts.net:8443/outputs?limit=100&offset=0" | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
for o in data['outputs']:
    print(f'{o[\"name\"]} ({o[\"size_mb\"]:.1f}MB) — https://macbook-pro.tailc4e23e.ts.net:8443{o[\"url\"]}')
"
```

---

## Pitfalls & Known Issues

1. **FormData only for /queue/add**: The endpoint does NOT accept JSON body. Use `-F` flags
   (multipart/form-data). JSON POST will silently use defaults for all fields.

2. **Default params override**: If you omit fields, Phosphene uses server defaults (1024×576,
   121 frames, balanced quality). Always specify width/height/frames/quality explicitly.

3. **Q8 model not installed**: High quality and FFLF keyframe modes require Q8 (37GB). Only
   download if Mac has storage headroom. Use `/models/download` with `repo_key=q8`.

4. **Model load errors**: First job after idle may fail with "Model not loaded. Call load() first."
   This resolves on retry as the model loads into memory.

5. **Self-signed TLS**: All curl calls need `-k` flag. No way around this without cert trust.

6. **Memory pressure**: 64GB Mac uses ~10GB at idle. Heavy jobs (Q8, high resolution) can push
   memory pressure. Use `memory_policy=safe` if other apps are running.

7. **File paths are Mac-local**: All `image`, `video_path`, `raw_path` values are absolute paths
   on the MacBook. Use `/upload` endpoint to upload files, then reference the returned path.

8. **Queue is FIFO**: Only one job runs at a time. Use `/queue/clear` to cancel pending jobs.

9. **Output filenames**: Generated from prompt text (sanitized). Check `/outputs` for actual names.

10. **Version behind**: Server is v3.2.5, remote is v3.2.6 (30 commits behind). Use
    `/version/pull` to update, but this restarts the server and kills any running job.

---

## Complete Fine-Tuning Reference

### Video Generation — All Tunable Parameters

#### Mode Selection
| Mode | Value | Description |
|------|-------|-------------|
| Text-to-Video | `t2v` | Prompt → video |
| Image-to-Video | `i2v` | Reference image + prompt → video |
| Character | `character` | Trained face + voice |
| First/Last Frame (FFLF) | `keyframe` (kf_mode=2) | Interpolate between start/end images |
| Multi-Keyframe | `keyframe` (kf_mode=multi) | Lock intermediate beats at specific times |
| Extend | `extend` | Add frames to existing video |

#### Quality Tiers
| Tier | Steps | Description | Time (est) |
|------|-------|-------------|------------|
| `quick` | 4 | Fastest, lowest quality | ~2 min |
| `balanced` | 8 | Good balance (default) | ~8 min |
| `standard` | 8 | Same as balanced, labeled differently | ~8 min |
| `high` | 16+ | Best quality, requires Q8 model | ~15 min |

#### Acceleration Modes
| Mode | Value | Description |
|------|-------|-------------|
| Exact | `off` | No acceleration, reference quality |
| Boost | `boost` | TeaCache acceleration, slight quality loss |
| Turbo | `turbo` | Maximum speed, noticeable quality loss |

#### Temporal Modes
| Mode | Value | Description |
|------|-------|-------------|
| Native | `native` | 24 fps native generation |
| 12→24 fps | `fps12_interp24` | Generate at 12 fps, interpolate to 24 |

#### Upscaling
| Mode | Value | Description |
|------|-------|-------------|
| Off | `off` | No upscaling |
| Fit 720p | `fit_720p` | Scale to fit 720p |
| 2x | `x2` | Double resolution |

#### Upscaling Methods
| Method | Value | Description |
|--------|-------|-------------|
| Lanczos | `lanczos` | Standard algorithm |
| PiperSR | `pipersr` | AI super-resolution (slower, better) |

#### Aspect Ratios (Video)
| Ratio | Value | Resolution |
|-------|-------|------------|
| Landscape 16:9 | `landscape` | 1024×576 |
| Vertical 9:16 | `vertical` | 576×1024 |

#### Frame Counts
- Minimum: 1
- Maximum: varies by mode
- Formula: `frames = (seconds × 24) + 1`
- Examples: 37 frames = ~1.5s, 121 frames = ~5s, 241 frames = ~10s

#### Keyframe Options
| Count | Value | Description |
|-------|-------|-------------|
| 3 keyframes | `3` | Minimal interpolation |
| 4 keyframes | `4` | |
| 5 keyframes | `5` | |
| 6 keyframes | `6` | Default |
| 7 keyframes | `7` | |
| 8 keyframes | `8` | Maximum |

#### Extend Options
| Parameter | Values | Description |
|-----------|--------|-------------|
| Direction | `after`, `before` | Where to add frames |
| Duration | 0.5-10 seconds | How much to add |
| Mode | `fast`, `quality` | Speed vs quality tradeoff |

#### Audio Modes (i2v)
| Mode | Value | Description |
|------|-------|-------------|
| Joint Audio | `i2v` | LTX generates audio synced with visual |
| External Audio | `i2v_clean_audio` | Mux external audio file onto video |

#### Other Video Settings
| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `cfg_scale` | float | 3.0 | Classifier-free guidance scale |
| `teacache_thresh` | float | 1.8 | TeaCache threshold |
| `stage1_steps` | int | 10 | First pass denoising steps |
| `stage2_steps` | int | 3 | Second pass denoising steps |
| `enhance` | bool | false | Enhancement pass |
| `hdr` | bool | false | HDR output |
| `no_music` | bool | false | Suppress music in audio |
| `no_voice` | bool | false | Suppress voice in audio |
| `video_skip_step` | int | 0 | Video skip step |
| `audio_skip_step` | int | 0 | Audio skip step |
| `bongmath_max_iter` | int | 100 | Bong math iterations |

### Image Generation — Ideogram 4

**Engine**: `ideogram4_inline` — text-in-image with layout control
**Modes**: Simple (prompt only) or Layout (canvas editor)

#### Ideogram Quality Presets
| Preset | Value | Steps | Speed |
|--------|-------|-------|-------|
| Default | `V4_DEFAULT_20` | 20 | Standard |
| Turbo | `V4_TURBO_12` | 12 | Fast |
| Quality | `V4_QUALITY_48` | 48 | Slow |

#### Image Aspect Ratios
| Ratio | Value | Resolution |
|-------|-------|------------|
| 16:9 | `16:9` | 1280×720 |
| 4:3 | `4:3` | 1024×768 |
| 1:1 | `1:1` | 1024×1024 |
| 9:16 | `9:16` | 720×1280 |
| 3:4 | `3:4` | 768×1024 |
| 21:9 | `21:9` | 1280×544 |
| 16:9 small | `16:9s` | 768×432 |
| 1:1 small | `1:1s` | 512×512 |
| 9:16 small | `9:16s` | 432×768 |

#### Layout Editor — Box Types
| Type | Value | Description |
|------|-------|-------------|
| Text | `text` | Text box with font/style controls |
| Object | `obj` | Region for model to draw something |

#### Text Styles (Font)
| Style | Value | Description |
|-------|-------|-------------|
| Headline | `headline` | Large, bold |
| Subhead | `subhead` | Medium |
| Body | `body` | Standard text |
| Small caps | `caps` | Small capitals |
| Script | `script` | Handwriting style |
| Serif | `serif` | Serif font |

#### Text Alignment
| Align | Value | Description |
|-------|-------|-------------|
| Left | `left` | Left-aligned |
| Center | `center` | Center-aligned |
| Right | `right` | Right-aligned |

#### Render Modes (Ideogram)
| Mode | Value | Description |
|------|-------|-------------|
| Art | `art` | Illustration/artistic style |
| Photo | `photo` | Photorealistic |

#### Color Palette
- Color picker for each box: `ideoPaletteColor`
- Add palette colors: `ideoAddImagePaletteColor()`
- Color names auto-detected from hex values

#### Reference Bridge
- When enabled, describes reference image and adds description to prompt
- Ideogram redraws the idea in its own style
- For faithful copy, use Reference Edit engine instead

### Image Generation — FLUX.1 [dev] (fal.ai) — 3:4 Portraits

**Engine**: `fal-ai/flux/dev` (FLUX.1 [dev], 12B flow transformer) via fal.ai.
Phosphene itself is a video engine; this is the dedicated static-image path,
used for 3:4 psychiatry / mental-health portraits. Full pipeline:
[`IMAGE_GEN_WORKFLOW.md`](../../IMAGE_GEN_WORKFLOW.md).

**Prereqs (one of):**
- `pip install fal-client pillow` + `fal-client login`  (preferred)
- `export FAL_KEY=...` + `pip install requests pillow`  (REST fallback)

**Run:**
```bash
# Curated 3:4 psychiatry set (768x1024), writes manifest.json
./examples/generate_images.sh

# Single image
python3 scripts/image_gen.py \
  --prompt "A calm psychiatric consultation room, warm window light" \
  --name psychiatry_room --out generated_images \
  --width 768 --height 1024
```

**FLUX call shape (fal_client):**
```python
import fal_client
fal_client.run("fal-ai/flux/dev", arguments={
    "prompt": prompt,
    "image_size": {"width": 768, "height": 1024},
    "num_images": 1,
    "output_format": "png",
    "enable_safety_checker": True,
})
```

**Notes:**
- Output is center-cropped to exact 768×1024 (3:4) by `ensure_crop()` regardless of what FLUX returns.
- Prompts ending in "Centered composition, subject fully visible." survive the crop cleanly.
- `prompts/psychiatry.tsv` holds the curated set: therapy session, mindfulness, neuroplasticity.
- Billing: ~$0.025 / megapixel on fal.ai.

### Image Generation — LOCAL Mac (mflux) — 3:4 Portraits

**Engine**: Phosphene's bundled **`mflux`** (Apple-Silicon FLUX port) on the MacBook,
driven over Tailscale. Fully local — no fal.ai key. This is the local counterpart
to the fal.ai path above. Full pipeline: [`LOCAL_IMAGE_GEN_WORKFLOW.md`](../../LOCAL_IMAGE_GEN_WORKFLOW.md).

**Endpoint facts (probed 2026-07-14, Phosphene v3.2.5):**
- Image jobs use the SAME `/queue/add` as video, with `mode=image`.
- `width`/`height`/`aspect_ratio` are **ignored** — output is always `1280x720`.
- Output file: `cand_<rand>_mflux.png`.
- Download via `GET /image?path=<abs>&v=<ts>` — **NOT** `/file` (video-only).
- Self-signed TLS: use `verify=False` / `curl -k`. No auth (Tailscale LAN).

**Run:**
```bash
# Curated 3:4 psychiatry set via the Mac (768x1024, cropped from 1280x720)
./examples/generate_local_images.sh

# Single image
python3 scripts/local_image_gen.py \
  --prompt "A depressed patient on a couch, dim window" \
  --name psychiatry_depressed --out generated_images
```

**Submit (curl):**
```bash
curl -sSk -X POST -d "mode=image" \
  -d "prompt=A calm psychiatry consultation room" \
  "https://macbook-pro.tailc4e23e.ts.net:8443/queue/add"
# → {"ok": true, "id": "j-xxxxxxxxxxxx-012"}
```

**Notes:**
- `scripts/local_image_gen.py` submits, polls `/status`, resolves the `/image` URL from `/outputs`, downloads, and center-crops to exact 768×1024.
- Recorded job IDs live in `generated_images/manifest.local.json`.
- Verified live: produced a real 768×1024 PNG (job `j-19f61f3d006-012`).

#### Fast Mode (M1/M2)
- Quantizes model to 4-bit on load
- Much faster on M1/M2 GPUs
- Clears macOS Metal command-buffer watchdog
- Roughly half the RAM
- Slightly lower quality; leave off on M3/M4

#### Canvas Controls
- Snap to thirds/center/other boxes: `ideoSnapToggle`
- Undo: `ideoUndo()` or Cmd/Ctrl+Z
- Delete box: `ideoDeleteSel()` or Delete key
- Apply JSON edits: `ideoApplyRaw()`

### Reference Edit — Image-to-Image

**Engines** (from fast to slow):
| Engine | Value | Steps | Time | Best For |
|--------|-------|-------|------|----------|
| Fast (Lightning) | `qwen_edit_lightning_inline` | 4 | ~1:20 | Quick iterations, multi-ref |
| Standard (Q6) | `qwen_edit_inline` | 8 | ~2:05 | Balanced, no LoRA |
| Quality (Q8) | `qwen_edit_high_inline` | 40 | ~3:50 | Final renders |

### Character Training

#### Training Presets
| Preset | Value | Description |
|--------|-------|-------------|
| Quick | `quick` | Fast training, lower quality |
| Medium | `medium` | Balanced |
| High | `high` | Best quality, slowest |

#### Character Quality
| Quality | Value | Resolution | Description |
|---------|-------|------------|-------------|
| Draft | `draft` | 736×416 | Faster, slightly less detail |
| Pro | `pro` | 1024×576 | Best identity, production recipe |

#### Training Parameters
| Parameter | Values | Description |
|-----------|--------|-------------|
| Steps | 100-10000 | Training iterations |
| Batch size | 8, 16, 32, 64 | Samples per step |
| Learning rate | 5e-5, 1e-4, 2e-4, 5e-4 | Update magnitude |
| Resolution | 512², 576², 768² | Training image size |
| Caption mode | `user_provided`, `trigger_simple`, `trigger_only` | How captions are handled |

#### Character Skip Step
- `charSkipstepToggle`: Skip certain training steps for faster iteration

### Output Settings

#### Presets
| Preset | Pix Fmt | CRF | Size/5s | Use Case |
|--------|---------|-----|---------|----------|
| Archival | yuv444p | 0 | ~50 MB | Lossless, pro workflows |
| Standard | yuv420p | 18 | ~7 MB | Default, visually lossless |
| Web | yuv420p | 23 | ~3 MB | Mobile, bandwidth-limited |

#### Memory Policies
| Policy | Value | Description |
|--------|-------|-------------|
| Auto | `auto` | Use faster path when headroom exists |
| Fast | `fast` | Spend more unified memory for speed |
| Safe | `safe` | Lower peak memory, streaming VAE decode |

### Prompt Enhancement
- Uses Gemma 3 12B to rewrite prompts in LTX 2.3 training style
- Endpoint: `POST /prompt/enhance`
- Parameter: `prompt` (form-data)

### Negative Prompts — Best Practices
```
blurry, low quality, text, watermark, logo, subtitle, caption,
cartoon, anime, cgi, 3d render, deformed, extra fingers, extra arms,
duplicate people, bad anatomy, distorted face, oversaturated,
flickering, jerky motion, masterpiece, best quality, 8k, 4k,
award winning, highly detailed, beautiful, epic, trending
```

### Batch Mode
- Paste multiple prompts at once
- Endpoint: `POST /queue/batch`
- Parameter: `batch` (newline-separated prompts)

### LoRA Integration
- Available LoRAs: `motion-track`, `union-control`
- Custom LoRAs: place in `/Users/apple/pinokio/api/phosphene.git/mlx_models/loras/`
- Parameter: `loras` (JSON array of LoRA IDs)

### Server Info

- **Install path**: `/Users/apple/pinokio/api/phosphene.git/`
- **Output dir**: `/Users/apple/pinokio/api/phosphene.git/mlx_outputs/`
- **Upload dir**: `/Users/apple/pinokio/api/phosphene.git/panel_uploads/`
- **Model dir**: `/Users/apple/pinokio/api/phosphene.git/mlx_models/`
- **LoRA dir**: `/Users/apple/pinokio/api/phosphene.git/mlx_models/loras/`
- **Q8 model path**: `/Users/apple/pinokio/api/phosphene.git/mlx_models/ltx-2.3-mlx-q8/`
- **Q4 model path**: `mlx_models/ltx-2.3-mlx-q4/`
- **Gemma model path**: `mlx_models/gemma-3-12b-it-4bit/`
- **Pinokio app dir**: `/Users/apple/pinokio/` (parent)
