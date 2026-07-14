# IMAGE_GEN_WORKFLOW — FLUX.1 [dev] 3:4 Psychiatry / Mental-Health Images

End-to-end pipeline for generating **true 3:4 portrait images** of a
psychiatry / mental-health theme using **FLUX.1 [dev]** on
[fal.ai](https://fal.ai/models/fal-ai/flux/dev).

This workflow complements the existing Phosphene **video** workflows
(`IMAGE_TO_VIDEO_WORKFLOW.md`, etc.). Phosphene itself is a video engine
(LTX 2.3) running on the MacBook; the image path below uses a separate,
purpose-built image model (FLUX) because it produces cleaner static frames
and supports exact resolution control.

> **Why 3:4?** Requested by Sak. All outputs are guaranteed 768×1024 (3:4).
> The script center-crops whatever FLUX returns so the ratio is always exact,
> even if the backend resamples.

---

## 1. Prerequisites

Pick **one** of two auth backends (the script auto-selects):

**A. fal_client (recommended)**
```bash
pip install fal-client
fal-client login          # stores ~/.falcredentials.json
```

**B. REST + FAL_KEY**
```bash
export FAL_KEY="your-fal-key"   # from https://fal.ai/dashboard/keys
# requests is the only dependency:
pip install requests pillow
```

Both backends additionally require **Pillow** (for the 3:4 crop):
```bash
pip install pillow
```

---

## 2. The Pipeline (3 steps)

```bash
# 0. From repo root
cd phosphene-hermes

# 1. Define prompts  (prompts/psychiatry.tsv:  name<TAB>prompt)
#    Three curated psychiatry prompts are already included.

# 2. Generate  →  downloads FLUX images, crops to 768x1024, writes manifest
./examples/generate_images.sh

# 3. Output lands in generated_images/
#    psychiatry_therapy_session.png   (768x1024)
#    psychiatry_mindfulness.png       (768x1024)
#    psychiatry_neuroplasticity.png   (768x1024)
#    manifest.json                    (metadata for every image)
```

### Direct Python usage (single image)
```bash
python3 scripts/image_gen.py \
  --prompt "A calm psychiatric consultation room, warm window light" \
  --name psychiatry_room \
  --out generated_images \
  --width 768 --height 1024
```

### Deterministic (fixed seed)
```bash
./examples/generate_images.sh --seed 42
```

---

## 3. How It Works (call chain)

```
prompts/psychiatry.tsv
        │  (TSV: name<TAB>prompt)
        ▼
examples/generate_images.sh
        │  sets OUT + PROMPTS_FILE, calls python
        ▼
scripts/image_gen.py
        │  1. load_prompts()        → [(name, prompt), ...]
        │  2. backend auto-select   → fal_client | requests
        │  3. fal-ai/flux/dev run   → image bytes (PNG)
        │  4. ensure_crop()         → center-crop to exact 768x1024
        │  5. write <name>.png
        ▼
generated_images/
   psychiatry_therapy_session.png
   psychiatry_mindfulness.png
   psychiatry_neuroplasticity.png
   manifest.json
```

**FLUX call shape (fal_client backend):**
```python
fal_client.run("fal-ai/flux/dev", arguments={
    "prompt": prompt,
    "image_size": {"width": 768, "height": 1024},
    "num_images": 1,
    "output_format": "png",
    "enable_safety_checker": True,
})
```

**FLUX call shape (requests backend):**
```bash
POST https://queue.fal.run/fal-ai/flux/dev/requests
Authorization: Key $FAL_KEY
{
  "prompt": "...",
  "image_size": {"width": 768, "height": 1024},
  "num_images": 1,
  "output_format": "png"
}
# then poll .../requests/{id}/status until COMPLETED
```

---

## 4. Prompt Templates (psychiatry theme)

The curated set in `prompts/psychiatry.tsv`:

| File | Theme |
|------|-------|
| `psychiatry_therapy_session.png` | Therapist + client in a warm, safe room; subtle neural-network glow |
| `psychiatry_mindfulness.png` | Person meditating by a window; brain silhouette of calm light |
| `psychiatry_neuroplasticity.png` | Brain of light cradled by caring hands — hope / healing |

Each prompt is engineered to:
- stay **bright / warm / indoor** (cleaner FLUX output, no dark-scene artifacts),
- keep the **subject centered and fully visible** so the 3:4 crop never clips it,
- end with **"Centered composition, subject fully visible."** as a crop safeguard.

---

## 5. Custom Prompts

Create your own TSV (`name<TAB>prompt`, `#` for comments):
```bash
cat > prompts/custom.tsv <<'EOF'
# name    prompt
my_scene    A psychiatrist's desk with a notebook and a small plant, soft morning light
EOF

./examples/generate_images.sh --prompts prompts/custom.tsv --out generated_images
```
Or a JSON list:
```json
[{"name": "a", "prompt": "..."}, {"name": "b", "prompt": "..."}]
```

---

## 6. Output: manifest.json

```json
{
  "generated_at": "2026-07-14T18:05:00+00:00",
  "model": "fal-ai/flux/dev",
  "backend": "fal_client",
  "default_size": {"width": 768, "height": 1024},
  "images": [
    {"name": "psychiatry_therapy_session", "prompt": "...", "path": "generated_images/psychiatry_therapy_session.png", "width": 768, "height": 1024, "seed": 123, "model": "fal-ai/flux/dev"}
  ]
}
```

---

## 7. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: fal_client` | `pip install fal-client` **or** set `FAL_KEY` for the requests backend |
| `FAL_KEY env var not set` | `export FAL_KEY=*****` (requests backend only) |
| Image ratio is not exactly 3:4 | `ensure_crop()` always center-crops to 768×1024; re-run, the script is idempotent on size |
| Subject clipped in crop | Add "Centered composition, subject fully visible." to the prompt; FLUX centers by default |
| `Pillow` missing | `pip install pillow` (needed for the crop step) |

---

## 8. Repo Layout (after this workflow)

```
phosphene-hermes/
├── IMAGE_GEN_WORKFLOW.md          # This file
├── IMAGE_TO_VIDEO_WORKFLOW.md     # (existing) FLUX-via-Phosphene video path
├── README.md                      # updated with IMAGE_GEN section
├── prompts/
│   └── psychiatry.tsv             # curated 3:4 psychiatry prompts
├── scripts/
│   ├── image_gen.py               # FLUX.1 [dev] generator (this workflow)
│   ├── generate.py                # (existing) Phosphene video generator
│   ├── monitor.py                 # (existing) Phosphene job monitor
│   └── upload-image.py            # (existing) Phosphene image upload
├── examples/
│   ├── generate_images.sh         # (new) wrapper for this workflow
│   ├── quick-test.sh              # (existing) video
│   ├── portrait.sh                # (existing) video
│   └── ...
└── generated_images/              # produced by this workflow (gitignored or committed)
    ├── psychiatry_therapy_session.png
    ├── psychiatry_mindfulness.png
    ├── psychiatry_neuroplasticity.png
    └── manifest.json
```

---

## 9. Notes

- **Model:** FLUX.1 [dev] (12B flow transformer). Billed ~$0.025 / megapixel on fal.ai.
- **Safety checker:** enabled by default (`enable_safety_checker: true`).
- **Idempotent:** re-running overwrites `<name>.png` and refreshes `manifest.json`.
- **Video bridge:** any of these 3:4 PNGs can be fed into Phosphene's `i2v`
  mode (`IMAGE_TO_VIDEO_WORKFLOW.md`) as a reference frame for a clips.
