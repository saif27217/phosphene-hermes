# End-to-End Workflow: Remote Video Generation via Phosphene

Complete walkthrough of discovering, accessing, and using Phosphene for video generation from a remote machine via Tailscale.

## Architecture

```
┌─────────────────────┐     Tailscale      ┌─────────────────────────┐
│  Hermes Agent (VPS) │ ←─────────────────→ │  MacBook Pro (M-series) │
│  100.93.x.x         │    HTTPS :8443      │  Phosphene + Pinokio    │
│                     │                      │  MLX + LTX 2.3          │
└─────────────────────┘                      └─────────────────────────┘
```

## Phase 1: Endpoint Discovery

### Initial Scan
```bash
# Check what's running on the MacBook
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/status
```

### Key Findings
- **Port 8443**: Phosphene web UI (main interface)
- **Port 42003**: Pinokio app browser (app catalog)
- **Port 42005**: Pinokio daemon (localhost only, 403 for remote)

### API Surface Discovery
```bash
# Find all JS files and extract API endpoints
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/ | grep -oP 'src="[^"]*\.js"'
# Socket.js, common.js, layout.js

# Extract fetch/API calls from JS
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/common.js | grep -oP 'fetch\([^)]+\)'
```

### Discovered Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/status` | Server state, queue, history, outputs |
| POST | `/queue/add` | Submit generation job |
| POST | `/queue/batch` | Submit multiple jobs |
| POST | `/queue/clear` | Clear pending jobs |
| POST | `/stop` | Cancel current job |
| GET | `/models` | Model status |
| GET | `/outputs` | List generated videos |
| GET | `/file` | Download video |
| POST | `/upload` | Upload image |
| GET | `/characters` | List trained characters |
| GET | `/loras` | List available LoRAs |
| GET | `/settings` | Output settings |
| GET | `/version` | Server version |

## Phase 2: First Job Submission

### Minimal Test (Quick Quality)
```bash
curl -sSk -X POST \
  -F "mode=t2v" \
  -F "prompt=A single white sphere slowly rotating in dark void" \
  -F "width=480" \
  -F "height=480" \
  -F "frames=37" \
  -F "steps=4" \
  -F "quality=quick" \
  -F "accel=turbo" \
  -F "upscale=off" \
  "https://macbook-pro.tailc4e23e.ts.net:8443/queue/add"

# Response: {"ok": true, "id": "j-19f5f6afc11-001"}
```

### Critical Learning: FormData Only
The `/queue/add` endpoint **does NOT accept JSON**. It requires `multipart/form-data` (use `-F` flags with curl). JSON POST silently uses defaults.

## Phase 3: Monitoring

### Poll Status
```bash
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/status | python3 -c "
import sys, json
data = json.load(sys.stdin)
c = data['current']
p = c.get('progress', {})
print(f'{p.get(\"phase_label\",\"?\")} {p.get(\"pct\",0)}% '
      f'step {p.get(\"denoise_step\",\"?\")}/{p.get(\"denoise_total\",\"?\")} '
      f'ETA: {p.get(\"eta_sec\",0):.0f}s')
"
```

### Background Monitor Script
```bash
while true; do
  STATUS=$(curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/status)
  RUNNING=$(echo "$STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin)['running'])")
  if [ "$RUNNING" = "False" ]; then
    echo "DONE"
    echo "$STATUS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
h = data['history'][0]
print(f'Job: {h[\"id\"]}')
print(f'Status: {h[\"status\"]}')
print(f'Elapsed: {h[\"elapsed_sec\"]:.0f}s')
print(f'Output: {h.get(\"output_path\",\"N/A\")}')
"
    break
  fi
  PCT=$(echo "$STATUS" | python3 -c "
import sys,json
c=json.load(sys.stdin).get('current')
p=c.get('progress',{}) if c else {}
print(f'{p.get(\"phase_label\",\"?\")} {p.get(\"pct\",0)}%')
")
  echo "[$(date +%H:%M:%S)] $PCT"
  sleep 15
done
```

### Progress Phases
1. **setup** — Preparing model
2. **denoising** — Diffusion steps (main generation)
3. **VAE decode + audio mux** — Decoding latent to video
4. **upscale** — Optional upscaling
5. **cleanup** — Finalizing

## Phase 4: Download & Delivery

### Get Output URL
```bash
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/status | python3 -c "
import sys, json
data = json.load(sys.stdin)
for o in data.get('outputs', []):
    print(f'{o[\"name\"]} ({o[\"size_mb\"]:.1f}MB) — https://macbook-pro.tailc4e23e.ts.net:8443{o[\"url\"]}')
"
```

### Download
```bash
curl -sSk -o output.mp4 "https://macbook-pro.tailc4e23e.ts.net:8443/file?path=/path/to/video.mp4&v=TIMESTAMP"
```

### Deliver to Discord
```bash
# Include MEDIA: path in response for native Discord delivery
MEDIA:/tmp/output.mp4
```

## Phase 5: Results

### Our Test Job
```
Job:      j-19f5f6afc11-001
Status:   ✅ done
Time:     394s (6.5 min)
Output:   a_cinematic_atmospheric_scene_2_720p.mp4
Size:     1.8MB
Mode:     t2v (text-to-video)
Settings: 1024×576, 121 frames, balanced quality
```

### All Outputs on MacBook
1. `a_cinematic_atmospheric_scene_2_720p.mp4` — 1.8MB (just generated)
2. `a_psychiatrist_sits_across_from_a_up2x.mp4` — 5.4MB
3. `psychiatrist_taking_therapy_warm_comfortable_scene_v720p.mp4` — 2.3MB
4. `a_cinematic_atmospheric_scene_720p.mp4` — 1.3MB

## Phase 6: Skill Creation

### What Was Built
- **phosphene-hermes** skill (Hermes agent integration)
- **GitHub repo** (saif27217/phosphene-hermes)
- **Example scripts** (quick-test, landscape, portrait, batch, monitor, download)
- **Python wrappers** (generate.py, monitor.py, upload-image.py)

### Skill Structure
```
skills/phosphene-hermes.md
├── API Reference (all endpoints)
├── Generation Modes (t2v, i2v, keyframe, extend, character)
├── Fine-Tuning Parameters (quality, accel, upscale, temporal, CFG)
├── Image Generation (Ideogram 4, Reference Edit)
├── Character Training (presets, caption modes)
├── Output Settings (presets, memory policies)
├── Complete Workflow Examples
├── Pitfalls & Known Issues
└── Server Info (paths, models, versions)
```

## Key Learnings

1. **FormData requirement**: Always use `-F` flags, not JSON
2. **Default params**: Omitting fields uses server defaults (1024×576, 121 frames)
3. **Self-signed TLS**: All curl calls need `-k` flag
4. **Model load errors**: First job after idle may fail; retry resolves it
5. **Queue is FIFO**: One job at a time; use `/queue/clear` to cancel pending
6. **File paths are Mac-local**: Use `/upload` for remote files
7. **Version behind**: v3.2.5 vs v3.2.6; use `/version/pull` to update

## Automation Opportunities

### Future Enhancements
1. **Cron job**: Auto-generate daily videos
2. **Webhook integration**: Trigger generation from Discord commands
3. **Batch pipeline**: Process multiple prompts automatically
4. **Quality presets**: Create custom presets for common use cases
5. **Character training**: Train custom faces for consistent characters
6. **Reference Edit**: Use image-to-image for style transfer
7. **Multi-keyframe**: Complex scene transitions
8. **Extend mode**: Continue existing videos

### Integration Ideas
- **Hermes skill**: Automatic video generation on demand
- **Discord bot**: `/phosphene` command for quick generation
- **Pipeline**: Research → Script → Video → Post
- **Batch processing**: Generate multiple angles/variations

## Files Created

```
phosphene-hermes/
├── README.md                           # Full documentation
├── WORKFLOW.md                         # This file
├── skills/
│   └── phosphene-hermes.md            # Complete API reference
├── examples/
│   ├── quick-test.sh                  # Minimal test video
│   ├── landscape.sh                   # HD landscape video
│   ├── portrait.sh                    # Portrait video
│   ├── batch-prompt.sh               # Batch generation
│   ├── monitor.sh                     # Wait for completion
│   └── download-all.sh               # Download all outputs
└── scripts/
    ├── generate.py                    # Python wrapper
    ├── monitor.py                     # Job monitoring
    └── upload-image.py               # Image upload helper
```

## Repository

**GitHub**: https://github.com/saif27217/phosphene-hermes

Pushed with all skills, scripts, examples, and documentation.
