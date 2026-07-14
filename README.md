# Phosphene-Hermes

Comprehensive API guide and scripts for **Phosphene** — an MLX-accelerated text/image-to-video generation engine running on Apple Silicon via Tailscale.

## What is Phosphene?

Phosphene is a self-hosted video generation tool that uses:
- **LTX 2.3** (latent video diffusion model) — generates videos from prompts
- **Gemma 3 12B** (4-bit text encoder) — encodes prompts for diffusion
- **MLX** (Apple's ML framework) — Metal GPU acceleration on Mac

It runs on a MacBook Pro (64GB M-series) and is accessible via Tailscale.

## Quick Start

### Prerequisites
- MacBook Pro with Apple Silicon (M1/M2/M3/M4)
- Tailscale installed and connected
- Phosphene installed via Pinokio

### Access
```bash
# Base URL (Tailscale)
BASE_URL="https://macbook-pro.tailc4e23e.ts.net:8443"

# Check server status
curl -sSk "$BASE_URL/status" | python3 -m json.tool

# Generate a video
curl -sSk -X POST \
  -F "mode=t2v" \
  -F "prompt=A serene mountain landscape at sunset" \
  -F "width=576" \
  -F "height=1024" \
  -F "frames=121" \
  -F "quality=balanced" \
  "$BASE_URL/queue/add"
```

## Image Generation — Two Backends

Phosphene itself is a **video** engine (LTX 2.3). For still 3:4 portrait images
we run **FLUX** two ways:

1. **Local (your Mac)** — Phosphene's bundled `mflux` (Apple-Silicon FLUX),
   driven over Tailscale. Private, no cloud key. → [`LOCAL_IMAGE_GEN_WORKFLOW.md`](./LOCAL_IMAGE_GEN_WORKFLOW.md)
   (`scripts/local_image_gen.py`, `examples/generate_local_images.sh`)
2. **Cloud (fal.ai)** — `fal-ai/flux/dev`, exact 768×1024, clean frames.
   → [`IMAGE_GEN_WORKFLOW.md`](./IMAGE_GEN_WORKFLOW.md)
   (`scripts/image_gen.py`, `examples/generate_images.sh`)

Both emit true 3:4 (768×1024) PNGs + a manifest. Same prompt format
(`prompts/*.tsv`: `name<TAB>prompt`). The local Mac endpoint emits 1280×720,
so the local script center-crops to 3:4.

```bash
# Local (Mac)
./examples/generate_local_images.sh
# Cloud (fal.ai)
./examples/generate_images.sh
```

## Repository Structure

```
phosphene-hermes/
├── README.md                    # This file
├── IMAGE_GEN_WORKFLOW.md        # FLUX.1 [dev] (fal.ai cloud) 3:4 image generation
├── LOCAL_IMAGE_GEN_WORKFLOW.md  # FLUX via local Mac/Phosphene (mflux) 3:4 image generation
├── IMAGE_TO_VIDEO_WORKFLOW.md   # Image → Video via Phosphene (LTX)
├── skills/
│   ├── phosphene-hermes.md      # Full API reference (Hermes skill)
│   └── video-prompt-enhancer.md # Cinematic prompt framework
├── prompts/
│   ├── psychiatry.tsv           # Cloud image prompts
│   └── psychiatry_local.tsv     # Local (Mac) image prompts
├── examples/
│   ├── generate_images.sh        # fal.ai FLUX image wrapper
│   ├── generate_local_images.sh  # Local Mac FLUX image wrapper
│   ├── quick-test.sh            # Minimal test video
│   ├── landscape.sh             # High-quality landscape
│   ├── portrait.sh              # Portrait video
│   ├── batch-prompt.sh          # Batch generation
│   ├── monitor.sh               # Wait for job completion
│   └── download-all.sh          # Download all outputs
├── scripts/
│   ├── image_gen.py             # Python wrapper for fal.ai FLUX image generation
│   ├── local_image_gen.py       # Python wrapper for local Mac/Phosphene FLUX generation
│   ├── generate.py              # Python wrapper for Phosphene video generation
│   ├── monitor.py               # Job monitoring script
│   └── upload-image.py          # Image upload helper
└── generated_images/            # FLUX outputs (3:4 PNGs + manifest*.json)
```

## API Endpoints

### Core Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/status` | Server state, queue, history, outputs |
| POST | `/queue/add` | Submit generation job (FormData) |
| POST | `/queue/batch` | Submit multiple jobs |
| POST | `/queue/clear` | Clear pending jobs |
| POST | `/queue/pause` | Pause queue |
| POST | `/queue/resume` | Resume queue |
| POST | `/stop` | Cancel current job |

### Image Generation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload image |
| GET | `/uploads` | List uploaded images |
| POST | `/prompt/enhance` | AI-enhance prompt with Gemma |

### Character Training
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/train/start` | Start training |
| GET | `/train/list` | List training jobs |
| GET | `/train/dataset` | Dataset status |
| POST | `/train/upload` | Upload training images |
| POST | `/train/upload-voice` | Upload voice samples |

### Models & Settings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/models` | Model status |
| POST | `/models/download` | Download model |
| GET | `/settings` | Output settings |
| POST | `/settings` | Update settings |
| GET | `/loras` | List LoRAs |

### Outputs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/outputs` | List generated videos |
| GET | `/file` | Download video |
| POST | `/output/delete` | Delete output |
| POST | `/output/hide` | Hide output |

## Generation Modes

### Text-to-Video (`t2v`)
```bash
curl -sSk -X POST \
  -F "mode=t2v" \
  -F "prompt=A cinematic drone shot of a coastal cliff" \
  -F "negative_prompt=blurry, low quality, text" \
  -F "width=1280" \
  -F "height=704" \
  -F "frames=121" \
  -F "steps=8" \
  -F "quality=balanced" \
  -F "accel=off" \
  -F "upscale=fit_720p" \
  "$BASE_URL/queue/add"
```

### Image-to-Video (`i2v`)
```bash
# First upload image
curl -sSk -X POST -F "file=@image.png" "$BASE_URL/upload"

# Then submit job
curl -sSk -X POST \
  -F "mode=i2v" \
  -F "prompt=The scene comes to life" \
  -F "image=/path/to/uploaded.png" \
  -F "width=576" \
  -F "height=1024" \
  -F "frames=121" \
  "$BASE_URL/queue/add"
```

### Keyframe Interpolation (`keyframe`)
```bash
curl -sSk -X POST \
  -F "mode=keyframe" \
  -F "start_image=/path/to/start.png" \
  -F "end_image=/path/to/end.png" \
  -F "frames=121" \
  "$BASE_URL/queue/add"
```

### Extend Video (`extend`)
```bash
curl -sSk -X POST \
  -F "mode=extend" \
  -F "video_path=/path/to/video.mp4" \
  -F "extend_frames=6" \
  -F "extend_direction=after" \
  "$BASE_URL/queue/add"
```

## Quality Presets

| Quality | Steps | Time | Use Case |
|---------|-------|------|----------|
| `quick` | 4 | ~2 min | Testing, iteration |
| `balanced` | 8 | ~8 min | General use |
| `standard` | 8 | ~8 min | Same as balanced |
| `high` | 16+ | ~15 min | Final renders (requires Q8) |

## Acceleration Modes

| Mode | Value | Description |
|------|-------|-------------|
| Exact | `off` | No acceleration |
| Boost | `boost` | TeaCache (slight quality loss) |
| Turbo | `turbo` | Maximum speed |

## Upscaling

| Mode | Value | Description |
|------|-------|-------------|
| Off | `off` | No upscaling |
| 720p | `fit_720p` | Scale to fit 720p |
| 2x | `x2` | Double resolution |

Methods: `lanczos` (standard), `pipersr` (AI super-resolution)

## Frame Calculation

Formula: `frames = (seconds × 24) + 1`

| Duration | Frames |
|----------|--------|
| 1.5s | 37 |
| 5s | 121 |
| 10s | 241 |

## Image Generation (Ideogram 4)

### Quality Presets
| Preset | Steps | Speed |
|--------|-------|-------|
| Default | 20 | Standard |
| Turbo | 12 | Fast |
| Quality | 48 | Slow |

### Render Modes
- `art` — Illustration/artistic style
- `photo` — Photorealistic

### Layout Editor
- Text boxes: headline, subhead, body, caps, script, serif
- Object regions: draw areas for model
- Alignment: left, center, right
- Colors: per-box palette

## Reference Edit (Image-to-Image)

| Engine | Steps | Time | Use Case |
|--------|-------|------|----------|
| Fast (Lightning) | 4 | ~1:20 | Quick iterations |
| Standard (Q6) | 8 | ~2:05 | Balanced |
| Quality (Q8) | 40 | ~3:50 | Final renders |

## Character Training

### Presets
| Preset | Resolution | Steps |
|--------|------------|-------|
| Quick | 512² | 100-1000 |
| Medium | 576² | 1000-5000 |
| High | 768² | 5000-10000 |

### Caption Modes
- `user_provided` — Use your own captions
- `trigger_simple` — `<trigger> man/woman` format
- `trigger_only` — Trigger word only

## Output Settings

| Preset | Codec | CRF | Size/5s |
|--------|-------|-----|---------|
| Archival | yuv444p | 0 | ~50 MB |
| Standard | yuv420p | 18 | ~7 MB |
| Web | yuv420p | 23 | ~3 MB |

## Memory Policies

| Policy | Description |
|--------|-------------|
| `auto` | Use faster path when headroom exists |
| `fast` | Spend more unified memory for speed |
| `safe` | Lower peak memory, streaming VAE decode |

## Models

| Key | Name | Size | Status |
|-----|------|------|--------|
| `q4` | LTX 2.3 Q4 (base) | 20 GB | ✅ Installed |
| `gemma` | Gemma 3 12B (text encoder) | 6 GB | ✅ Installed |
| `q8` | LTX 2.3 Q8 (high-quality) | 37 GB | ❌ Not installed |

## LoRAs

| ID | Name | Description |
|----|------|-------------|
| `motion-track` | Motion Track Control | Motion-tracked control |
| `union-control` | Union Control | Multi-control (depth, edges, pose) |

Custom LoRAs go in: `/Users/apple/pinokio/api/phosphene.git/mlx_models/loras/`

## Pitfalls

1. **FormData only**: `/queue/add` requires multipart/form-data, not JSON
2. **Default params**: Omitting fields uses server defaults (1024×576, 121 frames)
3. **Q8 not installed**: High quality and FFLF require Q8 (37GB)
4. **Model load errors**: First job after idle may fail; retry resolves it
5. **Self-signed TLS**: All curl calls need `-k` flag
6. **Memory pressure**: Heavy jobs can push memory; use `memory_policy=safe`
7. **File paths**: All paths are Mac-local; use `/upload` for remote files
8. **Queue is FIFO**: One job at a time; use `/queue/clear` to cancel pending
9. **Version behind**: v3.2.5 vs v3.2.6; use `/version/pull` to update

## License

MIT

## Author

Sak (Dr. Saif) — [GitHub](https://github.com/skywalkerxz)
