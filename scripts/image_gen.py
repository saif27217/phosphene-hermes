#!/usr/bin/env python3
"""
image_gen.py — End-to-end FLUX.1 [dev] image generation for the Phosphene-Hermes repo.

Generates 3:4 portrait images (default 768x1024) of a psychiatry / mental-health
theme via fal.ai, downloads them, guarantees a true 3:4 crop, and writes a manifest.

Backend: fal.ai  model: fal-ai/flux/dev  (FLUX.1 [dev], 12B flow transformer)

Two backends are supported, auto-selected:
  1. fal_client           — preferred (pip install fal-client)
  2. requests REST        — fallback if fal_client is missing, uses FAL_KEY

Usage
-----
  # Single prompt
  python3 image_gen.py --prompt "A calm therapy room, warm light" \
      --name psychiatry_room --out generated_images

  # Batch from a prompts file (TSV: name<TAB>prompt, or JSON list)
  python3 image_gen.py --prompts prompts/psychiatry.tsv --out generated_images

  # Override size (still center-cropped to the requested 3:4 ratio)
  python3 image_gen.py --prompt "..." --width 768 --height 1024

Auth
----
  fal_client: logged in via `fal-client login` (stores ~/.falcredentials.json)
  requests REST: FAL_KEY env var (export FAL_KEY=****)

Outputs
-------
  <out>/<name>.png            the 3:4 image
  <out>/manifest.json         {generated_at, model, params, images:[...]}
"""

import argparse
import base64
import datetime as dt
import json
import os
import sys
import time

try:
    from PIL import Image
    _HAVE_PIL = True
except ImportError:
    _HAVE_PIL = False

MODEL_ID = "fal-ai/flux/dev"
DEFAULT_W, DEFAULT_H = 768, 1024


# --------------------------------------------------------------------------- #
# Prompt loading
# --------------------------------------------------------------------------- #
def load_prompts(path):
    """Load a batch of prompts from a TSV or JSON file.

    TSV format (no header):  name<TAB>prompt
    JSON format:             [{"name": "...", "prompt": "..."}, ...]  OR  ["prompt1", ...]
    Returns a list of (name, prompt) tuples.
    """
    items = []
    with open(path, "r", encoding="utf-8") as fh:
        if path.endswith(".json"):
            data = json.load(fh)
            if isinstance(data, list):
                for i, entry in enumerate(data):
                    if isinstance(entry, str):
                        items.append((f"image_{i+1:02d}", entry))
                    else:
                        items.append((entry.get("name", f"image_{i+1:02d}"),
                                      entry.get("prompt", "")))
            else:
                raise ValueError("JSON prompts file must be a list")
        else:  # TSV
            for line in fh:
                line = line.rstrip("\n")
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) >= 2:
                    items.append((parts[0].strip(), parts[1].strip()))
                else:
                    items.append((f"image_{len(items)+1:02d}", parts[0].strip()))
    if not items:
        raise ValueError("No prompts found in %s" % path)
    return items


# --------------------------------------------------------------------------- #
# Crop helper — guarantee exact 3:4 dimensions
# --------------------------------------------------------------------------- #
def ensure_crop(image_bytes, width, height):
    """Return cropped image bytes at exactly (width, height), center-cropped."""
    if not _HAVE_PIL:
        return image_bytes  # can't crop without PIL; return as-is
    im = Image.open(__import__("io").BytesIO(image_bytes)).convert("RGB")
    if (im.width, im.height) == (width, height):
        out = __import__("io").BytesIO()
        im.save(out, format="PNG")
        return out.getvalue()
    left = max(0, (im.width - width) // 2)
    top = max(0, (im.height - height) // 2)
    right = min(im.width, left + width)
    bottom = min(im.height, top + height)
    crop = im.crop((left, top, right, bottom))
    # if source is smaller, the crop is already padded by convert('RGB'); resize to target
    if crop.size != (width, height):
        crop = crop.resize((width, height), Image.LANCZOS)
    out = __import__("io").BytesIO()
    crop.save(out, format="PNG")
    return out.getvalue()


# --------------------------------------------------------------------------- #
# Backend: fal_client
# --------------------------------------------------------------------------- #
def gen_fal_client(prompt, width, height, seed, num_images):
    import fal_client
    kwargs = {
        "prompt": prompt,
        "image_size": {"width": width, "height": height},
        "num_images": num_images,
        "output_format": "png",
        "enable_safety_checker": True,
    }
    if seed is not None:
        kwargs["seed"] = seed
    result = fal_client.run(MODEL_ID, arguments=kwargs)
    return result  # {"images":[{"url":...}], "seed":..., "prompt":...}


# --------------------------------------------------------------------------- #
# Backend: requests REST (FAL_KEY)
# --------------------------------------------------------------------------- #
def gen_requests(prompt, width, height, seed, num_images):
    import requests

    api_key = os.environ.get("FAL_KEY")
    if not api_key:
        raise RuntimeError("FAL_KEY env var not set (required for requests backend)")

    headers = {"Authorization": f"Key {api_key}", "Content-Type": "application/json"}
    payload = {
        "prompt": prompt,
        "image_size": {"width": width, "height": height},
        "num_images": num_images,
        "output_format": "png",
        "enable_safety_checker": True,
    }
    if seed is not None:
        payload["seed"] = seed

    base = "https://queue.fal.run/fal-ai/flux/dev"
    r = requests.post(f"{base}/requests", headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    request_id = r.json()["request_id"]

    status_url = f"{base}/requests/{request_id}/status"
    result_url = f"{base}/requests/{request_id}"
    while True:
        s = requests.get(status_url, headers=headers, timeout=60).json()
        if s.get("status") == "COMPLETED":
            return requests.get(result_url, headers=headers, timeout=60).json()
        if s.get("status") in ("FAILED", "ERROR"):
            raise RuntimeError(f"FAL job failed: {s}")
        time.sleep(3)


# --------------------------------------------------------------------------- #
# Generate one image, return (local_path, meta)
# --------------------------------------------------------------------------- #
def generate_one(name, prompt, out_dir, width, height, seed, backend):
    print(f"[gen] {name}: {prompt[:60]}...")
    if backend == "fal_client":
        result = gen_fal_client(prompt, width, height, seed, 1)
    else:
        result = gen_requests(prompt, width, height, seed, 1)

    img = result["images"][0]
    # FAL returns either a URL or base64 data field
    if img.get("url"):
        import requests
        raw = requests.get(img["url"], timeout=60).content
    elif img.get("base64"):
        raw = base64.b64decode(img["base64"])
    else:
        raise RuntimeError(f"Unexpected image payload: {list(img.keys())}")

    raw = ensure_crop(raw, width, height)
    path = os.path.join(out_dir, f"{name}.png")
    with open(path, "wb") as fh:
        fh.write(raw)
    print(f"[ok ] saved {path} ({width}x{height})")
    return path, {
        "name": name,
        "prompt": prompt,
        "path": path,
        "width": width,
        "height": height,
        "seed": result.get("seed"),
        "model": MODEL_ID,
    }


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description="FLUX.1 [dev] 3:4 image generation")
    ap.add_argument("--prompt", help="single prompt")
    ap.add_argument("--name", help="filename stem for single prompt (no ext)")
    ap.add_argument("--prompts", help="batch prompts file (.tsv or .json)")
    ap.add_argument("--out", default="generated_images", help="output directory")
    ap.add_argument("--width", type=int, default=DEFAULT_W)
    ap.add_argument("--height", type=int, default=DEFAULT_H)
    ap.add_argument("--seed", type=int, default=None, help="fixed seed (else random)")
    ap.add_argument("--backend", choices=["auto", "fal_client", "requests"],
                    default="auto")
    args = ap.parse_args()

    if not args.prompt and not args.prompts:
        ap.error("provide --prompt or --prompts")

    # choose backend
    backend = args.backend
    if backend in ("auto", None):
        try:
            import fal_client  # noqa: F401
            backend = "fal_client"
            print("[backend] fal_client")
        except ImportError:
            backend = "requests"
            print("[backend] requests (fal_client not installed)")

    os.makedirs(args.out, exist_ok=True)

    if args.prompts:
        items = load_prompts(args.prompts)
    else:
        items = [(args.name or "image", args.prompt)]

    manifest = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "model": MODEL_ID,
        "backend": backend,
        "default_size": {"width": args.width, "height": args.height},
        "images": [],
    }

    for name, prompt in items:
        path, meta = generate_one(name, prompt, args.out, args.width,
                                  args.height, args.seed, backend)
        manifest["images"].append(meta)

    manifest_path = os.path.join(args.out, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    print(f"[done] {len(items)} image(s) -> {manifest_path}")


if __name__ == "__main__":
    main()
