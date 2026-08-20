#!/usr/bin/env python3
"""
FanSale Max Pezzali Monitor - Scraping automatico con anti-detection
Estrae biglietti Quantità ≥2, evidenzia BLOCCO B, salva JSON + notifica Telegram
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import time

# Config
WORKSPACE = Path("/home/openclaw/.openclaw/workspace")
PROJECT_DIR = WORKSPACE / "projects/fansale-biglietti-pezzali"
EVENTS_FILE = PROJECT_DIR / "_system" / "eventi_list.json"
LOGS_DIR = PROJECT_DIR / "_logs"
LOGS_DIR.mkdir(exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = LOGS_DIR / f"monitor_{TIMESTAMP}.json"

# FanSale URLs
BASE_URL = "https://www.fansale.it"
ARTIST_PAGE = "/tickets/all/max-pezzali/482766"

async def extract_biglietti(page, event_id, event_date):
    """Estrae biglietti dalla pagina evento con Quantità ≥2"""
    biglietti = []

    try:
        # Prendi tutti gli item di biglietti
        items = await page.locator("div[role='button']").filter(has=page.locator("text=Quantità")).all()

        for item in items:
            try:
                # Estrai info biglietto
                qty_elem = await item.locator("text=Quantità").evaluate(
                    "el => el.closest('*').nextElementSibling.textContent"
                )
                qty = int(qty_elem.strip() if qty_elem else "0")

                # Skip se quantità < 2
                if qty < 2:
                    continue

                # Estrai descrizione (posto/blocco)
                desc_elem = await item.locator("xpath=.//*").nth(1).inner_text()

                # Skip Parterre/Posto Unico/nominativi
                if any(x in desc_elem for x in ["PARTERRE", "Posto Unico", "nominativ"]):
                    continue

                # Estrai prezzo
                price_elem = await item.locator("text=€").inner_text()
                price = price_elem.strip() if price_elem else "N/A"

                # Estrai informazioni blocco (per BLOCCO B highlight)
                blocco_match = desc_elem
                is_blocco_b = "Blocco B" in blocco_match or " B" in blocco_match

                biglietti.append({
                    "quantita": qty,
                    "descrizione": desc_elem.strip(),
                    "prezzo": price,
                    "is_blocco_b": is_blocco_b
                })

            except Exception as e:
                continue

    except Exception as e:
        pass

    return biglietti

async def monitor_evento(browser, event_id, event_date, event_num, total_events):
    """Monitora un singolo evento seguendo il flusso anti-detection"""

    print(f"[{event_num}/{total_events}] Monitoraggio evento {event_date} (ID: {event_id})...")

    try:
        page = await browser.new_page()

        # Naviga all'evento
        url = f"{BASE_URL}/tickets/all/max-pezzali/482766/{event_id}"
        await page.goto(url, wait_until="networkidle")

        # Attendi 6 secondi (anti-detection)
        await asyncio.sleep(6)

        # Cerca e clicca "Carica Offerte" (può essere un button con testo o icona)
        try:
            load_btn = page.locator("button:has-text('Carica')")
            if await load_btn.count() > 0:
                await load_btn.click()
            else:
                # Fallback: clicca il pulsante non disabilitato nella toolbar
                toolbar_btns = await page.locator("button[disabled=false]").all()
                if toolbar_btns:
                    await toolbar_btns[0].click()
        except:
            pass

        # Attendi 7 secondi (anti-detection)
        await asyncio.sleep(7)

        # Estrai biglietti
        biglietti = await extract_biglietti(page, event_id, event_date)

        await page.close()

        return {
            "event_id": event_id,
            "data": event_date,
            "biglietti_trovati": len(biglietti),
            "biglietti": biglietti,
            "alert_blocco_b": sum(1 for b in biglietti if b.get("is_blocco_b"))
        }

    except Exception as e:
        print(f"❌ Errore evento {event_date}: {e}")
        return {
            "event_id": event_id,
            "data": event_date,
            "biglietti_trovati": 0,
            "biglietti": [],
            "alert_blocco_b": 0,
            "errore": str(e)
        }

async def main():
    # Leggi eventi
    with open(EVENTS_FILE) as f:
        data = json.load(f)

    eventi = data["eventi"]
    print(f"📅 Monitoraggio {len(eventi)} date Max Pezzali Milano...\n")

    results = {
        "timestamp": TIMESTAMP,
        "evento": "Max Pezzali - Milano",
        "date_scansionate": len(eventi),
        "biglietti_totali": 0,
        "alert_blocco_b_totali": 0,
        "eventi": []
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for idx, evento in enumerate(eventi, 1):
            result = await monitor_evento(
                browser,
                evento["id"],
                evento["data"],
                idx,
                len(eventi)
            )

            results["eventi"].append(result)
            results["biglietti_totali"] += result["biglietti_trovati"]
            results["alert_blocco_b_totali"] += result["alert_blocco_b"]

            # Delay tra eventi (anti-detection)
            if idx < len(eventi):
                await asyncio.sleep(2)

        await browser.close()

    # Salva risultati
    with open(LOG_FILE, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Monitoraggio completato!")
    print(f"📊 Risultati salvati: {LOG_FILE}")
    print(f"📌 Biglietti totali trovati: {results['biglietti_totali']}")
    print(f"🚨 ALERT BLOCCO B: {results['alert_blocco_b_totali']}")

    return results

if __name__ == "__main__":
    results = asyncio.run(main())
