#!/usr/bin/env python3
"""
Phosphene Video Generation Wrapper

Usage:
    python generate.py "A cinematic landscape"
    python generate.py "A cat playing" --width 576 --height 1024 --quality quick
    python generate.py --image reference.png "Image to video prompt"
"""

import argparse
import json
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

BASE_URL = "https://macbook-pro.tailc4e23e.ts.net:8443"


def submit_job(prompt: str, **kwargs) -> dict:
    """Submit a video generation job."""
    data = {
        "mode": kwargs.get("mode", "t2v"),
        "prompt": prompt,
        "width": kwargs.get("width", 1024),
        "height": kwargs.get("height", 576),
        "frames": kwargs.get("frames", 121),
        "steps": kwargs.get("steps", 8),
        "quality": kwargs.get("quality", "balanced"),
        "accel": kwargs.get("accel", "off"),
        "upscale": kwargs.get("upscale", "fit_720p"),
        "upscale_method": kwargs.get("upscale_method", "lanczos"),
        "temporal_mode": kwargs.get("temporal_mode", "native"),
        "cfg_scale": kwargs.get("cfg_scale", 3.0),
        "teacache_thresh": kwargs.get("teacache_thresh", 1.8),
        "stage1_steps": kwargs.get("stage1_steps", 10),
        "stage2_steps": kwargs.get("stage2_steps", 3),
        "seed": kwargs.get("seed", -1),
        "enhance": kwargs.get("enhance", False),
        "hdr": kwargs.get("hdr", False),
    }

    if kwargs.get("negative_prompt"):
        data["negative_prompt"] = kwargs["negative_prompt"]

    if kwargs.get("image"):
        data["image"] = kwargs["image"]

    resp = requests.post(
        f"{BASE_URL}/queue/add",
        files={k: (None, str(v)) for k, v in data.items()},
        verify=False,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_status() -> dict:
    """Get server status."""
    resp = requests.get(f"{BASE_URL}/status", verify=False, timeout=10)
    resp.raise_for_status()
    return resp.json()


def wait_for_completion(job_id: str, poll_interval: int = 10) -> dict:
    """Wait for a job to complete."""
    print(f"Waiting for job {job_id}...")

    while True:
        status = get_status()

        if not status["running"]:
            job = status["history"][0]
            if job["id"] == job_id:
                return job

        current = status.get("current")
        if current and current.get("progress"):
            p = current["progress"]
            print(f"\r  {p.get('phase_label', '?')} {p.get('pct', 0)}% "
                  f"step {p.get('denoise_step', '?')}/{p.get('denoise_total', '?')} "
                  f"ETA: {p.get('eta_sec', 0):.0f}s", end="", flush=True)

        time.sleep(poll_interval)


def download_output(url: str, output_path: str):
    """Download a generated video."""
    resp = requests.get(f"{BASE_URL}{url}", verify=False, stream=True, timeout=60)
    resp.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Downloaded: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Phosphene Video Generation")
    parser.add_argument("prompt", help="Video prompt")
    parser.add_argument("--mode", default="t2v", choices=["t2v", "i2v", "keyframe", "extend"])
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=576)
    parser.add_argument("--frames", type=int, default=121)
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--quality", default="balanced", choices=["quick", "balanced", "standard", "high"])
    parser.add_argument("--accel", default="off", choices=["off", "boost", "turbo"])
    parser.add_argument("--upscale", default="fit_720p", choices=["off", "fit_720p", "x2"])
    parser.add_argument("--negative-prompt", default="")
    parser.add_argument("--image", help="Reference image path for i2v")
    parser.add_argument("--seed", type=int, default=-1)
    parser.add_argument("--wait", action="store_true", help="Wait for completion")
    parser.add_argument("--download", help="Download output to path")
    parser.add_argument("--no-verify", action="store_true", help="Disable SSL verification")

    args = parser.parse_args()

    # Submit job
    print(f"Submitting {args.quality} {args.mode} video...")
    print(f"Prompt: {args.prompt}")
    print(f"Resolution: {args.width}×{args.height}, {args.frames} frames")

    result = submit_job(
        args.prompt,
        mode=args.mode,
        width=args.width,
        height=args.height,
        frames=args.frames,
        steps=args.steps,
        quality=args.quality,
        accel=args.accel,
        upscale=args.upscale,
        negative_prompt=args.negative_prompt,
        image=args.image,
        seed=args.seed,
    )

    if not result.get("ok"):
        print(f"Error: {result}")
        sys.exit(1)

    job_id = result["id"]
    print(f"Job submitted: {job_id}")

    if args.wait:
        job = wait_for_completion(job_id)
        print()

        if job["status"] == "done":
            print(f"✅ Complete in {job['elapsed_sec']:.0f}s")
            if job.get("output_path"):
                print(f"Output: {job['output_path']}")

            if args.download:
                # Get download URL from outputs
                status = get_status()
                for o in status.get("outputs", []):
                    if o["name"] in job.get("output_path", ""):
                        download_output(o["url"], args.download)
                        break
        else:
            print(f"❌ Failed: {job.get('error', 'Unknown error')}")
            sys.exit(1)


if __name__ == "__main__":
    main()
