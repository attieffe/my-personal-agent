#!/usr/bin/env python3
"""
FanSale Quick Scan - Estrae biglietti via API/Network
Alternativa al browser Playwright che ha problemi HTTP/2
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


class FanSaleQuickScan:
    def __init__(self):
        self.base_url = "https://www.fansale.it"

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
        """Esecuzione: scan veloce manuale"""
        logger.info("🚀 FanSale Quick Scan - Manual Collection Mode")

        import httpx

        async with httpx.AsyncClient(
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            },
            timeout=15.0
        ) as client:
            all_tickets = []

            for i, event in enumerate(self.eventi, 1):
                event_id = event["id"]
                event_date = event["data"]
                logger.info(f"{i}/7: Scansione evento {event_date} (ID: {event_id})")

                try:
                    # Naviga alla pagina dell'evento
                    event_url = f"{self.base_url}/tickets/all/max-pezzali/482766/{event_id}"

                    response = await client.get(event_url, follow_redirects=True)

                    if response.status_code == 200:
                        html = response.text

                        # Parsing semplice HTML per estrarre i biglietti
                        tickets = self.parse_tickets_from_html(html, event)
                        all_tickets.extend(tickets)

                        logger.info(f"   ✓ {len(tickets)} biglietti trovati")
                        for t in tickets:
                            logger.info(f"      - {t['blocco']} | Qtà {t['quantita']} | {t['prezzo']}")

                        # Delay anti-detection: 7 sec tra eventi
                        if i < len(self.eventi):
                            await asyncio.sleep(7)

                    else:
                        logger.warning(f"   ✗ Status {response.status_code}")

                except Exception as e:
                    logger.error(f"   ❌ Errore: {e}")

            # Salva risultati
            self.save_results(all_tickets)
            logger.info(f"✅ Scan completato: {len(all_tickets)} biglietti totali")

            return all_tickets

    def parse_tickets_from_html(self, html: str, event: Dict) -> List[Dict]:
        """Parsing HTML per estrarre biglietti"""
        tickets = []

        try:
            import re

            # Regex per trovare biglietti con formato: "Quantità X" seguito dalla descrizione
            # Pattern: "Quantità (\d+)" -> "Ingresso ... Blocco ..." -> "€ X,XX"

            # Cerco pattern: <generic>Quantità<br>(\d+)</...> seguito da descrizione <generic>...Blocco...
            # Poi € prezzo

            pattern = r'Quantità\s+(\d+).*?Ingresso\s+(\d+).*?\|\s*Fila\s+(\d+).*?\|\s*Posto\s+(\d+).*?\|\s*Blocco\s+(\w+).*?€\s+([\d,]+)'

            matches = re.findall(pattern, html, re.DOTALL)

            for match in matches:
                qtà = int(match[0])
                ingresso = match[1]
                fila = match[2]
                posto = match[3]
                blocco = match[4]
                prezzo = match[5].replace(',', '.')

                # Filtra: SOLO Quantità ≥2, NO Parterre/Posto Unico
                if qtà >= 2 and blocco.upper() not in ["PARTERRE", "UNICO"]:
                    tickets.append({
                        "data": event["data"],
                        "evento_id": event["id"],
                        "descrizione": f"Ingresso {ingresso} | Fila {fila} | Posto {posto}",
                        "blocco": blocco,
                        "quantita": qtà,
                        "prezzo": f"€ {prezzo}",
                        "timestamp": datetime.now().isoformat()
                    })

        except Exception as e:
            logger.warning(f"   ⚠ Errore parsing HTML: {e}")

        return tickets

    def save_results(self, tickets: List[Dict]):
        """Salva risultati in JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"monitor_{timestamp}.json"

        # Raggruppa per BLOCCO
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
            "alert_blocco_b": "B" in blocchi
        }

        output_file.write_text(json.dumps(output_data, indent=2, ensure_ascii=False))
        logger.info(f"💾 Salvato: {output_file}")

        # Alert speciale per BLOCCO B
        if output_data["alert_blocco_b"]:
            logger.critical(f"🔴 ALERT SPECIALE: {len(blocchi['B'])} biglietti BLOCCO B trovati!")


async def main():
    scan = FanSaleQuickScan()
    await scan.run()


if __name__ == "__main__":
    asyncio.run(main())
