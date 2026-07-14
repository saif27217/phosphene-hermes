#!/usr/bin/env python3
"""
local_image_gen.py — End-to-end image generation via the LOCAL Phosphene endpoint
(MacBook Pro, Apple Silicon, Tailscale) using its bundled FLUX port (mflux).

This is the "local" counterpart to scripts/image_gen.py (which uses fal.ai's
FLUX.1 [dev] cloud). Instead of calling fal.ai, it drives Sak's MacBook:

    POST /queue/add   (mode=image)   -> submit FLUX image job
    GET  /status                       -> poll until done, read output_path
    GET  /outputs                      -> resolve download URL for that path
    GET  /image?path=..&v=..           -> download the PNG
    center-crop                        -> exact 3:4 (default 768x1024)

Verified facts about the endpoint (probed 2026-07-14, Phosphene v3.2.5):
  * Image jobs use the SAME /queue/add as video, but with `mode=image`.
  * Aspect-ratio / width / height params are IGNORED — output is always 1280x720.
  * Image downloads use /image?path=<abs>&v=<ts>  (NOT /file, which is video-only).
  * The generated file is named cand_<rand>_mflux.png (mflux = Apple FLUX port).
  * Self-signed TLS -> all requests need verify=False (curl -k).

Usage
-----
  # Curated prompts file (TSV: name<TAB>prompt)
  python3 local_image_gen.py --prompts prompts/psychiatry.tsv --out generated_images

  # Single prompt
  python3 local_image_gen.py --prompt "A depressed patient on a couch" \
      --name psychiatry_depressed --out generated_images

  # Custom Mac host / size
  python3 local_image_gen.py --base-url https://macbook-pro.tailc4e23e.ts.net:8443 \
      --prompt "..." --width 768 --height 1024

Env / args
----------
  --base-url   Tailscale URL of Phosphene (default below)
  Requires no API key (Tailscale LAN). Self-signed cert is accepted.
"""

import argparse
import datetime as dt
import io
import json
import os
import sys
import time
import urllib.parse
import urllib.request

try:
    from PIL import Image
    from PIL.Image import LANCZOS  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover - Pillow always present in this env
    Image = None
    LANCZOS = None

DEFAULT_BASE = "https://macbook-pro.tailc4e23e.ts.net:8443"
DEFAULT_W, DEFAULT_H = 768, 1024
POLL_INTERVAL = 8        # seconds
TIMEOUT = 600            # max seconds to wait for one job


# --------------------------------------------------------------------------- #
# Prompt loading (same TSV/JSON format as image_gen.py)
# --------------------------------------------------------------------------- #
def load_prompts(path):
    items = []
    with open(path, "r", encoding="utf-8") as fh:
        if path.endswith(".json"):
            data = json.load(fh)
            if isinstance(data, list):
                for i, e in enumerate(data):
                    if isinstance(e, str):
                        items.append((f"image_{i+1:02d}", e))
                    else:
                        items.append((e.get("name", f"image_{i+1:02d}"), e.get("prompt", "")))
            else:
                raise ValueError("JSON prompts file must be a list")
        else:
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
# HTTP helpers (urllib, verify=False equivalent via unverified context)
# --------------------------------------------------------------------------- #
import ssl
_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE


def _http(method, url, data=None, timeout=60):
    req = urllib.request.Request(url, data=data, method=method)
    if data is not None and method == "POST":
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=timeout, context=_CTX) as r:
        return r.read().decode("utf-8", "replace")


def _post_form(url, fields, timeout=60):
    body = urllib.parse.urlencode(fields).encode("utf-8")
    return _http("POST", url, data=body, timeout=timeout)


def _get_bytes(url, timeout=120):
    """Binary GET (for PNG download). Rejects self-signed certs implicitly ok via _CTX."""
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout, context=_CTX) as r:
        return r.read()


# --------------------------------------------------------------------------- #
# Crop -> exact 3:4
# --------------------------------------------------------------------------- #
def ensure_crop(image_bytes, width, height):
    if Image is None:
        return image_bytes
    im = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    if (im.width, im.height) == (width, height):
        out = io.BytesIO(); im.save(out, format="PNG"); return out.getvalue()
    # largest 3:4 window centered, then resize to target
    cw = min(im.width, int(round(im.height * width / height)))
    ch = min(im.height, int(round(cw * height / width)))
    left = (im.width - cw) // 2
    top = (im.height - ch) // 2
    crop = im.crop((left, top, left + cw, top + ch))
    if crop.size != (width, height):
        crop = crop.resize((width, height), LANCZOS)
    out = io.BytesIO(); crop.save(out, format="PNG"); return out.getvalue()


# --------------------------------------------------------------------------- #
# Submit + wait + download one image
# --------------------------------------------------------------------------- #
def generate_one(name, prompt, base_url, out_dir, width, height):
    print(f"[submit] {name}: {prompt[:60]}...")

    # 1. submit
    resp = _post_form(f"{base_url}/queue/add",
                      {"mode": "image", "prompt": prompt, "num_images": "1"},
                      timeout=30)
    job = json.loads(resp)
    if not job.get("ok"):
        raise RuntimeError(f"submit failed: {resp}")
    job_id = job["id"]
    print(f"        job {job_id}")

    # 2. poll /status until not running
    deadline = time.time() + TIMEOUT
    while time.time() < deadline:
        st = json.loads(_http("GET", f"{base_url}/status", timeout=20))
        cur = st.get("current")
        running = st.get("running")
        if not running:
            break
        pct = ""
        if isinstance(cur, dict) and cur.get("progress"):
            pct = f" {cur['progress'].get('pct')}% {cur['progress'].get('phase_label','')}"
        print(f"        ...running{pct}", flush=True)
        time.sleep(POLL_INTERVAL)
    else:
        raise TimeoutError(f"job {job_id} did not finish in {TIMEOUT}s")

    # 3. find our output_path in history
    st = json.loads(_http("GET", f"{base_url}/status", timeout=20))
    out_path = None
    for h in st.get("history", []):
        if job_id in str(h.get("id", "")):
            out_path = h.get("output_path")
            if h.get("status") != "done":
                raise RuntimeError(f"job {job_id} status={h.get('status')} error={h.get('error')}")
            break
    if not out_path:
        raise RuntimeError(f"output_path not found for job {job_id}")
    print(f"        output: {out_path}")

    # 4. resolve download URL from /outputs
    outs = json.loads(_http("GET", f"{base_url}/outputs?limit=50", timeout=20))
    url = None
    for o in outs.get("outputs", []):
        if o.get("path") == out_path:
            url = o.get("url")
            break
    if not url:
        # fallback: build /image url with v=timestamp from path mtime
        ts = str(int(time.time()))
        url = f"/image?path={urllib.parse.quote(out_path)}&v={ts}"
    print(f"        download {url}")

    # 5. download PNG (binary — must not decode/re-encode)
    raw_bytes = _get_bytes(f"{base_url}{url}", timeout=120)
    if raw_bytes[:4] != b"\x89PNG":
        raise RuntimeError(f"download did not return a PNG for {url}: {raw_bytes[:40]!r}")

    raw_bytes = ensure_crop(raw_bytes, width, height)
    path = os.path.join(out_dir, f"{name}.png")
    with open(path, "wb") as fh:
        fh.write(raw_bytes)
    print(f"[ok ] saved {path} ({width}x{height})")
    return path, {
        "name": name, "prompt": prompt, "path": path,
        "width": width, "height": height,
        "job_id": job_id, "source": "phosphene-mac-mflux",
        "native_size": "1280x720", "base_url": base_url,
    }


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description="Local Phosphene (Mac) FLUX image generation")
    ap.add_argument("--prompt")
    ap.add_argument("--name")
    ap.add_argument("--prompts", help="batch TSV/JSON prompts file")
    ap.add_argument("--out", default="generated_images")
    ap.add_argument("--base-url", default=DEFAULT_BASE)
    ap.add_argument("--width", type=int, default=DEFAULT_W)
    ap.add_argument("--height", type=int, default=DEFAULT_H)
    args = ap.parse_args()

    if not args.prompt and not args.prompts:
        ap.error("provide --prompt or --prompts")

    print(f"[local] Phosphene @ {args.base_url}")
    # sanity check reachable
    try:
        _http("GET", f"{args.base_url}/status", timeout=15)
    except Exception as e:
        ap.error(f"cannot reach {args.base_url}: {e}")

    os.makedirs(args.out, exist_ok=True)
    items = load_prompts(args.prompts) if args.prompts else [(args.name or "image", args.prompt)]

    manifest = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": "phosphene-mac-mflux",
        "base_url": args.base_url,
        "native_size": "1280x720",
        "default_size": {"width": args.width, "height": args.height},
        "images": [],
    }
    for name, prompt in items:
        p, meta = generate_one(name, prompt, args.base_url, args.out, args.width, args.height)
        manifest["images"].append(meta)

    mp = os.path.join(args.out, "manifest.local.json")
    with open(mp, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    print(f"[done] {len(items)} image(s) -> {mp}")


if __name__ == "__main__":
    main()
