#!/bin/bash
# Download all outputs
# Usage: ./download-all.sh [output_dir]

BASE_URL="https://macbook-pro.tailc4e23e.ts.net:8443"
OUTPUT_DIR="${1:-./downloads}"

mkdir -p "$OUTPUT_DIR"

echo "Downloading all Phosphene outputs to $OUTPUT_DIR..."

curl -sSk "$BASE_URL/outputs?limit=100&offset=0" | python3 -c "
import sys, json, subprocess, os

data = json.load(sys.stdin)
output_dir = '$OUTPUT_DIR'

for o in data.get('outputs', []):
    name = o['name']
    url = f'$BASE_URL{o[\"url\"]}'
    size = o['size_mb']
    print(f'Downloading {name} ({size:.1f}MB)...')
    subprocess.run(['curl', '-sSk', '-o', f'{output_dir}/{name}', url], check=True)
    print(f'  ✅ {output_dir}/{name}')

print(f'\nDone! {len(data.get(\"outputs\", []))} files downloaded to {output_dir}')
"
