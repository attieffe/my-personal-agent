#!/usr/bin/env python3
"""
padel_checker.py
Controlla i calendari .ics per partite di padel imminenti (15-30 min)
e invia il reminder su Telegram con la routine di preparazione.
Evita duplicati tramite _state/padel_notified.json.
"""

import re, json, os, sys, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

# ── Configurazione ──────────────────────────────────────────────────────────
BASE = "/home/openclaw/.openclaw/workspace/projects/myAgenda"
ICS_FILES = [
    f"{BASE}/calendars/padel_playtomic.ics",
    f"{BASE}/calendars/personale_gmail.ics",
]
ROUTINE_FILE = "/home/openclaw/.openclaw/workspace/projects/myJob/PERSONALE/hobby/32_padel.md"
STATE_FILE   = f"{BASE}/_state/padel_notified.json"

BOT_TOKEN = "8699275494:AAE13PcCiRgMr5ELrAtJMHodaCHCcbtQM3A"
CHAT_ID   = "-1003877516285"
TOPIC_ID  = 1

# Finestra: partite che iniziano tra WINDOW_MIN e WINDOW_MAX minuti da ora
WINDOW_MIN = 15
WINDOW_MAX = 35

PADEL_KEYWORDS = ["padel", "campo", "playtomic", "tennis", "racchett"]


# ── Parsing .ics ─────────────────────────────────────────────────────────────
def parse_ics_events(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, encoding="utf-8", errors="replace") as f:
        content = f.read()
    events = []
    for block in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", content, re.DOTALL):
        def get(field):
            m = re.search(rf"{field}[^:]*:(.*)", block)
            return m.group(1).strip() if m else ""
        dtstart_raw = get("DTSTART")
        summary     = get("SUMMARY")
        location    = get("LOCATION").replace("\\,", ",").replace("\\n", " ")
        events.append({
            "dtstart_raw": dtstart_raw,
            "summary": summary,
            "location": location,
        })
    return events


def parse_dt(raw):
    """Converte DTSTART raw in datetime UTC."""
    raw = raw.replace("Z", "")
    # Rimuove TZID=... se presente
    raw = re.sub(r"TZID=[^:]+:", "", raw)
    raw = raw.strip()
    if "T" in raw:
        try:
            dt = datetime.strptime(raw, "%Y%m%dT%H%M%S")
        except ValueError:
            return None
        # Assumiamo UTC se no Z, altrimenti Europe/Rome (offset +2 in estate)
        # Per semplicità usiamo UTC diretto (i file Playtomic usano UTC)
        return dt.replace(tzinfo=timezone.utc)
    else:
        # All-day: non è una partita con orario
        return None


def is_padel(summary):
    s = summary.lower()
    return any(kw in s for kw in PADEL_KEYWORDS)


# ── Stato notifiche ──────────────────────────────────────────────────────────
def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ── Routine di preparazione ──────────────────────────────────────────────────
def load_routine():
    if not os.path.exists(ROUTINE_FILE):
        return "(routine non trovata)"
    with open(ROUTINE_FILE, encoding="utf-8") as f:
        content = f.read()
    # Estrae solo la sezione "Routine di preparazione / concentrazione"
    m = re.search(
        r"## Routine di preparazione.*?\n(.*?)(?=\n---|\n## |\Z)",
        content, re.DOTALL
    )
    if not m:
        return "(sezione routine non trovata)"
    section = m.group(1).strip()
    # Pulisce markdown leggero
    lines = [l for l in section.splitlines() if l.strip() and not l.startswith("_")]
    return "\n".join(lines)


# ── Telegram ─────────────────────────────────────────────────────────────────
def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHAT_ID,
        "message_thread_id": TOPIC_ID,
        "text": text,
        "parse_mode": "HTML",
    }).encode()
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Errore Telegram: {e}", file=sys.stderr)
        return False


# ── Formattazione messaggio ──────────────────────────────────────────────────
def format_message(event, dt_rome):
    orario = dt_rome.strftime("%H:%M")
    luogo  = event["location"] or "luogo non specificato"
    partita = event["summary"]
    routine = load_routine()

    msg = (
        f"🎾 <b>Partita tra {WINDOW_MAX} minuti!</b>\n"
        f"<b>{partita}</b>\n"
        f"🕐 Ore {orario}  |  📍 {luogo}\n\n"
        f"<b>📋 Routine di preparazione:</b>\n"
        f"{routine}"
    )
    return msg


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    now_utc = datetime.now(timezone.utc)
    rome_offset = timedelta(hours=2)  # CEST (estate); aggiustare in inverno a +1

    state = load_state()
    # Pulizia stato vecchio (> 24h)
    cutoff = (now_utc - timedelta(hours=24)).isoformat()
    state = {k: v for k, v in state.items() if v > cutoff}

    found = False
    for ics_file in ICS_FILES:
        for event in parse_ics_events(ics_file):
            if not is_padel(event["summary"]):
                continue
            dt = parse_dt(event["dtstart_raw"])
            if dt is None:
                continue
            delta_min = (dt - now_utc).total_seconds() / 60
            if not (WINDOW_MIN <= delta_min <= WINDOW_MAX):
                continue

            # Chiave univoca: summary + ora inizio
            key = f"{event['summary']}_{dt.isoformat()}"
            if key in state:
                print(f"Già notificato: {key}")
                continue

            # Converti in ora italiana per il messaggio
            dt_rome = dt + rome_offset
            msg = format_message(event, dt_rome)
            ok = send_telegram(msg)
            if ok:
                state[key] = now_utc.isoformat()
                save_state(state)
                print(f"Reminder inviato: {event['summary']} alle {dt_rome.strftime('%H:%M')}")
                found = True
            else:
                print(f"Errore invio reminder per: {event['summary']}")

    if not found:
        print("Nessuna partita imminente.")


if __name__ == "__main__":
    main()
