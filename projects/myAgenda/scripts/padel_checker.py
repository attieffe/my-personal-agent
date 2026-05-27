#!/usr/bin/env python3
"""
padel_checker.py
Controlla i calendari live per partite di padel imminenti (15-35 min)
e invia il reminder su Telegram con la routine di preparazione.
Evita duplicati tramite _state/padel_notified.json.
"""

import re, json, os, sys, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta

# ── Configurazione ──────────────────────────────────────────────────────────
BASE = "/home/openclaw/.openclaw/workspace/projects/myAgenda"
ICS_URLS = [
    "https://ingsoftware.it/ingsoftware/playtomic-ical/ical.php?auth=5uof_dBSABKnWtNZdQP9nm4yOkmlEM8gkCTRAsYS7ZT3lYqu__uuQiB22Sd5JJvBbdlqaP-9AsjcP0LpKdVgS5VGbCwtu19wQrA&asd=1",
    "https://calendar.google.com/calendar/ical/ing.fiumano%40gmail.com/private-1e6a7d3bbd7c548786476f11207ad71f/basic.ics?futureevents=true",
]
ROUTINE_FILE = "/home/openclaw/.openclaw/workspace/projects/myJob/PERSONALE/hobby/32_padel.md"
STATE_FILE   = f"{BASE}/_state/padel_notified.json"

BOT_TOKEN = "8699275494:AAE13PcCiRgMr5ELrAtJMHodaCHCcbtQM3A"
CHAT_ID   = "-1003877516285"
TOPIC_ID  = 1125

WINDOW_MIN = 15
WINDOW_MAX = 35

PADEL_KEYWORDS = ["padel", "campo", "playtomic", "tennis", "racchett"]


# ── Fetch ICS live ────────────────────────────────────────────────────────────
def fetch_ics(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "myAgenda/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"Errore fetch {url}: {e}", file=sys.stderr)
        return ""


# ── Parsing ICS ───────────────────────────────────────────────────────────────
def parse_ics_events(content):
    events = []
    for block in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", content, re.DOTALL):
        def get(field):
            m = re.search(rf"{field}[^:]*:(.*)", block)
            return m.group(1).strip() if m else ""
        events.append({
            "dtstart_raw": get("DTSTART"),
            "summary":     get("SUMMARY"),
            "location":    get("LOCATION").replace("\\,", ",").replace("\\n", " "),
        })
    return events


def parse_dt(raw, rome_offset=None):
    # TZID presente = orario già in ora locale (Europe/Rome), non UTC
    has_tzid = "TZID=" in raw
    raw = re.sub(r"TZID=[^:]+:", "", raw).strip()
    is_utc_explicit = raw.endswith("Z")
    raw = raw.replace("Z", "")
    if "T" not in raw:
        return None
    try:
        dt = datetime.strptime(raw, "%Y%m%dT%H%M%S")
        if has_tzid and not is_utc_explicit and rome_offset is not None:
            # Converti da ora Rome → UTC
            return dt.replace(tzinfo=timezone.utc) - rome_offset
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def is_padel(summary):
    return any(kw in summary.lower() for kw in PADEL_KEYWORDS)


# ── Stato notifiche ───────────────────────────────────────────────────────────
def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ── Routine di preparazione ───────────────────────────────────────────────────
def load_routine():
    if not os.path.exists(ROUTINE_FILE):
        return "(routine non trovata)"
    with open(ROUTINE_FILE, encoding="utf-8") as f:
        content = f.read()
    m = re.search(
        r"## Routine di preparazione.*?\n(.*?)(?=\n---|\n## |\Z)",
        content, re.DOTALL
    )
    if not m:
        return "(sezione routine non trovata)"
    lines = [l for l in m.group(1).strip().splitlines() if l.strip() and not l.startswith("_")]
    return "\n".join(lines)


# ── Telegram ──────────────────────────────────────────────────────────────────
def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHAT_ID,
        "message_thread_id": TOPIC_ID,
        "text": text,
        "parse_mode": "HTML",
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Errore Telegram: {e}", file=sys.stderr)
        return False


def format_message(event, dt_rome):
    orario  = dt_rome.strftime("%H:%M")
    luogo   = event["location"] or "luogo non specificato"
    routine = load_routine()
    return (
        f"🎾 <b>Partita tra {WINDOW_MAX} minuti!</b>\n"
        f"<b>{event['summary']}</b>\n"
        f"🕐 Ore {orario}  |  📍 {luogo}\n\n"
        f"<b>📋 Routine di preparazione:</b>\n{routine}\n\n"
        f"🧠 <a href=\"https://attibot.ingeniosolution.it/reports/padel-psicologia-sportiva.html\">Psicologia sportiva — gestione del loop mentale</a>"
    )


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    now_utc = datetime.now(timezone.utc)
    # Offset Europe/Rome: +2 CEST (mar-ott), +1 CET (nov-mar)
    month = now_utc.month
    rome_offset = timedelta(hours=2 if 3 < month < 11 else 1)

    state = load_state()
    cutoff = (now_utc - timedelta(hours=24)).isoformat()
    state = {k: v for k, v in state.items() if v > cutoff}

    found = False
    contents = []
    with ThreadPoolExecutor(max_workers=len(ICS_URLS)) as pool:
        futures = {pool.submit(fetch_ics, url): url for url in ICS_URLS}
        for fut in as_completed(futures):
            content = fut.result()
            if content:
                contents.append(content)

    for content in contents:
        for event in parse_ics_events(content):
            if not is_padel(event["summary"]):
                continue
            dt = parse_dt(event["dtstart_raw"], rome_offset)
            if dt is None:
                continue
            delta_min = (dt - now_utc).total_seconds() / 60
            if not (WINDOW_MIN <= delta_min <= WINDOW_MAX):
                continue

            key = f"{event['summary']}_{dt.isoformat()}"
            if key in state:
                print(f"Già notificato: {key}")
                continue

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
