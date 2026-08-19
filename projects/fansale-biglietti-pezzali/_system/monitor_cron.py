#!/usr/bin/env python3
"""
FanSale Monitor - Cron version
Controlla tutti gli eventi Max Pezzali e genera report per biglietti Qty≥2
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from playwright.async_api import async_playwright
except ImportError:
    logger.error("Playwright non installato. Installa con: pip install playwright")
    exit(1)


class FanSaleMonitor:
    def __init__(self):
        self.base_url = "https://www.fansale.it"
        self.event_url_template = "https://www.fansale.it/tickets/all/max-pezzali/482766"
        self.output_dir = Path(__file__).parent.parent / "_logs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Carica eventi
        eventi_file = Path(__file__).parent / "eventi_list.json"
        with open(eventi_file) as f:
            self.eventi = json.load(f)["eventi"]

    async def run(self):
        """Esecuzione principale: controlla tutti gli eventi"""
        logger.info(f"Avvio monitor per {len(self.eventi)} eventi")

        results = {"timestamp": datetime.now().isoformat(), "biglietti": []}

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ])
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            try:
                # Carica home e accept cookie (una volta sola)
                page = await context.new_page()
                await self.load_home(page)

                # Per ogni evento
                for evento in self.eventi:
                    logger.info(f"Controllando {evento['giorno']} {evento['data']}")
                    try:
                        tickets = await self.check_event(page, evento)
                        results["biglietti"].extend(tickets)
                        logger.info(f"  → {len(tickets)} biglietti idonei trovati")
                    except Exception as e:
                        logger.error(f"  Errore: {e}")
                        continue

                # Salva risultati
                self.save_results(results)
                logger.info(f"✅ Completato: {len(results['biglietti'])} biglietti totali")
                return results

            finally:
                await browser.close()

    async def load_home(self, page):
        """Carica home e accetta cookie"""
        logger.info("Caricamento home...")
        await page.goto(self.base_url + "/", wait_until="load")
        await asyncio.sleep(1)
        try:
            await page.click("button:has-text('Accept All Cookies')")
            await asyncio.sleep(1)
        except:
            pass

    async def check_event(self, page, evento: Dict) -> List[Dict]:
        """Controlla un singolo evento"""
        event_id = evento["id"]
        event_url = f"{self.event_url_template}/{event_id}"

        await page.goto(event_url, wait_until="load")
        await asyncio.sleep(1)

        # Clicca "Carica Offerte"
        try:
            await page.click("button:has-text('Carica Offerte')")
            await asyncio.sleep(2)
        except:
            logger.warning(f"  Bottone 'Carica Offerte' non trovato")
            return []

        # Estrai biglietti
        return await self.extract_tickets(page, evento)

    async def extract_tickets(self, page, evento: Dict) -> List[Dict]:
        """Estrai biglietti dalla pagina"""
        tickets = []

        # Usa JavaScript per estrarre i dati
        results = await page.evaluate("""
        () => {
            const items = [];
            document.querySelectorAll('[role="button"]').forEach(el => {
                const quantityEl = el.querySelector('[aria-label*="Quantità"]');
                const textEl = el.querySelector('div:nth-child(2)');

                if (quantityEl && textEl) {
                    const quantityText = quantityEl.textContent || '';
                    const quantity = parseInt(quantityText.split('Quantità')[1]?.trim() || '0');
                    const fullText = textEl.textContent || '';

                    if (quantity >= 2 && !fullText.includes('Parterre') && !fullText.includes('Posto Unico')) {
                        items.push({
                            quantity: quantity,
                            details: fullText,
                            raw: el.textContent
                        });
                    }
                }
            });
            return items;
        }
        """)

        # Elabora i risultati
        for item in results:
            # Estrai info dal testo
            details = item.get("details", "")
            quantity = item.get("quantity", 0)

            # Filtra BLOCCO B
            blocco = self.parse_blocco(details)

            ticket = {
                "data": evento["data"],
                "giorno": evento["giorno"],
                "evento_id": evento["id"],
                "quantita": quantity,
                "dettagli": details,
                "blocco": blocco,
                "alert_blocco_b": "YES" if blocco.startswith("B") else "NO",
                "prezzo": self.extract_price(details),
            }
            tickets.append(ticket)

        return tickets

    def parse_blocco(self, text: str) -> str:
        """Estrai il blocco dal testo"""
        # Formato: "Ingresso X | Fila Y | Posto Z | Blocco XX"
        parts = text.split("|")
        if len(parts) >= 4:
            blocco_part = parts[-1].strip()
            if "Blocco" in blocco_part:
                return blocco_part.replace("Blocco", "").strip()
        return "Unknown"

    def extract_price(self, text: str) -> str:
        """Estrai il prezzo dal testo"""
        import re
        match = re.search(r'€\s*([\d,\.]+)', text)
        return match.group(1) if match else "N/A"

    def save_results(self, results: Dict):
        """Salva risultati in JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"monitor_{timestamp}.json"
        output_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))
        logger.info(f"Salvato: {output_file}")


async def main():
    monitor = FanSaleMonitor()
    await monitor.run()


if __name__ == "__main__":
    asyncio.run(main())
