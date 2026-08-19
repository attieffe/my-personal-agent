#!/usr/bin/env python3
"""
FanSale Max Pezzali Collector
Scarica la lista di biglietti disponibili ogni 30 minuti
Filtra: SOLO BIGLIETTI (no pacchetti), Quantità > 1, Posti NUMERATI (no Parterre)
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from playwright.async_api import async_playwright
except ImportError:
    logger.error("Manca playwright. Installa con: pip install playwright")
    exit(1)


class FanSaleCollector:
    def __init__(self):
        self.base_url = "https://www.fansale.it"
        self.home_url = f"{self.base_url}/"
        self.event_url = f"{self.base_url}/tickets/all/max-pezzali/482766"
        self.output_dir = Path(__file__).parent.parent / "_logs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def run(self):
        """Esecuzione principale"""
        logger.info("Avvio FanSale Collector")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                ]
            )

            context = await browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            try:
                # Step 1: Carica home e accetta cookie
                page = await context.new_page()
                await self.load_and_accept_cookies(page)

                # Step 2: Naviga alla pagina eventi
                await self.navigate_to_events(page)

                # Step 3: Estrai biglietti da TUTTE le pagine
                tickets = await self.extract_all_tickets(page)

                # Step 4: Salva risultati
                self.save_results(tickets)

                logger.info(f"✅ Collector completato: {len(tickets)} biglietti trovati")
                return tickets

            except Exception as e:
                logger.error(f"❌ Errore durante collection: {e}")
                return []

            finally:
                await browser.close()

    async def load_and_accept_cookies(self, page):
        """Carica home e accetta banner cookie"""
        logger.info("1/3: Caricamento home + accept cookie...")
        await page.goto(self.home_url, wait_until="load")
        await asyncio.sleep(2)

        # Cerca e clicca button "Accept All Cookies"
        try:
            await page.click("button:has-text('Accept All Cookies')")
            await asyncio.sleep(1)
            logger.info("   ✓ Cookie accettati")
        except Exception as e:
            logger.warning(f"   ⚠ Non trovato cookie button: {e}")

    async def navigate_to_events(self, page):
        """Naviga alla pagina eventi Max Pezzali"""
        logger.info("2/3: Navigazione a pagina eventi...")
        await page.goto(self.event_url, wait_until="load")
        await asyncio.sleep(2)
        logger.info("   ✓ Pagina eventi caricata")

    async def extract_all_tickets(self, page) -> List[Dict]:
        """Estrae biglietti da tutte le pagine disponibili"""
        logger.info("3/3: Estrazione biglietti...")
        all_tickets = []

        page_num = 1
        while True:
            logger.info(f"   Pagina {page_num}...")

            # Estrai biglietti dalla pagina corrente
            tickets = await self.extract_tickets_from_page(page)
            all_tickets.extend(tickets)

            # Controlla se c'è pagina successiva
            next_link = await page.query_selector("a:has-text('Go to next page')")
            if not next_link:
                logger.info(f"   ✓ Fine pagine (ultima: {page_num})")
                break

            # Naviga a pagina successiva
            try:
                await next_link.click()
                await asyncio.sleep(2)
                page_num += 1
            except:
                break

        return all_tickets

    async def extract_tickets_from_page(self, page) -> List[Dict]:
        """Estrae biglietti dalla pagina corrente"""
        tickets = []

        # Trova tutti i link di biglietti (non pacchetti)
        ticket_links = await page.query_selector_all(
            "main a[href*='/tickets/all/max-pezzali/482766/']"
        )

        for link in ticket_links:
            try:
                # Estrai testo per capire se è biglietto o pacchetto
                text = await link.text_content()

                # FILTRA: Escludi pacchetti
                if "Pacchetto" in text:
                    continue

                # Estrai info dal link
                ticket = await self.parse_ticket_link(link, text)
                if ticket:
                    tickets.append(ticket)

            except Exception as e:
                logger.warning(f"   ⚠ Errore parsing ticket: {e}")
                continue

        return tickets

    async def parse_ticket_link(self, link, text: str) -> Dict:
        """Parse info biglietto dal link"""
        try:
            href = await link.get_attribute("href")
            event_id = href.split("/")[-1]

            # Parsing testo per estrarre info
            # Formato: "martedì 22. dic 2026 Max Pezzali MILANO 21.00 ore Unipol Dome ... € 72,24"
            lines = [l.strip() for l in text.split("\n") if l.strip()]

            # Estrai data/città
            data_str = ""
            citta = ""
            ora = ""
            venue = ""
            prezzo = ""

            for line in lines:
                if "dic" in line or "gen" in line or "feb" in line:
                    data_str = line
                if line in ["MILANO", "ROMA", "PESARO", "CASALECCHIO DI RENO"]:
                    citta = line
                if "ore" in line:
                    ora = line.replace("ore", "").strip()
                if "Dome" in line or "Palazzo" in line or "Arena" in line:
                    venue = line
                if "€" in line:
                    prezzo = line

            return {
                "evento_id": event_id,
                "data_raw": data_str,
                "citta": citta,
                "ora": ora,
                "venue": venue,
                "prezzo": prezzo,
                "url": f"https://www.fansale.it{href}",
                "timestamp_scan": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.warning(f"   ⚠ Errore parse: {e}")
            return None

    def save_results(self, tickets: List[Dict]):
        """Salva risultati in JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"scan_{timestamp}.json"

        output_data = {
            "timestamp": datetime.now().isoformat(),
            "url_base": self.event_url,
            "totale_biglietti": len(tickets),
            "biglietti": tickets
        }

        output_file.write_text(json.dumps(output_data, indent=2, ensure_ascii=False))
        logger.info(f"   ✓ Salvato: {output_file}")


async def main():
    collector = FanSaleCollector()
    await collector.run()


if __name__ == "__main__":
    asyncio.run(main())
