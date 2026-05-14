#!/bin/bash
# call-transcribe-segments.sh <call_dir>
#
# Trascrive tutti i segmenti validi presenti in audio/manifest.tsv.

set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "Uso: $0 <call_dir>" >&2
    exit 2
fi

CALL_DIR="$1"
META="$CALL_DIR/META.md"
MANIFEST="$CALL_DIR/audio/manifest.tsv"
TRANSCRIPT_DIR="$CALL_DIR/transcripts"
OUT="$CALL_DIR/trascrizione.txt"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$PROJECT_DIR/.env"
API_URL="${OPENAI_BASE_URL:-https://api.openai.com/v1}"
API_URL="${API_URL%/}"

if [ ! -f "$MANIFEST" ]; then
    echo "ERRORE: manifest non trovato: $MANIFEST" >&2
    exit 3
fi
if [ ! -f "$ENV_FILE" ]; then
    echo "ERRORE: .env non trovato in $PROJECT_DIR" >&2
    exit 3
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "ERRORE: OPENAI_API_KEY non impostata" >&2
    exit 3
fi

mkdir -p "$TRANSCRIPT_DIR"
: > "$OUT"

valid_seen=0
transcribed_ok=0
failed=0

transcribe_segment() {
    local seg_path="$1"
    local seg_out="$2"
    local http_body="$3"

    local http_code
    http_code=$(curl -sS -o "$http_body" -w '%{http_code}' \
        "$API_URL/audio/transcriptions" \
        -H "Authorization: Bearer $OPENAI_API_KEY" \
        -F "model=whisper-1" \
        -F "language=it" \
        -F "response_format=text" \
        -F "file=@$seg_path")

    if [ "$http_code" != "200" ]; then
        echo "HTTP $http_code" > "$seg_out"
        cat "$http_body" >> "$seg_out" 2>/dev/null || true
        return 1
    fi

    mv "$http_body" "$seg_out"
    return 0
}

while IFS=$'\t' read -r index file start_sec duration_sec size_bytes max_volume_db mean_volume_db status note; do
    [ "$index" = "index" ] && continue
    [ -z "${index:-}" ] && continue
    if [ "${status:-}" != "valid" ]; then
        continue
    fi

    valid_seen=$((valid_seen + 1))
    seg_name="segment-${index}.mp3"
    seg_path="$CALL_DIR/$file"
    seg_txt="$TRANSCRIPT_DIR/segment-${index}.txt"
    tmp_body="$CALL_DIR/.whisper-${index}.txt"

    if [ ! -s "$seg_path" ]; then
        echo "segment missing: $seg_path" > "$seg_txt"
        failed=$((failed + 1))
        continue
    fi

    if transcribe_segment "$seg_path" "$seg_txt" "$tmp_body"; then
        transcribed_ok=$((transcribed_ok + 1))
    else
        failed=$((failed + 1))
        continue
    fi

    end_sec=$(python3 - <<PY
start = float(${start_sec:-0} or 0)
dur = float(${duration_sec:-0} or 0)
print(f"{start + dur:.3f}")
PY
)

    {
        printf '[%s | %s - %s]\n' "$seg_name" "${start_sec:-0}" "$end_sec"
        cat "$seg_txt"
        printf '\n\n'
    } >> "$OUT"
done < "$MANIFEST"

if [ "$valid_seen" -eq 0 ]; then
    echo "ERRORE: nessun segmento valido da trascrivere" >&2
    exit 4
fi

if [ "$transcribed_ok" -eq 0 ]; then
    echo "ERRORE: nessun segmento è stato trascritto con successo" >&2
    exit 5
fi

python3 - "$OUT" <<'PY'
import re, sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(errors='ignore')
warnings = []

lower = text.lower()
if 'sottotitoli creati dalla comunità' in lower:
    warnings.append('contains subtitle-community boilerplate')

lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
if lines:
    uniq = len(set(lines))
    if uniq and len(lines) / uniq >= 3 and len(lines) > 8:
        warnings.append('repetitive transcript')

word_count = len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))
if word_count < 10:
    warnings.append('too short')

if warnings:
    print('\n'.join(warnings))
PY

echo "✓ trascrizione segmenti completata: $transcribed_ok/$valid_seen"
