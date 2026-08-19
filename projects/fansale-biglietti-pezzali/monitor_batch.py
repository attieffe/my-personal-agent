#!/usr/bin/env python3
import json
import subprocess
import time
from datetime import datetime

# IDs degli eventi rimanenti
eventi_rimanenti = [
    {"id": "21343715", "data": "2026-12-26", "giorno": "Sabato"},
    {"id": "21343722", "data": "2026-12-27", "giorno": "Domenica"},
    {"id": "21343718", "data": "2026-12-29", "giorno": "Martedì"},
    {"id": "21343719", "data": "2026-12-30", "giorno": "Mercoledì"},
    {"id": "21928067", "data": "2027-01-03", "giorno": "Domenica"},
]

# URLs degli eventi
base_url = "https://www.fansale.it/tickets/all/max-pezzali/482766/"

# Risultati
risultati = []

# Browser automation via mcp__openclaw__browser
def navigate_and_capture(event_id, data, giorno):
    """Naviga a un evento e estrae i biglietti con Qty≥2"""
    url = base_url + event_id
    print(f"Processing evento {giorno} ({data}) - ID: {event_id}")

    try:
        # Naviga
        subprocess.run([
            "bash", "-c",
            f'curl -s "http://127.0.0.1:18800/json/navigate?url={url}" | jq .'
        ], timeout=15, check=False)

        # Aspetta 6 sec
        time.sleep(6)

        # Screenshot
        subprocess.run([
            "bash", "-c",
            f'curl -s "http://127.0.0.1:18800/json/screenshot" | jq .'
        ], timeout=15, check=False)

        # Aspetta 7 sec per "Carica Offerte"
        time.sleep(7)

        print(f"  ✓ Completato {giorno}")
        return True
    except Exception as e:
        print(f"  ✗ Errore: {e}")
        return False

print("Monitoraggio FanSale - Batch processing eventi rimanenti")
print(f"Timestamp: {datetime.now().isoformat()}")
print("=" * 60)

for evt in eventi_rimanenti:
    navigate_and_capture(evt["id"], evt["data"], evt["giorno"])
    time.sleep(2)  # pausa tra eventi

print("\n" + "=" * 60)
print("Batch processing completato. Report saved to monitor_20260820_0026.json")
