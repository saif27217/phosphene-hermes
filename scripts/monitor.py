#!/usr/bin/env python3
"""
Phosphene Job Monitor

Usage:
    python monitor.py                  # Monitor current job
    python monitor.py --job JOB_ID     # Monitor specific job
    python monitor.py --list           # List recent jobs
    python monitor.py --outputs        # List outputs
"""

import argparse
import json
import sys
import time

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

BASE_URL = "https://macbook-pro.tailc4e23e.ts.net:8443"


def get_status() -> dict:
    resp = requests.get(f"{BASE_URL}/status", verify=False, timeout=10)
    resp.raise_for_status()
    return resp.json()


def list_jobs(limit: int = 10):
    status = get_status()
    print(f"{'ID':<25} {'Status':<10} {'Started':<20} {'Elapsed':<10}")
    print("-" * 70)

    for h in status.get("history", [])[:limit]:
        print(f"{h['id']:<25} {h['status']:<10} {h['started_at']:<20} {h['elapsed_sec']:.0f}s")


def list_outputs():
    resp = requests.get(f"{BASE_URL}/outputs?limit=100&offset=0", verify=False, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    print(f"{'Name':<50} {'Size':<10} {'URL'}")
    print("-" * 120)

    for o in data.get("outputs", []):
        print(f"{o['name']:<50} {o['size_mb']:.1f}MB{'':<5}{BASE_URL}{o['url']}")


def monitor_job(job_id: str = None, poll_interval: int = 10):
    print("Monitoring Phosphene...")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            status = get_status()

            if not status["running"]:
                if status["history"]:
                    h = status["history"][0]
                    print(f"\n{'✅' if h['status'] == 'done' else '❌'} Job {h['id']}: {h['status']}")
                    print(f"   Elapsed: {h['elapsed_sec']:.0f}s")
                    if h.get("output_path"):
                        print(f"   Output: {h['output_path']}")
                    if h.get("error"):
                        print(f"   Error: {h['error']}")
                else:
                    print("No jobs in history")
                break

            current = status.get("current")
            if current:
                p = current.get("progress", {})
                print(f"\r  [{current['id']}] {p.get('phase_label', '?')} "
                      f"{p.get('pct', 0)}% "
                      f"step {p.get('denoise_step', '?')}/{p.get('denoise_total', '?')} "
                      f"ETA: {p.get('eta_sec', 0):.0f}s", end="", flush=True)

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        print("\n\nStopped monitoring")


def main():
    parser = argparse.ArgumentParser(description="Phosphene Job Monitor")
    parser.add_argument("--job", help="Monitor specific job ID")
    parser.add_argument("--list", action="store_true", help="List recent jobs")
    parser.add_argument("--outputs", action="store_true", help="List outputs")
    parser.add_argument("--limit", type=int, default=10, help="Number of jobs to list")

    args = parser.parse_args()

    if args.list:
        list_jobs(args.limit)
    elif args.outputs:
        list_outputs()
    else:
        monitor_job(args.job)


if __name__ == "__main__":
    main()
