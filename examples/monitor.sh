#!/bin/bash
# Monitor current job until completion
# Usage: ./monitor.sh

BASE_URL="https://macbook-pro.tailc4e23e.ts.net:8443"

echo "Monitoring Phosphene job..."

while true; do
  STATUS=$(curl -sSk --max-time 10 "$BASE_URL/status" 2>/dev/null)
  RUNNING=$(echo "$STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin)['running'])" 2>/dev/null)

  if [ "$RUNNING" = "False" ]; then
    echo ""
    echo "✅ Job complete!"
    echo "$STATUS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
h = data['history'][0]
print(f'Job: {h[\"id\"]}')
print(f'Status: {h[\"status\"]}')
print(f'Elapsed: {h[\"elapsed_sec\"]:.0f}s')
if h.get('output_path'):
    print(f'Output: {h[\"output_path\"]}')
if h.get('error'):
    print(f'Error: {h[\"error\"]}')
"
    break
  fi

  PCT=$(echo "$STATUS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
c = data.get('current')
if c and c.get('progress'):
    p = c['progress']
    print(f'{p.get(\"phase_label\",\"?\")} {p.get(\"pct\",0)}% step {p.get(\"denoise_step\",\"?\")}/{p.get(\"denoise_total\",\"?\")}')
else:
    print('Waiting...')
" 2>/dev/null)

  echo "[$(date +%H:%M:%S)] $PCT"
  sleep 10
done
