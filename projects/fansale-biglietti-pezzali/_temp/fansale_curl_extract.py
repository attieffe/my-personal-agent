#!/usr/bin/env python3
"""
FanSale Extraction via Curl + BeautifulSoup
Scarica HTML con curl e estrae biglietti
"""

import json
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from bs4 import BeautifulSoup
except ImportError:
    logger.error("Manca beautifulsoup4. Installa con: pip install beautifulsoup4")
    exit(1)


def fetch_url(url: str, delay: float = 1.0) -> str:
    """Scarica URL con curl e ritorna HTML"""
    logger.info(f"   Fetching: {url}")

    try:
        # User-Agent per evitare blocchi
        cmd = [
            "curl",
            "-s",
            "-L",
            "--max-time", "30",
            "-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "-H", "Accept-Language: it-IT,it;q=0.9",
            url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            time.sleep(delay)  # Anti-detection delay
            return result.stdout
        else:
            logger.warning(f"   Curl error: {result.stderr[:100]}")
            return ""

    except Exception as e:
        logger.error(f"   Exception: {e}")
        return ""


def extract_tickets_from_html(html: str, event_date: str) -> List[Dict]:
    """Estrae biglietti dall'HTML"""
    tickets = []

    if not html:
        return tickets

    try:
        soup = BeautifulSoup(html, "html.parser")

        # Cerca tutte le righe di biglietti (possibili selettori)
        ticket_divs = soup.find_all("div", class_=lambda x: x and "ticket" in x.lower())
        ticket_rows = soup.find_all("tr", class_=lambda x: x and ("ticket" in x.lower() or "row" in x.lower()))

        all_elements = ticket_divs + ticket_rows
        logger.info(f"   Trovate {len(all_elements)} righe potenziali")

        for elem in all_elements:
            try:
                text = elem.get_text()

                if "Quantità" not in text:
                    continue

                # Parsing semplice della quantità
                qty = 1
                if "Quantità" in text:
                    parts = text.split("Quantità")
                    if len(parts) > 1:
                        # Estrai numero dopo "Quantità"
                        rest = parts[1][:20]
                        num_str = ''.join(c for c in rest if c.isdigit())
                        if num_str:
                            qty = int(num_str)

                # Filtra
                text_upper = text.upper()
                if qty >= 2 and "PARTERRE" not in text_upper and "POSTO UNICO" not in text_upper:

                    # Estrai prezzo
                    price = "N/A"
                    if "€" in text:
                        parts = text.split("€")
                        if len(parts) > 1:
                            price_part = parts[1].strip().split()[0]
                            price = f"€ {price_part}"

                    # Estrai blocco
                    blocco = "N/A"
                    if "Blocco" in text:
                        blocco_part = text.split("Blocco")[-1].split()[0] if "Blocco" in text else "N/A"
                        blocco = blocco_part

                    tickets.append({
                        "data": event_date,
                        "descrizione": text[:100],
                        "quantita": qty,
                        "prezzo": price,
                        "blocco": blocco,
                        "timestamp": datetime.now().isoformat()
                    })

            except Exception as e:
                logger.debug(f"   Parse error: {e}")
                continue

        return tickets

    except Exception as e:
        logger.warning(f"   HTML parse error: {e}")
        return tickets


def main():
    config_dir = Path(__file__).parent.parent / "_system"
    eventi_file = config_dir / "eventi_list.json"
    output_dir = config_dir.parent / "_logs"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Carica eventi
    with open(eventi_file) as f:
        data = json.load(f)
        eventi = data.get("eventi", [])

    logger.info(f"🚀 Estrazione via Curl: {len(eventi)} eventi")

    all_tickets = {}

    # Per ogni evento
    for i, event in enumerate(eventi, 1):
        logger.info(f"\n{i}. Evento {event['data']} (ID: {event['id']})")

        # Costruisci URL evento
        event_url = f"https://www.fansale.it/tickets/all/max-pezzali/482766/{event['id']}"

        # Scarica HTML
        html = fetch_url(event_url, delay=2.0)

        # Estrai biglietti
        tickets = extract_tickets_from_html(html, event['data'])
        all_tickets[event['data']] = {
            "evento_id": event['id'],
            "biglietti_count": len(tickets),
            "biglietti": tickets
        }

        logger.info(f"   ✓ {len(tickets)} biglietti estratti")

    # Salva risultati
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"monitor_{timestamp}_curl.json"

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


if __name__ == "__main__":
    main()
