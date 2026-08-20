#!/usr/bin/env python3
"""
FanSale Quick Extraction - Estrae biglietti da pagina già caricata
Navigazione rapida attraverso 7 date Milano
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from playwright.async_api import async_playwright
except ImportError:
    logger.error("Manca playwright")
    exit(1)


async def extract_tickets_from_page(page):
    """Estrae biglietti dalla pagina corrente"""
    tickets = []

    try:
        # Attendi che la pagina sia pronta
        await page.wait_for_load_state("networkidle", timeout=10000)

        # Estrai tutti i row dei biglietti
        rows = await page.query_selector_all("div[class*='ticket'], tr[class*='row']")

        logger.info(f"   Trovate {len(rows)} righe di biglietti")

        for row in rows:
            try:
                text = await row.text_content()

                if not text or "Quantità" not in text:
                    continue

                # Parsing semplice
                lines = text.strip().split("\n")

                # Estrai quantità (numero dopo "Quantità")
                qty = 1
                for line in lines:
                    if "Quantità" in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if "Quantità" in part and i + 1 < len(parts):
                                try:
                                    qty = int(parts[i + 1])
                                    break
                                except:
                                    pass

                # Filtra: solo Quantità >= 2, escludi Parterre e Posto Unico
                full_text = " ".join(lines).upper()
                if qty >= 2 and "PARTERRE" not in full_text and "POSTO UNICO" not in full_text:

                    # Estrai informazioni
                    ticket_info = {
                        "descrizione": " | ".join(lines[:3]),
                        "quantita": qty,
                        "prezzo": "N/A",
                        "blocco": "N/A",
                        "text_raw": text[:200]
                    }

                    # Cerca prezzo
                    for line in lines:
                        if "€" in line:
                            ticket_info["prezzo"] = line.strip()

                    # Cerca blocco
                    for line in lines:
                        if "Blocco" in line:
                            ticket_info["blocco"] = line.split("Blocco")[-1].strip()

                    tickets.append(ticket_info)

            except Exception as e:
                logger.debug(f"   Errore parsing riga: {e}")
                continue

        return tickets

    except Exception as e:
        logger.warning(f"   Errore estrazione: {e}")
        return tickets


async def main():
    # Carica eventi
    config_dir = Path(__file__).parent.parent / "_system"
    eventi_file = config_dir / "eventi_list.json"
    output_dir = config_dir.parent / "_logs"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(eventi_file) as f:
        data = json.load(f)
        eventi = data.get("eventi", [])

    logger.info(f"🚀 Estrazione rapida {len(eventi)} eventi")

    all_tickets = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )

        try:
            page = await context.new_page()

            # Carica pagina artista
            logger.info("Caricamento pagina Max Pezzali...")
            await page.goto(
                "https://www.fansale.it/tickets/all/max-pezzali/482766",
                wait_until="load",
                timeout=30000
            )
            await asyncio.sleep(4)

            # Per ogni evento
            for i, event in enumerate(eventi, 1):
                logger.info(f"\n{i}. Evento {event['data']} (ID: {event['id']})")

                # Naviga a evento specifico
                event_url = f"https://www.fansale.it/tickets/all/max-pezzali/482766/{event['id']}"
                await page.goto(event_url, wait_until="load", timeout=15000)
                await asyncio.sleep(2)

                # Estrai biglietti
                tickets = await extract_tickets_from_page(page)
                all_tickets[event['data']] = {
                    "evento_id": event['id'],
                    "biglietti_count": len(tickets),
                    "biglietti": tickets
                }

                logger.info(f"   ✓ {len(tickets)} biglietti estratti")
                await asyncio.sleep(3)

            # Salva risultati
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"monitor_{timestamp}_rapid.json"

            # Conta per blocco
            blocco_count = {}
            total = 0
            for data, info in all_tickets.items():
                for ticket in info['biglietti']:
                    blocco = ticket.get('blocco', 'N/A')
                    blocco_count[blocco] = blocco_count.get(blocco, 0) + 1
                    total += 1

            result = {
                "timestamp": datetime.now().isoformat(),
                "totale_biglietti": total,
                "biglietti_per_blocco": blocco_count,
                "per_data": all_tickets,
                "alert_blocco_b": blocco_count.get("B", 0) > 0,
                "blocco_b_count": blocco_count.get("B", 0)
            }

            output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))
            logger.info(f"\n✅ Completato: {total} biglietti totali")
            logger.info(f"   BLOCCO B: {blocco_count.get('B', 0)} biglietti")
            logger.info(f"   Salvato: {output_file}")

            return result

        except Exception as e:
            logger.error(f"❌ Errore: {e}", exc_info=True)
            return {}

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
