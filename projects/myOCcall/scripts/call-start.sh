#!/bin/bash
# call-start.sh — Fase 1 (Pre-join)
#
# Crea la cartella della call, scrive META.md e avvia ffmpeg in background
# per catturare audio da virtual_out.monitor (PulseAudio null sink).
#
# Uso: ./call-start.sh <platform> <url>
#   <platform>: meet | zoom | teams | test | ...
#   <url>:      URL della call
#
# Output (su stdout): path assoluto della cartella call creata.

set -euo pipefail

if [ "$#" -lt 2 ]; then
    echo "Uso: $0 <platform> <url>" >&2
    exit 2
fi

PLATFORM="$1"
URL="$2"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$PROJECT_DIR/data"
PULSE_SOURCE="virtual_out.monitor"

mkdir -p "$DATA_DIR"

NOW_FOLDER="$(TZ=Europe/Rome date +'%Y%m%d %H%M')"
NOW_HUMAN="$(TZ=Europe/Rome date +'%Y-%m-%d %H:%M')"
NOW_HM="$(TZ=Europe/Rome date +'%H:%M')"

CALL_DIR="$DATA_DIR/$NOW_FOLDER $PLATFORM"

# Se la cartella esiste già (stesso minuto), aggiungiamo un suffisso incrementale
SUFFIX=2
ORIG="$CALL_DIR"
while [ -d "$CALL_DIR" ]; do
    CALL_DIR="$ORIG-$SUFFIX"
    SUFFIX=$((SUFFIX + 1))
done

mkdir -p "$CALL_DIR"
mkdir -p "$CALL_DIR/audio/segments" "$CALL_DIR/transcripts"

META="$CALL_DIR/META.md"
cat > "$META" <<EOF
# Call — $PLATFORM — $NOW_HUMAN (Europe/Rome)

## Info call
- **Piattaforma:** $PLATFORM
- **URL:** $URL
- **Bot join:** — (in attesa)
- **Bot leave:** — (in corso)
- **Durata:** —
- **Stato:** in corso
- **Creazione cartella:** $NOW_HUMAN (Europe/Rome)

## File di lavoro
- **Audio:** segmenti MP3 da 300s [ in registrazione ]
- **Cartella segmenti:** audio/segments/
- **Manifest:** audio/manifest.tsv [ ] da generare
- **Trascrizione:** trascrizione.txt [ ] da generare
- **Sintesi:** SINTESI.md [ ] da generare

## Audio
- **Fonte:** virtual_out.monitor
- **Modalità:** segmenti MP3 da 300s
- **Cartella segmenti:** audio/segments/
- **Manifest:** audio/manifest.tsv [ ] da generare
- **Segmenti generati:** —
- **Segmenti validi:** —
- **Trascrizione:** [ ] da generare

## Partecipanti
| Nome | Entrata | Uscita |
|------|---------|--------|
| Attilio F. (bot) | — | — |

## Note
—
EOF

# Avvio ffmpeg in background.
# - Input: PulseAudio source virtual_out.monitor
# - Output: segmenti MP3 a 128k, 44.1kHz, mono da 300s
# - Log: audio/recording.log nella cartella call (utile per debug)
LOGFILE="$CALL_DIR/audio/recording.log"
PIDFILE="$CALL_DIR/ffmpeg.pid"
SEGMENT_OUT="$CALL_DIR/audio/segments/segment-%04d.mp3"

if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "ERRORE: ffmpeg non trovato nel PATH" >&2
    exit 3
fi

# Verifica che PulseAudio risponda; se no, prova a lanciare lo script di bootstrap
if ! pactl info >/dev/null 2>&1; then
    if [ -x "$PROJECT_DIR/scripts/start-audio.sh" ]; then
        "$PROJECT_DIR/scripts/start-audio.sh" >>"$LOGFILE" 2>&1 || true
    fi
fi

# Verifica che il source virtual_out.monitor esista; se no, warning ma proseguiamo
if ! pactl list short sources 2>/dev/null | grep -q "$PULSE_SOURCE"; then
    {
        echo "[WARN] $NOW_HUMAN — source PulseAudio '$PULSE_SOURCE' non trovato al pre-join."
    } >> "$META"
fi

nohup ffmpeg -hide_banner -loglevel warning -nostdin -y \
    -f pulse -i "$PULSE_SOURCE" \
    -ac 1 -ar 44100 -b:a 128k \
    -f segment -segment_time 300 -reset_timestamps 1 -segment_format mp3 \
    "$SEGMENT_OUT" \
    >"$LOGFILE" 2>&1 &

FFMPEG_PID=$!
echo "$FFMPEG_PID" > "$PIDFILE"

# Piccolo wait per verificare che ffmpeg sia ancora vivo dopo l'avvio
sleep 1
if ! kill -0 "$FFMPEG_PID" 2>/dev/null; then
    {
        echo
        echo "## WARNING"
        echo "- ffmpeg si è interrotto subito dopo l'avvio (PID $FFMPEG_PID). Vedi audio/recording.log."
    } >> "$META"
    rm -f "$PIDFILE"
fi

# Aggiorna META con il PID effettivo e l'ora di start ffmpeg
{
    echo
    echo "## Tecnico"
    echo "- **ffmpeg PID:** $FFMPEG_PID"
    echo "- **ffmpeg start:** $NOW_HM (Europe/Rome)"
    echo "- **PulseAudio source:** $PULSE_SOURCE"
} >> "$META"

# Output finale: path della cartella call (l'unica riga su stdout)
echo "$CALL_DIR"
