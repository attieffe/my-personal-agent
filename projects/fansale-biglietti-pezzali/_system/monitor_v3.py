#!/usr/bin/env python3
"""
FanSale Monitor v3 - Versione semplificata
Delega tutto al cron OpenClaw usando il browser tool via MCP
Questo script viene eseguito dal cron e usa i tool OpenClaw disponibili
"""

import json
import time
from datetime import datetime
from pathlib import Path

# Carica eventi
eventi_file = Path(__file__).parent / "eventi_list.json"
eventi_data = json.loads(eventi_file.read_text())
eventi = eventi_data["eventi"]

base_url = "https://www.fansale.it/tickets/all/max-pezzali/482766"

print(f"Monitor FanSale: controllo {len(eventi)} eventi")
print("NOTA: Questo script richiede accesso ai tool OpenClaw (browser, message)")
print("Deve essere eseguito da un cron job OpenClaw con toolsAllow appropriati\n")

# Per ora stampa solo le info
# La logica vera andrà implementata come skill o agent dedicato
for ev in eventi:
    print(f"TODO: {ev['giorno']} {ev['data']} - {base_url}/{ev['id']}")

print("\nPer implementazione completa: creare skill dedicato con accesso browser tool")
