#!/usr/bin/env bash
# call-monitor.sh <call_dir>
#
# Loop di monitoring in-call. Ogni POLL_INTERVAL secondi:
#   - Legge browser-status.json (scritto da call-join-meet.js)
#   - Loga variazioni di partecipanti in META.md
#   - Rileva exit condition: partecipanti == 1 (solo bot) per EXIT_GRACE_MIN minuti
#   - Verifica che ffmpeg stia ancora scrivendo (segmenti audio crescono)
#
# Termina da solo quando la exit condition è soddisfatta.
# Exit code: 0 exit normale, 1 parametri, 2 call_dir non trovato, 3 timeout hard

set -euo pipefail

POLL_INTERVAL=60          # secondi tra ogni check
EXIT_GRACE_MIN=2          # minuti da solo prima di uscire
HARD_TIMEOUT_MIN=240      # timeout massimo assoluto (4 ore)

if [[ $# -lt 1 ]]; then
    echo "Usage: call-monitor.sh <call_dir>" >&2
    exit 1
fi

CALL_DIR="$1"
META="$CALL_DIR/META.md"
STATUS_FILE="$CALL_DIR/browser-status.json"
SEG_DIR="$CALL_DIR/audio/segments"
LOCK_FILE="$CALL_DIR/active.lock"

if [[ ! -d "$CALL_DIR" ]]; then
    echo "ERROR: call_dir non trovato: $CALL_DIR" >&2
    exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_PARTICIPANT="$SCRIPT_DIR/call-log-participant.sh"

# Stato tracking
prev_participants=-1
alone_since=0
start_epoch=$(date +%s)
hard_timeout=$((HARD_TIMEOUT_MIN * 60))
prev_audio_size=0

log() {
    local ts
    ts=$(TZ="Europe/Rome" date +'%Y-%m-%d %H:%M')
    echo "[$ts] $*"
}

log "Monitoring avviato — poll ogni ${POLL_INTERVAL}s, exit grace ${EXIT_GRACE_MIN}min"

while true; do
    now_epoch=$(date +%s)
    elapsed=$(( now_epoch - start_epoch ))

    # Hard timeout
    if [[ $elapsed -gt $hard_timeout ]]; then
        log "HARD TIMEOUT (${HARD_TIMEOUT_MIN}min) — forzo uscita"
        exit 3
    fi

    # Leggi status dal browser (se esiste)
    current_participants=0
    status_error=""
    if [[ -f "$STATUS_FILE" ]]; then
        current_participants=$(python3 -c "
import json, sys
try:
    d = json.load(open('$STATUS_FILE'))
    print(d.get('participants', 0))
except:
    print(0)
" 2>/dev/null || echo 0)
        status_error=$(python3 -c "
import json
try:
    d = json.load(open('$STATUS_FILE'))
    print(d.get('error',''))
except:
    print('')
" 2>/dev/null || echo "")
    fi

    if [[ -n "$status_error" ]]; then
        log "WARN browser-status error: $status_error"
    fi

    # Rileva variazioni partecipanti
    if [[ "$current_participants" -ne "$prev_participants" && "$prev_participants" -ne -1 ]]; then
        delta=$(( current_participants - prev_participants ))
        if [[ $delta -gt 0 ]]; then
            log "Partecipanti: ${prev_participants} → ${current_participants} (+${delta})"
        else
            log "Partecipanti: ${prev_participants} → ${current_participants} (${delta})"
        fi
    fi
    prev_participants=$current_participants

    # Watchdog audio: verifica che ffmpeg stia scrivendo segmenti E che crescano
    latest_segment=""
    if [[ -d "$SEG_DIR" ]]; then
        latest_segment=$(ls -1t "$SEG_DIR"/segment-*.mp3 2>/dev/null | head -n1 || true)
    fi
    if [[ -n "$latest_segment" && -f "$latest_segment" ]]; then
        audio_size=$(stat -c%s "$latest_segment" 2>/dev/null || echo 0)
        if [[ "$audio_size" -eq 0 ]]; then
            log "WARN: ultimo segmento audio è ancora 0 bytes — ffmpeg potrebbe non funzionare"
        elif [[ "$prev_audio_size" -gt 0 && "$audio_size" -eq "$prev_audio_size" ]]; then
            log "WARN: ultimo segmento audio non cresce da ultimo check ($audio_size bytes) — ffmpeg potrebbe essere fermo"
        else
            # File cresce normalmente
            prev_audio_size=$audio_size
        fi
    else
        log "WARN: nessun segmento audio trovato in audio/segments/"
    fi

    # Exit condition: solo bot rimasto per EXIT_GRACE_MIN minuti
    if [[ "$current_participants" -le 1 ]]; then
        if [[ "$alone_since" -eq 0 ]]; then
            alone_since=$now_epoch
            log "Solo bot rimasto — avvio grace period ${EXIT_GRACE_MIN}min"
        else
            alone_elapsed=$(( now_epoch - alone_since ))
            grace_secs=$(( EXIT_GRACE_MIN * 60 ))
            log "Solo bot da ${alone_elapsed}s / ${grace_secs}s prima di exit"
            if [[ $alone_elapsed -ge $grace_secs ]]; then
                log "Exit condition soddisfatta — avvio shutdown call"
                exit 0
            fi
        fi
    else
        # Tornati ad avere partecipanti → reset grace
        if [[ "$alone_since" -ne 0 ]]; then
            log "Partecipanti rientrati — reset grace period"
            alone_since=0
        fi
    fi

    sleep "$POLL_INTERVAL"
done
