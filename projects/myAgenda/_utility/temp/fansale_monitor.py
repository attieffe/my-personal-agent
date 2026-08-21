#!/usr/bin/env python3
import requests
import json
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

# Eventi Milano da controllare
EVENTS = [
    {
        "date": "22 Dicembre 2026",
        "venue": "Unipol Dome",
        "url": "https://www.fansale.it/tickets/all/max-pezzali/482766/21343215",
        "id": "21343215"
    },
    {
        "date": "22 Dicembre 2026",
        "venue": "Unipol Dome Party Terrace",
        "url": "https://www.fansale.it/tickets/all/max-pezzali/482766/21353575",
        "id": "21353575"
    },
    {
        "date": "23 Dicembre 2026",
        "venue": "Unipol Dome",
        "url": "https://www.fansale.it/tickets/all/max-pezzali/482766/21343717",
        "id": "21343717"
    },
    {
        "date": "26 Dicembre 2026",
        "venue": "Unipol Dome",
        "url": "https://www.fansale.it/tickets/all/max-pezzali/482766/21343715",
        "id": "21343715"
    },
    {
        "date": "27 Dicembre 2026",
        "venue": "Unipol Dome",
        "url": "https://www.fansale.it/tickets/all/max-pezzali/482766/21343722",
        "id": "21343722"
    },
    {
        "date": "29 Dicembre 2026",
        "venue": "Unipol Dome",
        "url": "https://www.fansale.it/tickets/all/max-pezzali/482766/21343718",
        "id": "21343718"
    },
    {
        "date": "30 Dicembre 2026",
        "venue": "Unipol Dome",
        "url": "https://www.fansale.it/tickets/all/max-pezzali/482766/21343719",
        "id": "21343719"
    },
    {
        "date": "3 Gennaio 2027",
        "venue": "Unipol Dome",
        "url": "https://www.fansale.it/tickets/all/max-pezzali/482766/21928067",
        "id": "21928067"
    }
]

MASTER_URL = "https://www.fansale.it/tickets/all/max-pezzali/482766"

def check_event(event):
    """Controlla un singolo evento"""
    result = {
        "event": event,
        "status": "unknown",
        "tickets_found": 0,
        "tickets_qty_2_plus": [],
        "blocco_b_found": False,
        "error": None
    }

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        print(f"Controllo {event['date']} - {event['venue']}...")
        response = requests.get(event['url'], headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Cerca i biglietti nelle offerte
        # Pattern comune: Quantità X, Blocco Y
        ticket_divs = soup.find_all(['div', 'li'], class_=re.compile(r'offer|ticket|item'))

        for div in ticket_divs:
            text = div.get_text()

            # Cerca quantità
            qty_match = re.search(r'Quantità\s*(\d+)', text, re.IGNORECASE)
            if qty_match:
                qty = int(qty_match.group(1))
                result['tickets_found'] += 1

                # Cerca blocco
                blocco_match = re.search(r'Blocco\s+([A-Z]\d+)', text, re.IGNORECASE)
                blocco = blocco_match.group(1) if blocco_match else "N/A"

                # Escludi Parterre e Posto Unico
                if 'parterre' in text.lower() or 'posto unico' in text.lower():
                    continue

                if qty >= 2:
                    ticket_info = {
                        "quantity": qty,
                        "blocco": blocco,
                        "text_snippet": text[:200]
                    }
                    result['tickets_qty_2_plus'].append(ticket_info)

                    # Check BLOCCO B
                    if blocco.upper().startswith('B'):
                        result['blocco_b_found'] = True

        result['status'] = 'success'

    except requests.Timeout:
        result['status'] = 'timeout'
        result['error'] = 'Timeout durante la richiesta'
    except requests.RequestException as e:
        result['status'] = 'error'
        result['error'] = f'Errore HTTP: {str(e)}'
    except Exception as e:
        result['status'] = 'error'
        result['error'] = f'Errore parsing: {str(e)}'

    return result

def main():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    all_results = []

    print(f"Inizio monitoraggio FanSale - {datetime.now()}")
    print(f"Master URL: {MASTER_URL}\n")

    for i, event in enumerate(EVENTS):
        result = check_event(event)
        all_results.append(result)

        # Pausa tra le richieste (tranne l'ultima)
        if i < len(EVENTS) - 1:
            print(f"Pausa 10 secondi...\n")
            time.sleep(10)

    # Salva report JSON
    log_file = f'/home/openclaw/.openclaw/workspace/projects/myAgenda/_logs/monitor_{timestamp}.json'
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'master_url': MASTER_URL,
            'events_checked': len(EVENTS),
            'results': all_results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Report salvato in {log_file}")

    # Genera report per Telegram
    print("\n" + "="*60)
    print("REPORT TELEGRAM")
    print("="*60 + "\n")

    print(f"📌 [Max Pezzali]({MASTER_URL}) — link principale al master\n")

    total_tested = 0
    total_failed = 0
    total_tickets_found = 0
    blocco_b_events = 0

    for res in all_results:
        ev = res['event']
        status_line = f"• [{ev['date']} {ev['venue']}]({ev['url']})"

        if res['status'] == 'success':
            total_tested += 1
            if res['tickets_qty_2_plus']:
                total_tickets_found += len(res['tickets_qty_2_plus'])
                status_line += f" — trovati {len(res['tickets_qty_2_plus'])} biglietti (Qtà≥2)"
            else:
                status_line += " — nessun biglietto con Qtà≥2"

            if res['blocco_b_found']:
                status_line += " ⚠️ **BLOCCO B TROVATO**"
                blocco_b_events += 1
            else:
                status_line += " [BLOCCO B: NO]"
        elif res['status'] == 'timeout':
            total_failed += 1
            status_line += f" — visita fallita (timeout)"
        else:
            total_failed += 1
            status_line += f" — visita fallita ({res['error']})"

        print(status_line)

    print(f"\n📊 **RIEPILOGO FINALE:**")
    print(f"- Eventi totali trovati: {len(EVENTS)}")
    print(f"- Eventi testati: {total_tested}")
    print(f"- Eventi con blocco antispam/errori: {total_failed}")
    print(f"- Biglietti trovati (Qtà≥2): {total_tickets_found}")
    print(f"- BLOCCO B trovato: {'SÌ' if blocco_b_events > 0 else 'NO'}")

if __name__ == '__main__':
    main()
