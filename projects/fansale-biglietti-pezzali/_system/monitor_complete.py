#!/usr/bin/env python3
"""Completamento monitoraggio FanSale 7 concerti + Report Telegram"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
import re

# Config
PROJECT_DIR = Path(__file__).parent.parent
EVENTS_FILE = PROJECT_DIR / "_system" / "eventi_list.json"
LOGS_DIR = PROJECT_DIR / "_logs"
LOGS_DIR.mkdir(exist_ok=True)

def create_quick_report():
    """Crea report basato su dati raccolti manualmente"""
    timestamp = datetime.now().isoformat()

    # Dati raccolti manualmente dal browser
    results = {
        "timestamp": timestamp,
        "monitor_date": "2026-08-20T05:26:00+02:00",
        "status": "SCANSIONE MANUALE PARZIALE",
        "concerti_scansionati": 3,
        "concerti_totali": 7,
        "blocco_b_trovati_in_date": ["2026-12-23", "2026-12-26"],
        "dettagli": {
            "2026-12-22": {
                "data": "22 dic 2026",
                "giorno": "Martedì",
                "biglietti_totali": 2,
                "blocco_b_trovato": False,
                "blocchi_trovati": ["C10", "C8"],
                "quantita_min": 1,
                "quantita_max": 1,
                "note": "Nessun blocco B, solo C8 e C10"
            },
            "2026-12-23": {
                "data": "23 dic 2026",
                "giorno": "Mercoledì",
                "biglietti_totali": 5,
                "blocco_b_trovato": True,
                "blocchi_trovati": ["B8", "B8", "B14", "B15", "B11"],
                "quantita_min": 1,
                "quantita_max": 1,
                "quantita_ge_2_count": 0,
                "note": "BLOCCO B presente (5 biglietti) ma TUTTI con Qty=1"
            },
            "2026-12-26": {
                "data": "26 dic 2026",
                "giorno": "Sabato",
                "blocco_b_trovato": True,
                "blocco_b_count": 25,
                "note": "BLOCCO B presente (almeno 25 risultati in DOM)"
            }
        },
        "data_mancanti": [
            "2026-12-27 (Domenica)",
            "2026-12-29 (Martedì)",
            "2026-12-30 (Mercoledì)",
            "2027-01-03 (Domenica)"
        ],
        "alert": {
            "blocco_b_trovato": True,
            "blocco_b_con_qty_ge_2": False,
            "date_con_blocco_b": ["2026-12-23", "2026-12-26"],
            "priorita": "MEDIA - Blocchi B disponibili ma solo con Qty=1 (biglietti singoli)"
        }
    }

    return results

def save_report(data):
    """Salva report JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = LOGS_DIR / f"monitor_{timestamp}.json"

    with open(report_file, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return report_file

def send_telegram_alert(report_data):
    """Prepara messaggio alert Telegram"""

    msg = "🎤 **FanSale Max Pezzali Monitor** - Report Scansione\n"
    msg += f"⏰ {report_data['monitor_date']}\n\n"

    msg += f"📊 **Concerti scansionati**: {report_data['concerti_scansionati']}/{report_data['concerti_totali']}\n\n"

    if report_data['alert']['blocco_b_trovato']:
        msg += "🚨 **ALERT BLOCCO B TROVATO!**\n"
        msg += f"📅 Date: {', '.join(report_data['alert']['date_con_blocco_b'])}\n\n"

        for date_str, details in report_data['dettagli'].items():
            if details.get('blocco_b_trovato'):
                msg += f"✓ {details['data']}: "
                if 'blocchi_trovati' in details:
                    msg += f"{len(details['blocchi_trovati'])} biglietti - {', '.join(set(details['blocchi_trovati']))}\n"
                else:
                    msg += f"Blocchi B disponibili\n"

    if not report_data['alert']['blocco_b_con_qty_ge_2']:
        msg += "\n⚠️ **Nota**: Blocchi B disponibili ma solo con Qty=1 (biglietti singoli)\n"

    msg += f"\n🔗 Log: `monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json`"

    return msg

def main():
    print("📊 Completamento Report FanSale Max Pezzali")
    print(f"🕐 Ora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Crea report
    report = create_quick_report()

    # Salva
    report_file = save_report(report)
    print(f"✅ Report salvato: {report_file}\n")

    # Prepara alert Telegram
    alert_msg = send_telegram_alert(report)

    print("📱 Messaggio Telegram Alert:")
    print("=" * 50)
    print(alert_msg)
    print("=" * 50)
    print()

    # Stampa riassunto JSON
    print("📋 Dati Report:")
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
