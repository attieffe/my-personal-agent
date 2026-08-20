#!/usr/bin/env python3
"""
FanSale Max Pezzali Fast Scan - Requests + BeautifulSoup
Scansione veloce 7 date Milano, estrazione BLOCCO B con Quantità ≥2
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    logger.error("Manca requests/bs4. Installa con: pip install --break-system-packages requests beautifulsoup4")
    exit(1)

class FanSaleFastScan:
    def __init__(self):
        self.base_url = "https://www.fansale.it"
        self.config_dir = Path(__file__).parent
        self.eventi_file = self.config_dir / "eventi_list.json"
        self.output_dir = self.config_dir.parent / "_logs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        })

        self.eventi = []
        self.load_eventi()

    def load_eventi(self):
        if self.eventi_file.exists():
            with open(self.eventi_file) as f:
                data = json.load(f)
                self.eventi = data.get("eventi", [])
                logger.info(f"✅ Caricati {len(self.eventi)} eventi")

    def run(self):
        logger.info("🚀 Avvio Fast Scan FanSale")
        all_tickets = []

        for i, event in enumerate(self.eventi, 1):
            event_url = f"{self.base_url}/tickets/all/max-pezzali/482766/{event['id']}"
            logger.info(f"\n{i}/7 Scanning: {event['data']} (ID {event['id']})")
            logger.info(f"   URL: {event_url}")

            try:
                tickets = self.extract_event(event_url, event)
                all_tickets.extend(tickets)

                if tickets:
                    logger.info(f"   ✓ {len(tickets)} biglietti trovati")
                    for t in tickets:
                        logger.info(f"     - {t['descrizione']}: Qtà {t['quantita']} @ {t['prezzo']}")
                else:
                    logger.info(f"   ✗ Nessun biglietto ≥2")

            except Exception as e:
                logger.warning(f"   ⚠ Errore: {e}")

        self.save_results(all_tickets)
        logger.info(f"\n✅ Scan completato: {len(all_tickets)} biglietti totali")
        return all_tickets

    def extract_event(self, url: str, event: Dict) -> List[Dict]:
        tickets = []
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.content, 'html.parser')

            # Trova tutti i biglietti: estructura "Quantità X ... Blocco B ... € 72,24"
            # Ricerca buttons che contengono descrizione biglietto
            ticket_divs = soup.find_all('div', class_=lambda x: x and 'offer' in x.lower())

            if not ticket_divs:
                # Alternativa: cerca tutti i div che contengono "Quantità" e "Blocco"
                ticket_divs = soup.find_all('div', string=lambda x: x and 'Quantità' in x if x else False)

            # Parsing semplificato: cerca pattern nel testo della pagina
            page_text = soup.get_text()

            # Split per linee
            lines = page_text.split('\n')

            for i, line in enumerate(lines):
                if 'Quantità' in line and i + 10 < len(lines):
                    # Estrai quantità
                    try:
                        qtà_str = ''.join(c for c in line.split('Quantità')[1][:5] if c.isdigit())
                        qtà = int(qtà_str) if qtà_str else 1
                    except:
                        qtà = 1

                    # Guarda le prossime righe per blocco e prezzo
                    next_text = '\n'.join(lines[i:min(i+10, len(lines))])

                    # Estrai blocco
                    blocco = "N/A"
                    if "Blocco" in next_text:
                        try:
                            blocco = next_text.split("Blocco")[1].split('\n')[0].strip()[:3]
                        except:
                            blocco = "N/A"

                    # Estrai prezzo
                    prezzo = "N/A"
                    if "€" in next_text:
                        try:
                            prezzo = "€ " + next_text.split("€")[1].split()[0]
                        except:
                            pass

                    # Filtra: SOLO Blocco B e Quantità ≥2
                    if blocco.startswith('B') and qtà >= 2:
                        tickets.append({
                            "data": event["data"],
                            "descrizione": f"Blocco {blocco}",
                            "blocco": blocco,
                            "quantita": qtà,
                            "prezzo": prezzo,
                            "timestamp": datetime.now().isoformat(),
                            "evento_id": event["id"]
                        })

        except Exception as e:
            logger.warning(f"Errore estrazione: {e}")

        return tickets

    def save_results(self, tickets: List[Dict]):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"monitor_{timestamp}.json"

        # Raggruppa per blocco
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
        logger.info(f"\n💾 Salvato: {output_file}")

        # Alert speciale
        if output_data["alert_blocco_b"]:
            logger.critical(f"🔴 ALERT SPECIALE: {len(blocchi['B'])} biglietti BLOCCO B trovati!")

async def main():
    scan = FanSaleFastScan()
    scan.run()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
