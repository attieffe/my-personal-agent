#!/bin/bash
# call-audio-manifest.sh <call_dir>
#
# Valida i segmenti audio e scrive audio/manifest.tsv.

set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "Uso: $0 <call_dir>" >&2
    exit 2
fi

CALL_DIR="$1"
SEG_DIR="$CALL_DIR/audio/segments"
MANIFEST="$CALL_DIR/audio/manifest.tsv"

mkdir -p "$CALL_DIR/audio"

python3 - "$SEG_DIR" "$MANIFEST" <<'PY'
import csv
import math
import re
import subprocess
import sys
from pathlib import Path

seg_dir = Path(sys.argv[1])
manifest = Path(sys.argv[2])

header = [
    'index', 'file', 'start_sec', 'duration_sec', 'size_bytes',
    'max_volume_db', 'mean_volume_db', 'status', 'note',
]

def run(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def ffprobe_duration(path: Path):
    r = run([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', str(path)
    ])
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or 'ffprobe failed')
    return float(r.stdout.strip())

def volumedetect(path: Path):
    r = run([
        'ffmpeg', '-hide_banner', '-nostdin', '-i', str(path),
        '-af', 'volumedetect', '-f', 'null', '-'
    ])
    out = r.stderr
    max_v = mean_v = ''
    m = re.search(r'max_volume:\s*([\-0-9\.inf]+) dB', out)
    if m:
        max_v = m.group(1)
    m = re.search(r'mean_volume:\s*([\-0-9\.inf]+) dB', out)
    if m:
        mean_v = m.group(1)
    return max_v, mean_v

files = sorted(seg_dir.glob('segment-*.mp3'))
rows = []
start = 0.0
seen = set()

for path in files:
    m = re.search(r'segment-(\d+)\.mp3$', path.name)
    if not m:
        continue
    idx = int(m.group(1))
    seen.add(idx)
    rel = f'audio/segments/{path.name}'
    size = path.stat().st_size if path.exists() else 0
    status = 'missing'
    dur = ''
    max_v = ''
    mean_v = ''
    note = ''

    if not path.exists():
        note = 'file missing'
    elif size <= 0:
        status = 'too_small'
        note = 'empty file'
    else:
        try:
            dur = ffprobe_duration(path)
            if not math.isfinite(dur) or dur <= 0.2:
                status = 'too_small'
                note = 'duration too short'
            else:
                try:
                    max_v, mean_v = volumedetect(path)
                except Exception:
                    max_v = mean_v = ''
                if max_v == '-inf':
                    status = 'silent'
                    note = 'no detectable volume'
                elif max_v not in {'', 'inf'}:
                    try:
                        if float(max_v) <= -45.0:
                            status = 'silent'
                            note = 'very low volume'
                        else:
                            status = 'valid'
                    except ValueError:
                        status = 'valid'
                else:
                    status = 'valid'
        except Exception as e:
            status = 'corrupt'
            note = str(e).replace('\t', ' ')[:120]

    rows.append({
        'index': f'{idx:04d}',
        'file': rel,
        'start_sec': f'{start:.3f}' if status != 'missing' else '',
        'duration_sec': f'{dur:.3f}' if isinstance(dur, float) else '',
        'size_bytes': str(size) if path.exists() else '',
        'max_volume_db': max_v,
        'mean_volume_db': mean_v,
        'status': status,
        'note': note,
    })
    if isinstance(dur, float) and dur > 0:
        start += dur

if files:
    max_idx = max(seen)
    for idx in range(min(seen), max_idx + 1):
        if idx not in seen:
            rows.append({
                'index': f'{idx:04d}',
                'file': f'audio/segments/segment-{idx:04d}.mp3',
                'start_sec': '',
                'duration_sec': '',
                'size_bytes': '',
                'max_volume_db': '',
                'mean_volume_db': '',
                'status': 'missing',
                'note': 'segment not found',
            })

rows.sort(key=lambda r: int(r['index']))

manifest.parent.mkdir(parents=True, exist_ok=True)
with manifest.open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=header, delimiter='\t')
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

print(manifest)
PY
