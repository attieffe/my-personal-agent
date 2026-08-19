#!/usr/bin/env python3
"""
FanSale Biglietti Max Pezzali Explorer
Bypassa Cloudflare e mappa la struttura del sito
"""

import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import undetected_chromedriver as uc
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
except ImportError:
    logger.error("Mancano dipendenze. Installa con: pip install undetected-chromedriver selenium")
    sys.exit(1)


class FanSaleExplorer:
    def __init__(self, headless=True):
        self.base_url = "https://www.fansale.it"
        self.event_url = "https://www.fansale.it/tickets/all/max-pezzali/482766"
        self.headless = headless
        self.driver = None
        self.wait_timeout = 10

    def setup_driver(self):
        """Configura Chromium con undetected-chromedriver"""
        logger.info("Setup driver con undetected-chromedriver...")
        options = uc.ChromeOptions()

        if self.headless:
            options.add_argument("--headless=new")

        # Header e opzioni per evitare rilevamento bot
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--start-maximized")
        options.add_argument(
            "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        try:
            self.driver = uc.Chrome(options=options, version_main=None)
            logger.info("Driver setup completato")
            return True
        except Exception as e:
            logger.error(f"Errore setup driver: {e}")
            return False

    def get_page(self, url):
        """Carica una pagina e aspetta il caricamento"""
        logger.info(f"Caricamento: {url}")
        try:
            self.driver.get(url)
            time.sleep(3)  # Aspetta render JS

            # Controlla se c'è Access Denied
            page_text = self.driver.page_source
            if "Access Denied" in page_text:
                logger.warning("Pagina bloccata (Access Denied)")
                return False

            logger.info("Pagina caricata correttamente")
            return True
        except Exception as e:
            logger.error(f"Errore caricamento: {e}")
            return False

    def explore_event_page(self):
        """Esplora la pagina evento e mappa i biglietti disponibili"""
        if not self.get_page(self.event_url):
            return None

        logger.info("Esplorazione pagina evento...")

        try:
            # Aspetta il caricamento della lista biglietti
            WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid*='ticket']"))
            )

            # Prende HTML per analisi
            page_html = self.driver.page_source

            # Cerca le sezioni principali
            result = {
                "timestamp": datetime.now().isoformat(),
                "url": self.driver.current_url,
                "page_title": self.driver.title,
                "sections_found": [],
                "tickets_preview": []
            }

            # Prova a trovare sezioni biglietti
            logger.info("Ricerca sezioni biglietti...")

            # Cerca elementi che contengono "BIGLIETTI" / "PACCHETTI"
            sections_text = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'BIGLIETTI') or contains(text(), 'PACCHETTI')]")
            result["sections_found"] = [s.text for s in sections_text[:5]]

            # Cerca eventuali div/card di biglietti
            ticket_cards = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'ticket') or contains(@class, 'card')]")
            logger.info(f"Trovate {len(ticket_cards)} card potenziali")

            # Prende info base dalle prime 3
            for i, card in enumerate(ticket_cards[:3]):
                try:
                    text = card.text
                    if text.strip():
                        result["tickets_preview"].append({
                            "index": i,
                            "preview_text": text[:200]
                        })
                except:
                    pass

            logger.info(f"Risultati esplorazione: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result

        except Exception as e:
            logger.error(f"Errore esplorazione: {e}")
            return None

    def close(self):
        """Chiude il driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Driver chiuso")


def main():
    explorer = FanSaleExplorer(headless=False)  # headless=False per debug visivo

    try:
        if not explorer.setup_driver():
            sys.exit(1)

        result = explorer.explore_event_page()

        if result:
            print("\n" + "="*60)
            print("ESPLORAZIONE COMPLETATA")
            print("="*60)
            print(json.dumps(result, indent=2, ensure_ascii=False))

            # Salva risultati
            output_file = Path("/tmp/fansale_exploration.json")
            output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))
            logger.info(f"Risultati salvati in {output_file}")
        else:
            logger.error("Esplorazione fallita")
            sys.exit(1)

    finally:
        explorer.close()


if __name__ == "__main__":
    main()
