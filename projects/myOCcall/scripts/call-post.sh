#!/bin/bash
# call-post.sh — Fase 5 (Post-call, indipendente)
#
# 1) Valida/trascrive i segmenti audio tramite manifest
# 2) Genera SINTESI.md solo se la trascrizione supera i controlli minimi
# 3) Aggiorna META.md con i flag di completamento

set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "Uso: $0 <call_dir>" >&2
    exit 2
fi

CALL_DIR="$1"
META="$CALL_DIR/META.md"
MANIFEST="$CALL_DIR/audio/manifest.tsv"
TRANSCRIPT="$CALL_DIR/trascrizione.txt"
SINTESI="$CALL_DIR/SINTESI.md"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_DIR/.env"

if [ ! -f "$META" ]; then
    echo "ERRORE: META.md non trovato in $CALL_DIR" >&2
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
    echo "ERRORE: OPENAI_API_KEY non impostata in $ENV_FILE" >&2
    exit 3
fi

NOW_FULL="$(TZ=Europe/Rome date +'%Y-%m-%d %H:%M')"

if [ ! -f "$MANIFEST" ]; then
    if [ -x "$SCRIPT_DIR/call-audio-manifest.sh" ]; then
        "$SCRIPT_DIR/call-audio-manifest.sh" "$CALL_DIR"
    fi
fi

if [ ! -f "$MANIFEST" ]; then
    echo "ERRORE: manifest non trovato in $CALL_DIR" >&2
    exit 4
fi

ATTRIBUTED="$CALL_DIR/trascrizione_attribuita.md"

echo "→ Trascrizione segmenti via Whisper…"
if ! "$SCRIPT_DIR/call-transcribe-segments.sh" "$CALL_DIR"; then
    python3 - "$META" <<'PY'
import pathlib, re, sys
meta = pathlib.Path(sys.argv[1])
text = meta.read_text()
text = re.sub(r'^- \*\*Trascrizione:\*\*.*$', '- **Trascrizione:** fallita', text, count=1, flags=re.MULTILINE)
meta.write_text(text)
PY
    echo "ERRORE: trascrizione segmenti fallita" >&2
    exit 5
fi

QUALITY_STATUS=$(python3 - "$TRANSCRIPT" <<'PY'
import re, sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(errors='ignore') if path.exists() else ''
lower = text.lower()
words = re.findall(r'\b\w+\b', text, flags=re.UNICODE)

if len(words) < 10:
    print('too_short')
elif 'sottotitoli creati dalla comunità' in lower:
    print('suspicious')
else:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if lines:
        uniq = len(set(lines))
        if len(lines) > 8 and uniq and len(lines) / uniq >= 3:
            print('repetitive')
        else:
            print('ok')
    else:
        print('too_short')
PY
)

if [ "$QUALITY_STATUS" != "ok" ]; then
    python3 - "$META" "$QUALITY_STATUS" <<'PY'
import pathlib, re, sys
meta = pathlib.Path(sys.argv[1])
status = sys.argv[2]
text = meta.read_text()
text = re.sub(r'^- \*\*Trascrizione:\*\*.*$', f'- **Trascrizione:** {status}', text, count=1, flags=re.MULTILINE)
meta.write_text(text)
PY
    echo "ERRORE: trascrizione non abbastanza valida ($QUALITY_STATUS)" >&2
    exit 6
fi

# Aggiorna META: trascrizione ✓
python3 - "$META" <<'PY'
import pathlib, re, sys
meta = pathlib.Path(sys.argv[1])
text = meta.read_text()
text = re.sub(r'^- \*\*Trascrizione:\*\*.*$', '- **Trascrizione:** trascrizione.txt [✓ generata]', text, count=1, flags=re.MULTILINE)
meta.write_text(text)
PY

# ---- Speaker attribution overlay ----
if [ -f "$SCRIPT_DIR/call-speaker-overlay.py" ]; then
    echo "→ Speaker attribution overlay…"
    if python3 "$SCRIPT_DIR/call-speaker-overlay.py" "$CALL_DIR"; then
        echo "✓ trascrizione_attribuita.md pronta"
    else
        echo "[WARN] Speaker overlay fallito, uso trascrizione semplice" >&2
        ATTRIBUTED=""
    fi
else
    ATTRIBUTED=""
fi

# ---- Generazione SINTESI.md (template strutturato) ----
PLATFORM=$(grep -m1 -E '^- \*\*Piattaforma:\*\*' "$META" | sed -E 's/^- \*\*Piattaforma:\*\* //' | xargs || echo "—")
URL=$(grep -m1 -E '^- \*\*URL:\*\*' "$META" | sed -E 's/^- \*\*URL:\*\* //' | xargs || echo "—")
JOIN=$(grep -m1 -E '^- \*\*Bot join:\*\*' "$META" | sed -E 's/^- \*\*Bot join:\*\* //' | xargs || echo "—")
LEAVE=$(grep -m1 -E '^- \*\*Bot leave:\*\*' "$META" | sed -E 's/^- \*\*Bot leave:\*\* //' | xargs || echo "—")
DURATION=$(grep -m1 -E '^- \*\*Durata:\*\*' "$META" | sed -E 's/^- \*\*Durata:\*\* //' | xargs || echo "—")

WORDS=$(wc -w < "$TRANSCRIPT" | xargs)
PREVIEW=$(head -c 800 "$TRANSCRIPT")

if [ -n "$ATTRIBUTED" ] && [ -f "$ATTRIBUTED" ]; then
    SPEAKER_SECTION=$(head -c 3000 "$ATTRIBUTED")
    ATTRIBUTED_NOTE="trascrizione_attribuita.md [✓ generata]"
else
    SPEAKER_SECTION="_(speaker-events.jsonl non disponibile o overlay fallito)_"
    ATTRIBUTED_NOTE="—"
fi

cat > "$SINTESI" <<EOF
# Sintesi call — $PLATFORM — $NOW_FULL (Europe/Rome)

## Info call
- **Piattaforma:** $PLATFORM
- **URL:** $URL
- **Bot join:** $JOIN
- **Bot leave:** $LEAVE
- **Durata:** $DURATION
- **Parole trascritte:** $WORDS
- **Trascrizione attribuita:** $ATTRIBUTED_NOTE

## Contesto e inizio riunione
_(da compilare manualmente o tramite LLM a partire dalla trascrizione)_

## Argomenti trattati
_(elenco puntato)_

## Decisioni prese
_(elenco puntato)_

## Dettaglio per parlante
$SPEAKER_SECTION

## Estratto trascrizione (primi 800 caratteri)
\`\`\`
$PREVIEW
\`\`\`

> Trascrizione completa in \`trascrizione.txt\`. Trascrizione attribuita in \`trascrizione_attribuita.md\`.
EOF

# Aggiorna META: sintesi ✓
python3 - "$META" <<'PY'
import pathlib, re, sys
meta = pathlib.Path(sys.argv[1])
text = meta.read_text()
text = re.sub(r'^- \*\*Sintesi:\*\*.*$', '- **Sintesi:** SINTESI.md [✓ generata]', text, count=1, flags=re.MULTILINE)
meta.write_text(text)
PY

# ---- Invio SINTESI.md ad Atti via Telegram ----
echo "→ Invio SINTESI.md via Telegram…"
SINTESI_TEXT=$(cat "$SINTESI")
PLATFORM_LABEL=$(grep -m1 -E '^- \*\*Piattaforma:\*\*' "$META" | sed -E 's/^- \*\*Piattaforma:\*\* //' | xargs || echo "call")

openclaw sessions send main "📋 *Sintesi $PLATFORM_LABEL — $NOW_FULL*

$SINTESI_TEXT" 2>/dev/null || {
    PENDING_FILE="$CALL_DIR/sintesi-pending-send.txt"
    echo "ERRORE invio Telegram — sintesi salvata in $PENDING_FILE" >&2
    echo "$SINTESI_TEXT" > "$PENDING_FILE"
}

echo "Post-call completata: $NOW_FULL"
