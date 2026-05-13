#!/bin/bash
# call-stop.sh — Fase 4 (Exit)
#
# Ferma ffmpeg in modo graceful, genera il manifest segmenti e aggiorna META.md.
#
# Uso: ./call-stop.sh <call_dir>

set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "Uso: $0 <call_dir>" >&2
    exit 2
fi

CALL_DIR="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
META="$CALL_DIR/META.md"
PIDFILE="$CALL_DIR/ffmpeg.pid"
MANIFEST="$CALL_DIR/audio/manifest.tsv"
SEG_DIR="$CALL_DIR/audio/segments"
COMPAT_AUDIO="$CALL_DIR/audio.mp3"

if [ ! -f "$META" ]; then
    echo "ERRORE: META.md non trovato in $CALL_DIR" >&2
    exit 3
fi

NOW_FULL="$(TZ=Europe/Rome date +'%Y-%m-%d %H:%M')"
NOW_HM="$(TZ=Europe/Rome date +'%H:%M')"
NOW_EPOCH="$(date +%s)"

# Stop graceful di ffmpeg
if [ -f "$PIDFILE" ]; then
    FFMPEG_PID="$(cat "$PIDFILE" 2>/dev/null || echo)"
    if [ -n "$FFMPEG_PID" ] && kill -0 "$FFMPEG_PID" 2>/dev/null; then
        kill -TERM "$FFMPEG_PID" 2>/dev/null || true
        for _ in $(seq 1 20); do
            if ! kill -0 "$FFMPEG_PID" 2>/dev/null; then
                break
            fi
            sleep 0.5
        done
        if kill -0 "$FFMPEG_PID" 2>/dev/null; then
            kill -KILL "$FFMPEG_PID" 2>/dev/null || true
            sleep 0.5
        fi
    fi
    rm -f "$PIDFILE"
fi

# Calcolo durata: differenza tra "Bot join" (se presente) e ora
JOIN_TS="$(grep -m1 -E '^- \*\*Bot join:\*\*' "$META" | sed -E 's/^- \*\*Bot join:\*\* ([^(]*)\(.*$/\1/' | xargs || true)"
DURATION="—"
if [ -n "$JOIN_TS" ] && [[ "$JOIN_TS" =~ ^[0-9]{4}- ]]; then
    JOIN_EPOCH="$(TZ=Europe/Rome date -d "$JOIN_TS" +%s 2>/dev/null || echo 0)"
    if [ "$JOIN_EPOCH" -gt 0 ]; then
        DIFF=$((NOW_EPOCH - JOIN_EPOCH))
        if [ "$DIFF" -ge 0 ]; then
            HH=$((DIFF / 3600))
            MM=$(((DIFF % 3600) / 60))
            DURATION="$(printf '%02d:%02d' "$HH" "$MM")"
        fi
    fi
fi

# Genera manifest segmenti
if [ -x "$SCRIPT_DIR/call-audio-manifest.sh" ]; then
    "$SCRIPT_DIR/call-audio-manifest.sh" "$CALL_DIR" >/dev/null
else
    echo "ERRORE: call-audio-manifest.sh non trovato o non eseguibile" >&2
    exit 4
fi

if [ ! -f "$MANIFEST" ]; then
    echo "ERRORE: manifest segmenti non generato: $MANIFEST" >&2
    exit 5
fi

read -r TOTAL VALID SILENT TOOSMALL CORRUPT MISSING < <(
    python3 - "$MANIFEST" <<'PY'
import csv, sys
from pathlib import Path

path = Path(sys.argv[1])
total = valid = silent = toosmall = corrupt = missing = 0
with path.open(newline='') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        total += 1
        status = (row.get('status') or '').strip()
        if status == 'valid':
            valid += 1
        elif status == 'silent':
            silent += 1
        elif status == 'too_small':
            toosmall += 1
        elif status == 'corrupt':
            corrupt += 1
        elif status == 'missing':
            missing += 1

print(total, valid, silent, toosmall, corrupt, missing)
PY
)

# Aggiorna META con lo stato audio base
python3 - "$META" "$NOW_FULL" "$DURATION" "$NOW_HM" "$TOTAL" "$VALID" "$MANIFEST" <<'PY'
import sys, re, pathlib

meta = pathlib.Path(sys.argv[1])
full_ts = sys.argv[2]
duration = sys.argv[3]
hm = sys.argv[4]
total = sys.argv[5]
valid = sys.argv[6]
manifest = sys.argv[7]
text = meta.read_text()

replacements = [
    (r'^- \*\*Bot leave:\*\*.*$', f'- **Bot leave:** {full_ts} (Europe/Rome)'),
    (r'^- \*\*Durata:\*\*.*$', f'- **Durata:** {duration}'),
    (r'^- \*\*Stato:\*\*.*$', '- **Stato:** terminata'),
    (r'^- \*\*Audio:\*\*.*$', '- **Audio:** segmenti MP3 da 300s [✓ registrazione chiusa]'),
    (r'^- \*\*Cartella segmenti:\*\*.*$', '- **Cartella segmenti:** audio/segments/'),
    (r'^- \*\*Manifest:\*\*.*$', f'- **Manifest:** {manifest.replace(str(meta.parent) + "/", "")} [✓ generato]'),
    (r'^- \*\*Segmenti generati:\*\*.*$', f'- **Segmenti generati:** {total}'),
    (r'^- \*\*Segmenti validi:\*\*.*$', f'- **Segmenti validi:** {valid}'),
    (r'^- \*\*Trascrizione:\*\*.*$', '- **Trascrizione:** [ ] da generare'),
]
for pattern, repl in replacements:
    count = 0 if 'Trascrizione' in repl or 'Manifest' in repl or 'Audio:' in repl or 'Segmenti ' in repl or 'Cartella segmenti' in repl else 1
    text = re.sub(pattern, repl, text, count=count, flags=re.MULTILINE)

def _bot_leave(m):
    n = m.group(1)
    e = m.group(2).strip() or '—'
    u = m.group(3).strip() or '—'
    if u == '—':
        u = hm
    return f'| {n} | {e} | {u} |'

text = re.sub(
    r'^\| (Attilio F\. \(bot\)) \|([^|]*)\|([^|]*)\|',
    _bot_leave,
    text, count=1, flags=re.MULTILINE,
)

meta.write_text(text)
PY

# Crea un audio derivato opzionale per compatibilità, senza usarlo come fonte primaria
if [ "$VALID" -gt 0 ]; then
    TMP_LIST="$CALL_DIR/.concat-segments.txt"
    python3 - "$MANIFEST" "$SEG_DIR" "$TMP_LIST" <<'PY'
import csv, sys
from pathlib import Path

manifest = Path(sys.argv[1])
seg_dir = Path(sys.argv[2])
tmp_list = Path(sys.argv[3])

rows = []
with manifest.open(newline='') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if (row.get('status') or '').strip() == 'valid':
            rows.append(seg_dir / Path(row['file']).name)

with tmp_list.open('w') as f:
    for row in rows:
        f.write(f"file '{row.as_posix()}'\n")
PY
    if [ -s "$TMP_LIST" ]; then
        ffmpeg -hide_banner -loglevel error -nostdin -y \
            -f concat -safe 0 -i "$TMP_LIST" -c copy "$COMPAT_AUDIO" \
            >/dev/null 2>&1 || true
    fi
    rm -f "$TMP_LIST"
fi

# Verifica qualità minimo e segnala errori chiari
if [ "$VALID" -le 0 ]; then
    {
        echo
        echo "## WARNING"
        echo "- $NOW_FULL — nessun segmento audio valido da trascrivere."
    } >> "$META"
    echo "ERRORE: nessun segmento audio valido da trascrivere" >&2
    exit 6
fi

if [ "$CORRUPT" -gt 0 ] || [ "$TOOSMALL" -gt 0 ] || [ "$MISSING" -gt 0 ]; then
    {
        echo
        echo "## WARNING"
        echo "- $NOW_FULL — segmenti non validi: corrupt=$CORRUPT too_small=$TOOSMALL missing=$MISSING"
    } >> "$META"
fi

echo "Call terminata: $NOW_FULL (durata $DURATION, segmenti validi $VALID/$TOTAL)"
