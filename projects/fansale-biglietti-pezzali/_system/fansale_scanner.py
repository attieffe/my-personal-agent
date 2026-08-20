#!/usr/bin/env python3
"""FanSale Max Pezzali Milano monitor - scanner veloce con browser automation"""

import json
import time
from datetime import datetime
from pathlib import Path
import re
import sys

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ Playwright non disponibile. Installa: pip install playwright")
    print("   Poi: playwright install")
    sys.exit(1)

# Config
PROJECT_DIR = Path(__file__).parent.parent
EVENTS_FILE = PROJECT_DIR / "_system" / "eventi_list.json"
LOGS_DIR = PROJECT_DIR / "_logs"
LOGS_DIR.mkdir(exist_ok=True)

# URL base
BASE_URL = "https://www.fansale.it"
ARTIST_PAGE = f"{BASE_URL}/tickets/all/max-pezzali/482766"

def load_events():
    """Carica lista eventi da monitora"""
    with open(EVENTS_FILE) as f:
        data = json.load(f)
    return data["eventi"]

def extract_tickets(page):
    """Estrae biglietti dalla pagina evento"""
    tickets = []
    try:
        # Aspetta caricamento sezione biglietti
        page.wait_for_selector('section:has-text("Biglietti")', timeout=5000)

        # Estrai tutti i biglietti
        ticket_items = page.query_selector_all('[class*="offer"]')

        for item in ticket_items:
            text = item.inner_text()

            # Parse: Quantità, Blocco, Prezzo
            match_qty = re.search(r'Quantità\s+(\d+)', text)
            qty = int(match_qty.group(1)) if match_qty else 0

            # Cerca "Blocco B" oppure altri blocchi
            match_block = re.search(r'Blocco\s+([A-Z]\d+|[A-Z]{1,2})', text)
            block = match_block.group(1) if match_block else "Unknown"

            # Prezzo
            match_price = re.search(r'€\s*([\d,]+)', text)
            price = match_price.group(1) if match_price else "N/A"

            if qty > 0:
                tickets.append({
                    "quantita": qty,
                    "blocco": block,
                    "prezzo": price,
                    "full_text": text[:150]
                })
    except Exception as e:
        print(f"⚠️  Errore estrazione biglietti: {e}")

    return tickets

def scan_evento(browser, event_id, event_data, timestamp):
    """Scansiona un singolo evento"""
    try:
        context = browser.new_context()
        page = context.new_page()

        # Imposta timeout di pagina
        page.set_default_timeout(15000)

        data = {
            "event_id": event_id,
            "data": event_data["data"],
            "giorno": event_data["giorno"],
            "timestamp": timestamp,
            "tickets": [],
            "blocco_b_found": False,
            "error": None
        }

        try:
            # 1. Apri FanSale
            print(f"  📱 {event_data['data']} ({event_data['giorno']}): apri FanSale...")
            page.goto(BASE_URL, wait_until="networkidle")
            time.sleep(2)

            # 2. Click Max Pezzali
            print(f"  🎤 Click Max Pezzali...")
            try:
                page.click('a:has-text("Max Pezzali")', timeout=5000)
            except PlaywrightTimeout:
                # Prova con link diretto
                page.goto(ARTIST_PAGE, wait_until="networkidle")

            time.sleep(3)

            # 3. Click evento specifico
            event_url = f"{ARTIST_PAGE}/{event_id}"
            print(f"  📍 Click evento {event_data['data']}...")
            page.goto(event_url, wait_until="networkidle")
            time.sleep(6)

            # 4. Click "Carica Offerte"
            print(f"  ⬇️  Click 'Carica Offerte'...")
            try:
                load_btn = page.query_selector('button:has-text("Carica Offerte")')
                if load_btn:
                    load_btn.click()
                    time.sleep(7)
                else:
                    print(f"  ⚠️  Pulsante 'Carica Offerte' non trovato")
            except Exception as e:
                print(f"  ⚠️  Errore click Carica: {e}")

            # 5. Estrai biglietti
            print(f"  🎟️  Estraggo biglietti...")
            tickets = extract_tickets(page)

            # Filtra: Quantità ≥2, blocco B
            blocco_b_tickets = [t for t in tickets if t["quantita"] >= 2 and "B" in t["blocco"]]

            data["tickets"] = tickets
            data["blocco_b_tickets"] = blocco_b_tickets
            data["blocco_b_found"] = len(blocco_b_tickets) > 0

            if blocco_b_tickets:
                print(f"  ✅ **ALERT BLOCCO B**: {len(blocco_b_tickets)} biglietti trovati!")
            else:
                print(f"  ✓ Nessun blocco B con Qty≥2 ({len(tickets)} biglietti totali)")

        except Exception as e:
            print(f"  ❌ Errore: {e}")
            data["error"] = str(e)

        finally:
            context.close()

        return data

    except Exception as e:
        print(f"  ❌ Errore critico evento {event_id}: {e}")
        return {
            "event_id": event_id,
            "data": event_data["data"],
            "error": str(e),
            "tickets": [],
            "blocco_b_found": False
        }

def main():
    print("🚀 FanSale Max Pezzali Monitor - Scansione rapida")
    print(f"📅 Ora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Carica eventi
    eventi = load_events()
    print(f"📋 Monitorando {len(eventi)} eventi Milano...\n")

    timestamp = datetime.now().isoformat()
    results = {
        "timestamp": timestamp,
        "eventi_scansionati": [],
        "blocco_b_trovati": [],
        "errori": []
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])

        try:
            for i, event in enumerate(eventi, 1):
                print(f"[{i}/{len(eventi)}] {event['data']} ({event['giorno']})")

                result = scan_evento(browser, event["id"], event, timestamp)
                results["eventi_scansionati"].append(result)

                if result.get("blocco_b_found"):
                    results["blocco_b_trovati"].append({
                        "event_id": result["event_id"],
                        "data": result["data"],
                        "biglietti": result.get("blocco_b_tickets", [])
                    })

                if result.get("error"):
                    results["errori"].append({
                        "event_id": event["id"],
                        "data": event["data"],
                        "error": result["error"]
                    })

                # Delay tra eventi (anti-detection)
                if i < len(eventi):
                    time.sleep(2)

        finally:
            browser.close()

    # Salva risultati
    log_file = LOGS_DIR / f"monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "="*50)
    print(f"✅ Scansione completata!")
    print(f"📊 Biglietti totali scansionati: {sum(len(e.get('tickets', [])) for e in results['eventi_scansionati'])}")
    print(f"🎯 Blocchi B trovati: {len(results['blocco_b_trovati'])}")

    if results["blocco_b_trovati"]:
        print("\n**ALERT BLOCCO B TROVATI:**")
        for item in results["blocco_b_trovati"]:
            print(f"  - {item['data']}: {len(item['biglietti'])} biglietti")

    print(f"\n📁 Log salvato: {log_file}")

if __name__ == "__main__":
    main()
