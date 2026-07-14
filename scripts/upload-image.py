#!/usr/bin/env python3
"""
Phosphene Image Upload Helper

Usage:
    python upload-image.py image.png
    python upload-image.py image.jpg --list
    python upload-image.py --delete /path/to/image.png
"""

import argparse
import json
import sys

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

BASE_URL = "https://macbook-pro.tailc4e23e.ts.net:8443"


def upload_image(file_path: str) -> dict:
    """Upload an image to Phosphene."""
    with open(file_path, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/upload",
            files={"file": f},
            verify=False,
            timeout=30,
        )
    resp.raise_for_status()
    return resp.json()


def list_uploads(limit: int = 18):
    """List uploaded images."""
    resp = requests.get(f"{BASE_URL}/uploads?limit={limit}", verify=False, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    print(f"{'Name':<40} {'Size':<10} {'Modified':<20} {'URL'}")
    print("-" * 120)

    for u in data.get("uploads", []):
        print(f"{u['name']:<40} {u['size_kb']:.0f}KB{'':<6} {u['mtime']:<20} {BASE_URL}{u['url']}")


def delete_upload(path: str):
    """Delete an uploaded image."""
    resp = requests.post(
        f"{BASE_URL}/output/delete",
        data={"path": path},
        verify=False,
        timeout=10,
    )
    resp.raise_for_status()
    print(f"Deleted: {path}")


def main():
    parser = argparse.ArgumentParser(description="Phosphene Image Upload")
    parser.add_argument("file", nargs="?", help="Image file to upload")
    parser.add_argument("--list", action="store_true", help="List uploads")
    parser.add_argument("--limit", type=int, default=18, help="Number to list")
    parser.add_argument("--delete", help="Delete upload by path")

    args = parser.parse_args()

    if args.list:
        list_uploads(args.limit)
    elif args.delete:
        delete_upload(args.delete)
    elif args.file:
        print(f"Uploading {args.file}...")
        result = upload_image(args.file)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
