#!/usr/bin/env bash
# call-orchestrate.sh <platform> <url> [--no-post]
#
# Orchestratore completo di una call:
#   Fase 1: call-start.sh    → crea cartella, avvia ffmpeg
#   Fase 2: call-log-join.sh → registra join del bot
#   Fase 3: join browser     → call-join-meet.js (o equivalente per zoom/teams)
#   Fase 4: call-monitor.sh  → loop monitoring partecipanti + exit condition
#   Fase 5: call-stop.sh     → stop ffmpeg, finalizza META.md
#   Fase 6: call-post.sh     → Whisper + SINTESI.md + invio Telegram (opzionale)
#
# Uso: call-orchestrate.sh meet https://meet.google.com/xxx-yyyy-zzz
#      call-orchestrate.sh meet https://... --no-post   (salta fase post-call)
#
# Exit code: 0 OK, 1 parametri, 2 errore critico, 3 platform non supportata

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -lt 2 ]]; then
    echo "Usage: call-orchestrate.sh <platform> <url> [--no-post]" >&2
    echo "  platform: meet | zoom | teams" >&2
    exit 1
fi

PLATFORM="$1"
URL="$2"
NO_POST=0
if [[ "${3:-}" == "--no-post" ]]; then NO_POST=1; fi

log() {
    local ts
    ts=$(TZ="Europe/Rome" date +'%Y-%m-%d %H:%M')
    echo "[$ts] [orchestrate] $*"
}

log "Avvio orchestratore — platform=$PLATFORM url=$URL"

# ---- Fase 1: init cartella + avvio ffmpeg ----
log "Fase 1 — init call e avvio registrazione"
CALL_DIR=$("$SCRIPT_DIR/call-start.sh" "$PLATFORM" "$URL")
if [[ -z "$CALL_DIR" || ! -d "$CALL_DIR" ]]; then
    log "ERRORE: call-start.sh non ha restituito una cartella valida"
    exit 2
fi
log "Cartella call: $CALL_DIR"

# Trap per cleanup in caso di errore imprevisto
cleanup() {
    log "TRAP cleanup — stop ffmpeg e finalizzazione"
    "$SCRIPT_DIR/call-stop.sh" "$CALL_DIR" 2>/dev/null || true
    # Termina browser se ancora attivo
    if [[ -f "$CALL_DIR/browser.pid" ]]; then
        BPID=$(cat "$CALL_DIR/browser.pid")
        kill "$BPID" 2>/dev/null || true
    fi
}
trap cleanup ERR

# ---- Fase 3: join browser ----
log "Fase 3 — join $PLATFORM"
case "$PLATFORM" in
    meet)
        BROWSER_SCRIPT="$SCRIPT_DIR/call-join-meet.js"
        if [[ ! -f "$BROWSER_SCRIPT" ]]; then
            log "ERRORE: script browser non trovato: $BROWSER_SCRIPT"
            exit 3
        fi
        # Avvia il join in background (il processo resta vivo per tutto il monitoring)
        node "$BROWSER_SCRIPT" "$CALL_DIR" "$URL" &
        BROWSER_PID=$!
        echo "$BROWSER_PID" > "$CALL_DIR/browser.pid"
        log "Browser avviato (PID $BROWSER_PID)"
        ;;
    teams)
        BROWSER_SCRIPT="$SCRIPT_DIR/call-join-teams.js"
        if [[ ! -f "$BROWSER_SCRIPT" ]]; then
            log "ERRORE: script browser non trovato: $BROWSER_SCRIPT"
            exit 3
        fi
        node "$BROWSER_SCRIPT" "$CALL_DIR" "$URL" &
        BROWSER_PID=$!
        echo "$BROWSER_PID" > "$CALL_DIR/browser.pid"
        log "Browser Teams avviato (PID $BROWSER_PID)"
        ;;
    zoom)
        log "ERRORE: platform zoom non ancora implementata"
        exit 3
        ;;
    *)
        log "ERRORE: platform sconosciuta: $PLATFORM"
        exit 3
        ;;
esac

# Attende che browser-status.json compaia (conferma che il join è avvenuto)
log "Attesa conferma join (max 90s)..."
for i in $(seq 1 90); do
    if [[ -f "$CALL_DIR/active.lock" ]]; then
        log "Join confermato (active.lock presente)"
        break
    fi
    if ! kill -0 "$BROWSER_PID" 2>/dev/null; then
        log "ERRORE: processo browser terminato prima del join"
        exit 2
    fi
    sleep 1
    if [[ "$i" -eq 90 ]]; then
        log "TIMEOUT: join non confermato entro 90s"
        exit 2
    fi
done

# ---- Auto-routing audio Chromium → virtual_out ----
# Il browser OpenClaw non punta automaticamente a virtual_out — bisogna spostare i sink input.
# Attende max 15s che Chromium registri i suoi sink input in PulseAudio.
log "Auto-routing audio Chromium → virtual_out..."
for i in $(seq 1 15); do
    CHROMIUM_INPUTS=$(pactl list sink-inputs short 2>/dev/null | grep -i chromium | awk '{print $1}' || true)
    if [[ -n "$CHROMIUM_INPUTS" ]]; then
        for SID in $CHROMIUM_INPUTS; do
            pactl move-sink-input "$SID" virtual_out 2>/dev/null && log "Sink input $SID → virtual_out OK"
        done
        break
    fi
    sleep 1
done
# Verifica livello audio (non silenzio = routing OK)
LEVEL=$(ffmpeg -nostdin -f pulse -i virtual_out.monitor -t 3 -filter:a volumedetect -f null /dev/null 2>&1 | grep max_volume | sed -E 's/.*max_volume: //' | xargs || echo "n/a")
log "Livello audio su virtual_out: $LEVEL"

# ---- Fase 2: log join bot in META.md ----
log "Fase 2 — log join bot"
"$SCRIPT_DIR/call-log-join.sh" "$CALL_DIR"

# ---- Fase 4: monitoring partecipanti ----
log "Fase 4 — avvio monitoring"
# call-monitor.sh termina da solo quando la exit condition è soddisfatta
"$SCRIPT_DIR/call-monitor.sh" "$CALL_DIR" || true
log "Monitoring terminato"

# ---- Fase 5: stop ffmpeg + finalizzazione ----
log "Fase 5 — stop registrazione"

# Termina il browser prima di call-stop (log leave)
if [[ -f "$CALL_DIR/browser.pid" ]]; then
    BPID=$(cat "$CALL_DIR/browser.pid")
    kill -SIGTERM "$BPID" 2>/dev/null || true
    sleep 3
fi

"$SCRIPT_DIR/call-stop.sh" "$CALL_DIR"
log "Registrazione fermata"

# Disattiva trap ora che siamo in shutdown controllato
trap - ERR

# ---- Fase 6: post-call (Whisper + sintesi + Telegram) ----
if [[ "$NO_POST" -eq 0 ]]; then
    log "Fase 6 — post-call (trascrizione + sintesi)"
    if "$SCRIPT_DIR/call-post.sh" "$CALL_DIR"; then
        log "Post-call completata"
    else
        log "WARN: post-call fallita — segmenti audio intatti in $CALL_DIR/audio/segments/"
        log "Puoi rieseguire: $SCRIPT_DIR/call-post.sh $CALL_DIR"
    fi
else
    log "Fase 6 skippata (--no-post)"
    log "Rieseguire manualmente: $SCRIPT_DIR/call-post.sh $CALL_DIR"
fi

log "Call completata — $CALL_DIR"
