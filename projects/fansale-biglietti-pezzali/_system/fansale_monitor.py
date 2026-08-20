#!/usr/bin/env python3
"""
FanSale Max Pezzali Monitor - Flusso Anti-Detection
Monitoraggio 7 date Milano con delay anti-detection specifici
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

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


class FanSaleMonitor:
    def __init__(self):
        self.base_url = "https://www.fansale.it"
        self.home_url = f"{self.base_url}/"
        self.event_artist_url = f"{self.base_url}/tickets/all/max-pezzali/482766"

        # Carica lista eventi
        self.config_dir = Path(__file__).parent
        self.eventi_file = self.config_dir / "eventi_list.json"
        self.output_dir = self.config_dir.parent / "_logs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.eventi = []
        self.load_eventi()

    def load_eventi(self):
        """Carica lista eventi da JSON"""
        if self.eventi_file.exists():
            with open(self.eventi_file) as f:
                data = json.load(f)
                self.eventi = data.get("eventi", [])
                logger.info(f"Caricati {len(self.eventi)} eventi")
        else:
            logger.error(f"File non trovato: {self.eventi_file}")
            exit(1)

    async def run(self):
        """Esecuzione principale con flusso anti-detection"""
        logger.info("🚀 Avvio FanSale Monitor - Flusso Anti-Detection")

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
                page = await context.new_page()

                # Step 1: Carica home con retry
                logger.info("1️⃣ Apertura https://www.fansale.it/")
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        await page.goto(self.home_url, wait_until="load", timeout=30000)
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            logger.warning(f"   Retry {attempt+1}/{max_retries-1}: {str(e)[:50]}")
                            await asyncio.sleep(2)
                        else:
                            raise

                # Step 2: Attendi 5 sec
                logger.info("2️⃣ Attesa 5 sec (anti-detection)")
                await asyncio.sleep(5)

                # Step 3: Clicca link Max Pezzali
                logger.info("3️⃣ Click su 'Max Pezzali'")
                await page.click("a[href='/tickets/all/max-pezzali/482766']")

                # Step 4: Attendi 4 sec
                logger.info("4️⃣ Attesa 4 sec (anti-detection)")
                await asyncio.sleep(4)

                # Step 5: Loop per ogni evento
                all_tickets = []
                for i, event in enumerate(self.eventi, 1):
                    logger.info(f"5️⃣.{i} Evento {i}/{len(self.eventi)}: {event['data']} (ID: {event['id']})")

                    # Clicca evento
                    event_url = f"/tickets/all/max-pezzali/482766/{event['id']}"
                    await page.goto(f"{self.base_url}{event_url}", wait_until="load")

                    # Attendi 6 sec
                    logger.info(f"      → Attesa 6 sec (load event)")
                    await asyncio.sleep(6)

                    # Estrai biglietti
                    tickets = await self.extract_tickets(page, event)

                    # Attendi 7 sec
                    logger.info(f"      → Attesa 7 sec (post-extraction)")
                    await asyncio.sleep(7)

                    all_tickets.extend(tickets)

                    if tickets:
                        logger.info(f"      ✓ {len(tickets)} biglietti trovati")
                        for t in tickets:
                            logger.info(f"         - {t['descrizione']}: Qtà {t['quantita']} @ {t['prezzo']}")
                    else:
                        logger.info(f"      ✗ Nessun biglietto con Qtà ≥2")

                # Step 6: Salva risultati
                self.save_results(all_tickets)

                logger.info(f"✅ Monitor completato: {len(all_tickets)} biglietti trovati")
                return all_tickets

            except Exception as e:
                logger.error(f"❌ Errore: {e}", exc_info=True)
                return []

            finally:
                await browser.close()

    async def extract_tickets(self, page, event: Dict) -> List[Dict]:
        """Estrae biglietti da una data evento"""
        tickets = []

        try:
            # Trova tutti i biglietti elencati
            ticket_buttons = await page.query_selector_all(
                "button:has-text('Ingresso')"
            )

            for btn in ticket_buttons:
                try:
                    # Estrai testo
                    text = await btn.text_content()

                    # Parsing: "Ingresso X | Fila Y | Posto Z | Blocco B"
                    lines = text.strip().split("\n")

                    # Cerca "Quantità" nella pagina vicino al bottone
                    # La struttura è: "Quantità N" seguito dal bottone

                    # Fai un doppio-check cercando l'elemento Quantità associato
                    parent = await btn.query_selector("..")
                    if parent:
                        parent_text = await parent.text_content() or ""

                        # Estrai quantità
                        qtà = self.extract_quantity(parent_text)

                        # Estrai prezzo
                        prezzo = self.extract_price(parent_text)

                        # Filtra: SOLO Quantità ≥2 e NO Parterre/Posto Unico
                        if qtà >= 2 and not self.is_excluded(lines):
                            tickets.append({
                                "data": event["data"],
                                "descrizione": " | ".join(lines[:3]),  # "Ingresso X | Fila Y | Posto Z"
                                "blocco": self.extract_blocco(lines),
                                "quantita": qtà,
                                "prezzo": prezzo,
                                "timestamp": datetime.now().isoformat(),
                                "evento_id": event["id"]
                            })

                except Exception as e:
                    logger.warning(f"      ⚠ Errore parsing biglietto: {e}")
                    continue

        except Exception as e:
            logger.warning(f"      ⚠ Errore durante estrazione: {e}")

        return tickets

    def extract_quantity(self, text: str) -> int:
        """Estrae quantità dal testo"""
        try:
            if "Quantità" in text:
                parts = text.split("Quantità")
                if len(parts) > 1:
                    # Prendi il numero dopo "Quantità"
                    num_str = ''.join(c for c in parts[1][:5] if c.isdigit())
                    return int(num_str) if num_str else 1
        except:
            pass
        return 1

    def extract_price(self, text: str) -> str:
        """Estrae prezzo dal testo"""
        try:
            if "€" in text:
                parts = text.split("€")
                if len(parts) > 1:
                    price_str = parts[1].strip().split()[0]
                    return f"€ {price_str}"
        except:
            pass
        return "N/A"

    def extract_blocco(self, lines: List[str]) -> str:
        """Estrae blocco dai dettagli"""
        for line in lines:
            if "Blocco" in line:
                return line.split("Blocco")[-1].strip()
        return "N/A"

    def is_excluded(self, lines: List[str]) -> bool:
        """Controlla se il biglietto deve essere escluso"""
        text = " ".join(lines).upper()

        # Escludi Parterre e Posto Unico
        if "PARTERRE" in text or "POSTO UNICO" in text:
            return True

        return False

    def save_results(self, tickets: List[Dict]):
        """Salva risultati in JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"monitor_{timestamp}.json"

        # Raggruppa per BLOCCO (ALERT SPECIALE per BLOCCO B)
        blocchi = {}
        for t in tickets:
            blocco = t["blocco"]
            if blocco not in blocchi:
                blocchi[blocco] = []
            blocchi[blocco].append(t)

        output_data = {
            "timestamp": datetime.now().isoformat(),
            "totale_biglietti": len(tickets),
            "biglietti_per_blocco": blocchi,
            "biglietti": tickets,
            "alert_blocco_b": len(blocchi.get("B", [])) > 0
        }

        output_file.write_text(json.dumps(output_data, indent=2, ensure_ascii=False))
        logger.info(f"💾 Salvato: {output_file}")

        # Alert speciale per BLOCCO B
        if output_data["alert_blocco_b"]:
            logger.critical(f"🔴 ALERT SPECIALE: {len(blocchi['B'])} biglietti BLOCCO B trovati!")


async def main():
    monitor = FanSaleMonitor()
    await monitor.run()


if __name__ == "__main__":
    asyncio.run(main())
