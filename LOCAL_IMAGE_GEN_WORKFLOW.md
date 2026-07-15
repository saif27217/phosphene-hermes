# LOCAL_IMAGE_GEN_WORKFLOW — Generate 3:4 Psychiatry Images via the LOCAL Mac Endpoint

End-to-end pipeline for generating **true 3:4 portrait images** of a
psychiatry / mental-health theme **entirely on Sak's local hardware** — the
MacBook Pro running [Phosphene](./skills/phosphene-hermes.md) (Apple Silicon,
Tailscale). Phosphene runs **FLUX via `mflux`** (the Apple-Silicon FLUX port)
for still images, driven through its REST API.

> This is the **local** counterpart to [`IMAGE_GEN_WORKFLOW.md`](./IMAGE_GEN_WORKFLOW.md),
> which generates the same 3:4 images via **fal.ai FLUX.1 [dev] (cloud)**.
> Same prompts, same 768×1024 output — different backend. Use the local one
> when you want images generated on your own Mac (no cloud key, private).

> **Why 3:4?** Requested by Sak. The Mac image endpoint **honors the `aspect`
> param** — `aspect=3:4` yields a **native 768×1024** image directly (verified
> 2026-07-14: model `Runpod/FLUX.2-klein-4B-mflux-4bit`, output `768×1024`).
> No cropping is needed. `scripts/local_image_gen.py` sets `aspect=3:4` on
> submit; the built-in `ensure_crop()` is retained only as a safety net if the
> endpoint ever returns a non-3:4 size. (`width`/`height` params are ignored —
> aspect ratio drives the dimensions: `9:16`→720×1280, `1:1`→1024×1024,
> `16:9`→1280×720.)

---

## 1. Prerequisites

- **Mac reachable** on Tailscale at `https://macbook-pro.tailc4e23e.ts.net:8443`
  (self-signed cert — the script accepts it automatically; `curl` needs `-k`).
- **Phosphene running** (check: `curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/status`)
- **Python 3 + Pillow** on the *client* machine (does the crop):
  ```bash
  pip install pillow
  ```
- **No API key** — image generation is on the LAN (Tailscale). The script uses
  `verify=False` for the self-signed cert.

---

## 2. The Pipeline (3 steps)

```bash
cd phosphene-hermes

# 1. prompts/psychiatry_local.tsv  (name<TAB>prompt) — curated set included

# 2. Generate on the Mac  →  submits, polls, downloads, crops to 768x1024
./examples/generate_local_images.sh

# 3. Output in generated_images/
#    psychiatry_therapy_session_local.png   (768x1024)
#    psychiatry_depressed_local.png         (768x1024)
#    psychiatry_recovery_local.png          (768x1024)
#    manifest.local.json                    (metadata + job IDs)
```

### Single image
```bash
python3 scripts/local_image_gen.py \
  --prompt "A calm psychiatric consultation room, warm window light" \
  --name psychiatry_room \
  --out generated_images
```

### Prompt enhancement (`--enhance`)
```bash
# Concrete subjects: deterministic FLUX-framework expansion (no LLM needed)
python3 scripts/local_image_gen.py --enhance --prompt "a red apple on white"

# Abstract/conceptual subjects (cognitive dissonance, patient getting better):
# enhance with the `image-prompt-enhancer` skill first, or pass a structured prompt.
# `--enhance` auto-skips prompts that already look enhanced.
```
**Caveat (verified live 2026-07-14):** the template-based `--enhance` cannot
invent concept-specific visual metaphors for abstract prompts — an LLM is
required. For those, let the agent expand via `image-prompt-enhancer` before
submitting.

### Different Mac host
```bash
BASE_URL=https://other-host.tailc4e23e.ts.net:8443 \
  ./examples/generate_local_images.sh
```

---

## 3. How It Works (call chain)

```
prompts/psychiatry_local.tsv
        │  (TSV: name<TAB>prompt)
        ▼
examples/generate_local_images.sh
        │  sets BASE_URL + OUT, calls python
        ▼
scripts/local_image_gen.py
        │  1. reachability check      GET  /status
        │  2. submit job              POST /queue/add  (mode=image, prompt)
        │  3. poll                    GET  /status      (loop until not running)
        │  4. find output_path        (history[].output_path for our job_id)
        │  5. resolve download URL    GET  /outputs      (match path -> url)
        │  6. download PNG            GET  /image?path=<p>&v=<ts>   (binary)
        │  7. ensure_crop()           center-crop 1280x720 -> 768x1024 (3:4)
        │  8. write <name>.png
        ▼
generated_images/
   psychiatry_therapy_session_local.png
   psychiatry_depressed_local.png
   psychiatry_recovery_local.png
   manifest.local.json
```

---

## 4. Endpoint Facts (probed 2026-07-14, Phosphene v3.2.5)

These were **reverse-engineered from the live server** (the repo docs only
cover video modes). They are the contract `scripts/local_image_gen.py` relies on:

| Fact | Value |
|------|-------|
| Submit image job | `POST /queue/add` with `mode=image` (same endpoint as video) |
| **`aspect` param** | **Honored** — `aspect=3:4` → native `768×1024`; `9:16`→720×1280; `1:1`→1024×1024; `16:9`→1280×720 |
| `width` / `height` params | **Ignored** — aspect ratio drives dimensions |
| `seed` param | Honored (recorded per job; `-1` = random) |
| `n` / `num_images` | Per job caps at 1; submit multiple jobs for a batch |
| Model (auto) | `Runpod/FLUX.2-klein-4B-mflux-4bit` (mflux = Apple FLUX port) |
| Output filename | `cand_<rand>_mflux.png` |
| Download endpoint | `GET /image?path=<abs path>&v=<timestamp>` (**not** `/file`) |
| `/file` endpoint | Video-only (returns 404 for images) |
| TLS | Self-signed — accept with `verify=False` / `curl -k` |
| Auth | None (Tailscale LAN) |

**Submit example (curl):**
```bash
curl -sSk -X POST \
  -d "mode=image" \
  -d "prompt=A depressed patient on a couch" \
  "https://macbook-pro.tailc4e23e.ts.net:8443/queue/add"
# → {"ok": true, "id": "j-xxxxxxxxxxxx-012"}
```

**Poll until done:**
```bash
curl -sSk https://macbook-pro.tailc4e23e.ts.net:8443/status | python3 -c "import sys,json;print(json.load(sys.stdin)['running'])"
```

**Resolve + download:**
```bash
# /outputs gives the url field for each image
URL=$(curl -sSk "https://macbook-pro.tailc4e23e.ts.net:8443/outputs?limit=10" | python3 -c "import json,sys;print(json.load(sys.stdin)['outputs'][0]['url'])")
curl -sSk "https://macbook-pro.tailc4e23e.ts.net:8443$URL" -o image.png
```

---

## 5. Prompt Templates (psychiatry theme)

Curated set in `prompts/psychiatry_local.tsv`:

| File | Theme |
|------|-------|
| `psychiatry_therapy_session_local.png` | Therapist + client, warm room, neural-network glow |
| `psychiatry_depressed_local.png` | Depressed patient on a couch, dim window, dignity |
| `psychiatry_recovery_local.png` | Person recovering, window + growing plant, warm light |

Each prompt ends with `Centered composition, subject fully visible.` so the
3:4 crop never clips the subject.

---

## 6. Custom Prompts

```bash
cat > prompts/custom_local.tsv <<'EOF'
# name    prompt
my_scene    A psychiatrist's desk with notebook and plant, soft morning light
EOF

./examples/generate_local_images.sh --prompts prompts/custom_local.tsv
```
Or JSON: `[{"name":"a","prompt":"..."}, ...]`

---

## 7. Output: manifest.local.json

```json
{
  "generated_at": "2026-07-14T18:46:36+00:00",
  "source": "phosphene-mac-mflux",
  "base_url": "https://macbook-pro.tailc4e23e.ts.net:8443",
  "native_size": "1280x720",
  "default_size": {"width": 768, "height": 1024},
  "images": [
    {"name": "psychiatry_recovery_mac", "prompt": "...", "path": "generated_images/psychiatry_recovery_mac.png",
     "width": 768, "height": 1024, "job_id": "j-19f61f3d006-012",
     "source": "phosphene-mac-mflux", "native_size": "1280x720"}
  ]
}
```

---

## 8. Cloud vs Local — Which to use?

| | Local (`LOCAL_IMAGE_GEN_WORKFLOW`) | Cloud (`IMAGE_GEN_WORKFLOW`) |
|---|---|---|
| Backend | Phosphene `mflux` on your Mac | fal.ai `fal-ai/flux/dev` |
| Needs | Tailscale + Mac on | fal.ai key (`fal_client`/`FAL_KEY`) |
| Privacy | Fully local | Goes to fal.ai |
| Native size | 1280×720 (cropped to 3:4) | exact 768×1024 |
| Speed | ~30–60s/job (M-series) | depends on fal.ai queue |
| Script | `scripts/local_image_gen.py` | `scripts/image_gen.py` |

---

## 9. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `cannot reach <base_url>` | Mac offline / Tailscale down. `curl -sSk <base_url>/status` to debug |
| Job hangs `Loading pipeline` | First job after idle reloads model; wait, or retry |
| Download returns HTML/404 | Use `/image?path=..&v=..` not `/file` (image vs video) |
| Output not 3:4 | `ensure_crop()` always produces 768×1024; re-run |
| `No module named PIL` | `pip install pillow` on the client |

---

## 10. Repo Layout (local workflow files)

```
phosphene-hermes/
├── LOCAL_IMAGE_GEN_WORKFLOW.md     # This file
├── IMAGE_GEN_WORKFLOW.md           # Cloud (fal.ai) counterpart
├── prompts/
│   ├── psychiatry.tsv              # Cloud prompts
│   └── psychiatry_local.tsv        # Local prompts (this workflow)
├── scripts/
│   ├── local_image_gen.py          # Mac/Phosphene FLUX generator (this workflow)
│   └── image_gen.py                # fal.ai FLUX generator (cloud counterpart)
├── examples/
│   ├── generate_local_images.sh    # Wrapper (this workflow)
│   └── generate_images.sh          # Cloud wrapper
└── generated_images/
    ├── psychiatry_recovery_mac.png  # real output, generated via this workflow
    ├── manifest.local.json          # local run metadata
    └── ...                          # cloud outputs + manifest.json
```

---

## 11. Notes

- **Model:** FLUX via `mflux` (Apple-Silicon FLUX port) on the Mac.
- **Crop:** `ensure_crop()` center-crops the largest 3:4 window from 1280×720
  then resizes to 768×1024 with LANCZOS — never distorts aspect ratio.
- **Job IDs:** recorded in `manifest.local.json` for traceability.
- **Idempotent:** re-running overwrites `<name>.png` and refreshes the manifest.
- **Verified:** `scripts/local_image_gen.py` was run live against the Mac on
  2026-07-14 and produced a real 768×1024 PNG (job `j-19f61f3d006-012`).
