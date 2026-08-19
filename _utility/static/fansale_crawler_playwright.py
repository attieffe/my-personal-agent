#!/usr/bin/env python3
"""
FanSale Max Pezzali Biglietti Crawler
Usa Playwright con stealth mode per evitare Cloudflare
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    logger.error("Mancano dipendenze. Installa con: pip install playwright")
    exit(1)


class FanSaleCrawler:
    def __init__(self):
        self.base_url = "https://www.fansale.it"
        self.event_url = "https://www.fansale.it/tickets/all/max-pezzali/482766"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "url": self.event_url,
            "evento": "Max Pezzali Milano",
            "biglietti_biglietti": [],
            "biglietti_pacchetti": [],
            "esploration_notes": []
        }

    async def run(self):
        """Esecuzione principale"""
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
            page = await context.new_page()

            try:
                logger.info(f"Navigazione a: {self.event_url}")
                try:
                    await page.goto(self.event_url, wait_until="load", timeout=15000)
                except:
                    logger.warning("Timeout su networkidle, provo con il contenuto caricato")
                    pass

                logger.info("Pagina caricata, inizio esplorazione...")
                await self.explore_page(page)

                # Salva risultati
                await self.save_results()

            except Exception as e:
                logger.error(f"Errore durante crawling: {e}")
                self.results["esploration_notes"].append(f"ERRORE: {str(e)}")
                await self.save_results()

            finally:
                await browser.close()

    async def explore_page(self, page):
        """Esplora la struttura della pagina"""

        # Aspetta stabilizzazione pagina
        await asyncio.sleep(3)
        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
        except:
            logger.warning("Timeout su networkidle, continuo comunque")
        await asyncio.sleep(2)

        # Prendi il contenuto della pagina
        try:
            page_html = await page.content()
        except:
            logger.warning("Errore content, riprovo...")
            await asyncio.sleep(2)
            page_html = await page.content()

        # Controlla se accesso negato
        if "Access Denied" in page_html:
            self.results["esploration_notes"].append("Pagina bloccata da Cloudflare (Access Denied)")
            logger.warning("Access Denied rilevato")
            return

        logger.info("Ricerca sezioni BIGLIETTI e PACCHETTI...")

        # Prova a trovare i sectionheader che dividono BIGLIETTI da PACCHETTI
        try:
            # Cerca elementi header/section che contengono "BIGLIETTI" o "PACCHETTI"
            section_headers = await page.query_selector_all("*:has-text('BIGLIETTI'), *:has-text('PACCHETTI')")
            self.results["esploration_notes"].append(f"Found {len(section_headers)} section headers")

            for i, header in enumerate(section_headers[:5]):
                text = await header.text_content()
                self.results["esploration_notes"].append(f"  Header {i}: {text[:80]}")

        except Exception as e:
            self.results["esploration_notes"].append(f"Errore ricerca headers: {e}")

        # Cerchiamo elementi che potenzialmente sono biglietti
        logger.info("Ricerca elementi biglietti...")
        try:
            # Prova diverse strategie di selezione
            selectors = [
                "div[class*='ticket']",
                "div[class*='card']",
                "li[class*='ticket']",
                "article",
                "button:has-text('VISUALIZZA')"
            ]

            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if len(elements) > 0:
                        self.results["esploration_notes"].append(f"Selector '{selector}': {len(elements)} elementi")

                        # Preview primo elemento
                        if len(elements) > 0:
                            preview = await elements[0].text_content()
                            self.results["esploration_notes"].append(f"  Preview: {preview[:150]}")

                except Exception as e:
                    self.results["esploration_notes"].append(f"  Selector '{selector}' errore: {e}")

        except Exception as e:
            self.results["esploration_notes"].append(f"Errore ricerca biglietti: {e}")

        # Prova a fare screenshot della pagina per debug
        try:
            screenshot_path = "/tmp/fansale_page.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            self.results["esploration_notes"].append(f"Screenshot salvato: {screenshot_path}")
            logger.info(f"Screenshot: {screenshot_path}")
        except Exception as e:
            self.results["esploration_notes"].append(f"Errore screenshot: {e}")

        # Prova uno scroll e aspetta dinamica
        logger.info("Scroll e attesa rendering dinamico...")
        try:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_load_state("networkidle")
            self.results["esploration_notes"].append("Scroll completato")
        except Exception as e:
            self.results["esploration_notes"].append(f"Errore scroll: {e}")

    async def save_results(self):
        """Salva risultati in JSON"""
        output_dir = Path("/home/openclaw/.openclaw/workspace/projects/fansale-biglietti-pezzali/_logs")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"exploration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_file.write_text(json.dumps(self.results, indent=2, ensure_ascii=False))
        logger.info(f"Risultati salvati: {output_file}")

        print("\n" + "="*60)
        print("ESPLORAZIONE COMPLETATA")
        print("="*60)
        print(json.dumps(self.results, indent=2, ensure_ascii=False))


async def main():
    crawler = FanSaleCrawler()
    await crawler.run()


if __name__ == "__main__":
    asyncio.run(main())
