#!/home/openclaw/.local/share/pipx/venvs/patchright/bin/python
"""
Fansale.it scraper usando patchright
Testa multipli URL di eventi e restituisce JSON strutturato
"""

import json
import sys
from datetime import datetime
from patchright.sync_api import sync_playwright

# Selettori
CONTAINER_SELECTOR = '#EventDetailsAndListingCard > div.Card.Card-onEventDetailsPage.Card-isMobileCard.EventDetail-Listing.js-EventDetail-Listing.EventDetail-Listing-seatmapLoaded > div.EventEntryList.js-EventEntryList.EventEntryList-clearFloat.u-flexboxSortingContainer'
OFFER_SELECTOR = CONTAINER_SELECTOR + ' > .EventEntry'

def log(*args):
    """Log con timestamp"""
    print(datetime.now().isoformat(), *args, file=sys.stderr)

def extract_offers(page):
    """Estrae le offerte dalla pagina usando la stessa logica dello script JS"""

    def parse_offers(nodes):
        """Funzione eseguita nel browser context"""
        results = []
        for el in nodes:
            seat_desc = el.get_attribute('data-seatdescriptionforarialabel') or ''

            # Helper per estrarre campi dal seat_desc
            def parse_field(label):
                import re
                match = re.search(rf'{label}\s*([^|]+)', seat_desc, re.IGNORECASE)
                return match.group(1).strip() if match else None

            # Cerca quantità nel DOM
            qty_el = el.query_selector('.NumberOfTicketsInOffer')
            quantita = qty_el.inner_text().strip() if qty_el else el.get_attribute('data-splitting-possibilities')

            results.append({
                'offerId': el.get_attribute('data-offer-id'),
                'quantita': quantita,
                'ingresso': parse_field('Ingresso'),
                'fila': parse_field('Fila'),
                'posto': parse_field('Posto'),
                'blocco': parse_field('Blocco'),
                'tipoOfferta': el.get_attribute('data-offertype'),
                'prezzo': el.get_attribute('data-splitting-possibility-prices'),
                'fairDeal': el.get_attribute('data-fairdeal') == 'true',
                'certified': el.get_attribute('data-certified') == 'true',
            })
        return results

    # Trova tutti gli elementi offerta
    offers_elements = page.query_selector_all(OFFER_SELECTOR)
    offers = []

    for el in offers_elements:
        seat_desc = el.get_attribute('data-seatdescriptionforarialabel') or ''

        # Helper per estrarre campi dal seat_desc
        import re
        def parse_field(label):
            match = re.search(rf'{label}\s*([^|]+)', seat_desc, re.IGNORECASE)
            return match.group(1).strip() if match else None

        # Cerca quantità nel DOM
        qty_el = el.query_selector('.NumberOfTicketsInOffer')
        quantita = qty_el.inner_text().strip() if qty_el else el.get_attribute('data-splitting-possibilities')

        offers.append({
            'offerId': el.get_attribute('data-offer-id'),
            'quantita': quantita,
            'ingresso': parse_field('Ingresso'),
            'fila': parse_field('Fila'),
            'posto': parse_field('Posto'),
            'blocco': parse_field('Blocco'),
            'tipoOfferta': el.get_attribute('data-offertype'),
            'prezzo': el.get_attribute('data-splitting-possibility-prices'),
            'fairDeal': el.get_attribute('data-fairdeal') == 'true',
            'certified': el.get_attribute('data-certified') == 'true',
        })

    return offers

def scrape_event(playwright, url, titolo, data):
    """Scrape singolo evento"""
    result = {
        'url': url,
        'titolo': titolo,
        'data': data,
        'timestamp': datetime.now().isoformat(),
        'success': False,
        'offers': [],
        'error': None
    }

    browser = None
    try:
        log(f'Inizio scraping: {titolo} ({data})')

        # Launch browser (headless=False come script originale, usa chromium disponibile)
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(
            locale='it-IT',
            viewport={'width': 1366, 'height': 900}
        )
        page = context.new_page()

        # Naviga
        log(f'Navigo a {url}')
        page.goto(url, wait_until='domcontentloaded', timeout=60000)

        # Gestisci cookie banner
        cookie_selectors = [
            'button#onetrust-accept-btn-handler',
            'button:has-text("Accetta")',
            'button:has-text("Accetto")',
            'button:has-text("Accept")',
        ]

        for sel in cookie_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=3000):
                    btn.click()
                    log(f'Cliccato banner cookie: {sel}')
                    break
            except:
                pass

        # Attendi un po'
        page.wait_for_timeout(3000)

        # Cerca container
        container_found = False
        try:
            page.wait_for_selector(CONTAINER_SELECTOR, timeout=20000)
            container_found = True
            log('Container trovato')
        except:
            log('Container non trovato entro 20s')

        # Verifica presenza container
        final_container = page.locator(CONTAINER_SELECTOR)
        final_count = final_container.count()
        log(f'Occorrenze container: {final_count}')

        if final_count > 0:
            # Estrai offerte
            offers = extract_offers(page)
            log(f'Offerte estratte: {len(offers)}')
            result['offers'] = offers
            result['success'] = True
        else:
            # Check per Access Denied
            body_text = page.locator('body').inner_text()
            if 'Access Denied' in body_text:
                result['error'] = 'Access Denied - bot detection attivo'
                log('ERRORE: Access Denied')
            else:
                result['error'] = 'Container offerte non trovato'
                log('ERRORE: Container non trovato')

    except Exception as e:
        log(f'ERRORE: {str(e)}')
        result['error'] = str(e)

    finally:
        if browser:
            browser.close()

    return result

def scrape_events(events):
    """
    Scrape multipli eventi

    Args:
        events: lista di dict con {url, titolo, data}

    Returns:
        dict con risultati strutturati
    """
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_events': len(events),
        'successful': 0,
        'failed': 0,
        'events': []
    }

    with sync_playwright() as playwright:
        for event in events:
            result = scrape_event(
                playwright,
                event['url'],
                event['titolo'],
                event['data']
            )

            results['events'].append(result)

            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1

    return results

def main():
    """Entry point"""
    if len(sys.argv) < 2:
        print("Uso: fansale-scraper.py <events_json_file>", file=sys.stderr)
        print("", file=sys.stderr)
        print("Il file JSON deve contenere un array di oggetti:", file=sys.stderr)
        print('[{"url": "...", "titolo": "...", "data": "..."}]', file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]

    # Leggi eventi da file
    with open(input_file, 'r', encoding='utf-8') as f:
        events = json.load(f)

    log(f'Caricati {len(events)} eventi da processare')

    # Scrape
    results = scrape_events(events)

    # Output JSON su stdout
    print(json.dumps(results, indent=2, ensure_ascii=False))

    log(f'Completato: {results["successful"]}/{results["total_events"]} successi')

if __name__ == '__main__':
    main()
