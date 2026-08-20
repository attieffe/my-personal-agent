#!/usr/bin/env python3
"""
FanSale Max Pezzali Monitor - Automated Check
Controlla ogni 30 minuti le 7 date Milano per biglietti Quantità ≥2 in posti numerati
Alert speciale per BLOCCO B
"""

import asyncio
import json
import logging
import subprocess
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
    from playwright_stealth import Stealth
except ImportError:
    logger.error("Manca playwright o playwright-stealth. Installa con: pip install playwright playwright-stealth")
    exit(1)


class FanSaleMonitor:
    def __init__(self):
        self.config_path = Path(__file__).parent / "config.json"
        self.config = self.load_config()

        self.base_url = "https://www.fansale.it/tickets/all/max-pezzali/482766"
        self.output_dir = Path(__file__).parent.parent / "_logs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # File per salvare lista eventi aggiornata
        self.eventi_list_path = Path(__file__).parent / "eventi_list.json"

        # Carica lista eventi (verrà aggiornata dinamicamente)
        self.eventi = self.load_eventi_list()

    def load_config(self):
        """Carica configurazione"""
        if not self.config_path.exists():
            logger.error(f"Config non trovato: {self.config_path}")
            return {}
        return json.loads(self.config_path.read_text())

    def load_eventi_list(self):
        """Carica lista eventi (da file o default iniziale)"""
        if self.eventi_list_path.exists():
            try:
                data = json.loads(self.eventi_list_path.read_text())
                return data.get("eventi", self.get_default_eventi())
            except Exception as e:
                logger.warning(f"Errore caricamento eventi list: {e}, uso default")

        # Lista default iniziale
        return self.get_default_eventi()

    def get_default_eventi(self):
        """Lista eventi default"""
        return [
            {"id": "21343215", "data": "2026-12-22", "giorno": "Martedì"},
            {"id": "21343717", "data": "2026-12-23", "giorno": "Mercoledì"},
            {"id": "21343715", "data": "2026-12-26", "giorno": "Sabato"},
            {"id": "21343722", "data": "2026-12-27", "giorno": "Domenica"},
            {"id": "21343718", "data": "2026-12-29", "giorno": "Martedì"},
            {"id": "21343719", "data": "2026-12-30", "giorno": "Mercoledì"},
            {"id": "21928067", "data": "2027-01-03", "giorno": "Domenica"},
        ]

    def save_eventi_list(self, eventi: List[Dict], last_update: str):
        """Salva lista eventi aggiornata"""
        data = {
            "last_update": last_update,
            "eventi": eventi
        }
        self.eventi_list_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        logger.info(f"Lista eventi salvata: {len(eventi)} eventi")

    def get_last_update_timestamp(self):
        """Ottiene timestamp ultimo aggiornamento lista"""
        if self.eventi_list_path.exists():
            try:
                data = json.loads(self.eventi_list_path.read_text())
                return data.get("last_update", "Mai aggiornato")
            except:
                pass
        return "Mai aggiornato"

    async def check_all_dates(self):
        """Controlla tutte le date"""
        logger.info("=== Inizio check di tutte le date ===")

        risultati = []
        lista_aggiornata = False

        async with Stealth().use_async(async_playwright()) as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                ]
            )

            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale="it-IT",
                timezone_id="Europe/Rome"
            )

            try:
                page = await context.new_page()

                # STEP 0: Carica home e accetta cookie (bypass anti-bot)
                logger.info("Step 0: Caricamento home + accettazione cookie...")
                await self.load_home_and_accept_cookies(page)

                # STEP 1: Aggiorna lista eventi dalla pagina principale
                logger.info("Step 1: Controllo pagina principale per nuovi eventi...")
                lista_aggiornata = await self.update_eventi_list_from_main_page(page)

                # STEP 2: Controlla tutti gli eventi nella lista
                logger.info(f"Step 2: Scansione {len(self.eventi)} eventi...")
                for evento in self.eventi:
                    logger.info(f"Controllo {evento['giorno']} {evento['data']}...")
                    biglietti = await self.check_evento(page, evento)

                    if biglietti:
                        risultati.extend(biglietti)

                    # Breve pausa tra una data e l'altra
                    await asyncio.sleep(2)

            finally:
                await browser.close()

        # Salva risultati
        self.save_results(risultati)

        # Invia notifiche Telegram
        self.send_telegram_notification(risultati, lista_aggiornata)

        return risultati

    async def load_home_and_accept_cookies(self, page):
        """Carica home page e accetta cookie (bypass anti-bot)"""
        try:
            # Naviga alla home
            home_url = "https://www.fansale.it/"
            await page.goto(home_url, wait_until="load", timeout=15000)
            await asyncio.sleep(3)

            # Cerca e clicca button "Accept All Cookies"
            try:
                cookie_button = await page.wait_for_selector(
                    "button:has-text('Accept All Cookies')",
                    timeout=5000
                )
                if cookie_button:
                    await cookie_button.click()
                    await asyncio.sleep(2)
                    logger.info("✅ Cookie accettati")
            except:
                logger.info("ℹ️ Cookie banner non trovato (già accettati?)")

        except Exception as e:
            logger.warning(f"⚠️ Errore caricamento home: {e}")

    async def update_eventi_list_from_main_page(self, page) -> bool:
        """
        Controlla la pagina principale per nuovi eventi MILANO
        Returns: True se aggiornamento riuscito, False altrimenti
        """
        try:
            # Naviga alla pagina principale (già autenticati con cookie)
            await page.goto(self.base_url, wait_until="load", timeout=15000)
            await asyncio.sleep(2)

            # Scroll per sembrare umano
            await page.evaluate("window.scrollTo(0, 300)")
            await asyncio.sleep(1)

            # Cerca tutti i link "Visualizza" per eventi MILANO (no pacchetti)
            nuovi_eventi = []

            # Trova tutti i link nella sezione BIGLIETTI
            # Cerco elementi che contengono "MILANO" e hanno pulsante "Visualizza"
            links = await page.query_selector_all('main a[href*="/tickets/all/max-pezzali/482766/"]')

            for link in links:
                try:
                    # Estrai href
                    href = await link.get_attribute("href")
                    if not href or href == "/tickets/all/max-pezzali/482766":
                        continue

                    # Estrai event_id dall'URL
                    event_id = href.split("/")[-1]

                    # Leggi il testo del link per capire se è MILANO e non pacchetto
                    text = await link.text_content()
                    if not text:
                        continue

                    # Filtri: deve contenere MILANO e NON deve contenere "Pacchetto"
                    if "MILANO" not in text or "Pacchetto" in text:
                        continue

                    # Estrai data e giorno
                    # Formato tipico: "martedì 22. dic 2026 Max Pezzali MILANO..."
                    lines = [l.strip() for l in text.split("\n") if l.strip()]

                    data_raw = ""
                    giorno = ""

                    for line in lines:
                        # Cerca linea con data
                        if any(mese in line.lower() for mese in ["dic", "gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov"]):
                            data_raw = line
                            # Estrai giorno della settimana
                            if "martedì" in line.lower():
                                giorno = "Martedì"
                            elif "mercoledì" in line.lower():
                                giorno = "Mercoledì"
                            elif "giovedì" in line.lower():
                                giorno = "Giovedì"
                            elif "venerdì" in line.lower():
                                giorno = "Venerdì"
                            elif "sabato" in line.lower():
                                giorno = "Sabato"
                            elif "domenica" in line.lower():
                                giorno = "Domenica"
                            elif "lunedì" in line.lower():
                                giorno = "Lunedì"
                            break

                    # Parse data (formato approssimato, migliora se necessario)
                    data_iso = self.parse_data_italiana(data_raw)

                    if event_id and data_iso and giorno:
                        nuovi_eventi.append({
                            "id": event_id,
                            "data": data_iso,
                            "giorno": giorno
                        })

                except Exception as e:
                    logger.warning(f"Errore parsing link evento: {e}")
                    continue

            # Rimuovi duplicati (stesso ID)
            eventi_unici = []
            ids_visti = set()
            for ev in nuovi_eventi:
                if ev["id"] not in ids_visti:
                    eventi_unici.append(ev)
                    ids_visti.add(ev["id"])

            # Controlla se ci sono eventi nuovi rispetto alla lista corrente
            ids_correnti = {e["id"] for e in self.eventi}
            ids_nuovi = {e["id"] for e in eventi_unici}

            # Se non troviamo eventi, probabilmente il parsing è fallito - non aggiornare
            if not ids_nuovi:
                logger.warning("⚠️ Nessun evento trovato nel parsing - probabile errore, uso lista esistente")
                return False

            if ids_nuovi != ids_correnti:
                logger.info(f"⚠️ Lista eventi aggiornata: {len(eventi_unici)} eventi totali")
                logger.info(f"   Nuovi ID: {ids_nuovi - ids_correnti}")
                logger.info(f"   Rimossi ID: {ids_correnti - ids_nuovi}")

                # Aggiorna lista
                self.eventi = eventi_unici
                self.save_eventi_list(eventi_unici, datetime.now().isoformat())
                return True
            else:
                logger.info(f"✅ Lista eventi invariata: {len(self.eventi)} eventi")
                return False

        except Exception as e:
            logger.error(f"❌ Errore aggiornamento lista eventi: {e}")
            logger.info("   → Uso lista esistente")
            return False

    def parse_data_italiana(self, data_raw: str) -> str:
        """
        Parse data italiana in formato ISO
        Input: "martedì 22. dic 2026" o simile
        Output: "2026-12-22"
        """
        try:
            # Mappa mesi italiani
            mesi = {
                "gen": "01", "feb": "02", "mar": "03", "apr": "04",
                "mag": "05", "giu": "06", "lug": "07", "ago": "08",
                "set": "09", "ott": "10", "nov": "11", "dic": "12"
            }

            # Estrai giorno, mese, anno
            import re
            match = re.search(r"(\d+)\.\s*(\w+)\s*(\d{4})", data_raw)
            if match:
                giorno = match.group(1).zfill(2)
                mese_ita = match.group(2).lower()
                anno = match.group(3)

                mese = mesi.get(mese_ita, "01")

                return f"{anno}-{mese}-{giorno}"

        except Exception as e:
            logger.warning(f"Errore parse data '{data_raw}': {e}")

        return ""

    async def check_evento(self, page, evento: Dict) -> List[Dict]:
        """Controlla singolo evento"""
        url = f"{self.base_url}/{evento['id']}"

        try:
            # Naviga con timeout generoso
            await page.goto(url, wait_until="load", timeout=20000)
            await asyncio.sleep(8)  # Delay fisso per rendering JavaScript pesante

            # Scroll per attivare lazy loading
            await page.evaluate("window.scrollTo(0, 600)")
            await asyncio.sleep(1)

            # Estrai biglietti dalla pagina
            biglietti = await self.extract_tickets(page, evento)

            # Filtra: solo Quantità ≥2 e posti numerati
            biglietti_validi = [
                b for b in biglietti
                if b.get("quantita", 0) >= 2
                and b.get("blocco", "").strip() != ""
                and "Posto Unico" not in b.get("posto", "")
                and "Parterre" not in b.get("blocco", "")
            ]

            return biglietti_validi

        except Exception as e:
            logger.error(f"Errore check evento {evento['id']}: {e}")
            return []

    async def extract_tickets(self, page, evento: Dict) -> List[Dict]:
        """Estrae biglietti dalla pagina"""
        biglietti = []

        try:
            # Step 1: Cerca e clicca pulsante "Carica Offerte" se presente
            try:
                carica_btn = await page.query_selector('button')
                buttons = await page.query_selector_all('button')
                for btn in buttons:
                    text = await btn.text_content()
                    if text and "Carica" in text and "Offerte" in text:
                        await btn.click()
                        logger.info("   → Cliccato 'Carica Offerte'")
                        await asyncio.sleep(6)  # Attendi caricamento
                        break
            except Exception as e:
                logger.info(f"   → Carica Offerte: {e}")

            # Step 2: Estrai biglietti con JavaScript (no selectors, più robusto)
            biglietti_raw = await page.evaluate("""
                () => {
                    const biglietti = [];
                    // Trova tutti i container che hanno "Quantità" seguito da un numero
                    const containers = Array.from(document.querySelectorAll('*')).filter(el => {
                        return el.textContent.includes('Quantità') &&
                               el.textContent.includes('Ingresso') &&
                               el.textContent.includes('Blocco');
                    });

                    // Per ogni container, estrai i dati più vicini
                    for (const container of containers) {
                        try {
                            const text = container.textContent;

                            // Estrai quantità (cerca numero dopo "Quantità")
                            const quantitaMatch = text.match(/Quantità\\s*(\\d+)/);
                            if (!quantitaMatch) continue;
                            const quantita = parseInt(quantitaMatch[1]);

                            // Estrai dettagli posto (linea con "Ingresso ... Blocco X")
                            const dettagliMatch = text.match(/(Ingresso\\s+\\d+\\s+\\|[^€]+Blocco\\s+\\w+)/);
                            if (!dettagliMatch) continue;
                            const dettagli = dettagliMatch[1].trim();

                            // Estrai blocco
                            const bloccoMatch = dettagli.match(/Blocco\\s+(\\w+)/);
                            const blocco = bloccoMatch ? bloccoMatch[1] : "";

                            // Estrai prezzo
                            const prezzoMatch = text.match(/€\\s*([\\d,\\.]+)/);
                            const prezzo = prezzoMatch ? `€ ${prezzoMatch[1]}` : "";

                            biglietti.push({
                                quantita: quantita,
                                dettagli: dettagli,
                                blocco: blocco,
                                prezzo: prezzo
                            });
                        } catch (e) {
                            // Ignora errori parsing singolo biglietto
                        }
                    }

                    return biglietti;
                }
            """)

            # Aggiungi metadati evento
            for b in biglietti_raw:
                biglietti.append({
                    "evento_id": evento["id"],
                    "data": evento["data"],
                    "giorno": evento["giorno"],
                    "quantita": b["quantita"],
                    "dettagli": b["dettagli"],
                    "blocco": b["blocco"],
                    "posto": b["dettagli"],
                    "prezzo": b["prezzo"],
                    "url": f"{self.base_url}/{evento['id']}",
                    "timestamp": datetime.now().isoformat()
                })

            logger.info(f"   → Trovati {len(biglietti)} biglietti totali")

        except Exception as e:
            logger.error(f"Errore extract_tickets: {e}")

        return biglietti

    def save_results(self, biglietti: List[Dict]):
        """Salva risultati in JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"monitor_{timestamp}.json"

        output_data = {
            "timestamp": datetime.now().isoformat(),
            "totale_biglietti_trovati": len(biglietti),
            "biglietti": biglietti
        }

        output_file.write_text(json.dumps(output_data, indent=2, ensure_ascii=False))
        logger.info(f"Risultati salvati: {output_file}")

    def send_telegram_notification(self, biglietti: List[Dict], lista_aggiornata: bool):
        """Invia notifica Telegram tramite OpenClaw message tool"""
        telegram_config = self.config.get("telegram", {})

        if not telegram_config.get("enabled", False):
            logger.info("Telegram notifiche disabilitate in config")
            return

        topic_id = telegram_config.get("topic_id", 1125)

        # Ottieni timestamp ultimo aggiornamento lista
        last_update = self.get_last_update_timestamp()

        # Separa biglietti BLOCCO B da altri
        blocco_b = [b for b in biglietti if b.get("blocco", "").startswith("B")]
        altri = [b for b in biglietti if not b.get("blocco", "").startswith("B")]

        # Costruisci messaggio
        message = f"🎫 *BIGLIETTI [Max Pezzali]({self.base_url}) DISPONIBILI*\n\n"

        # Info aggiornamento lista
        if lista_aggiornata:
            message += "✅ *Lista eventi aggiornata*\n"
        else:
            message += "ℹ️ Lista eventi invariata\n"
        message += f"🕐 Ultimo aggiornamento: {last_update}\n\n"
        message += "---\n\n"

        # BLOCCO B - ALERT SPECIALE
        if blocco_b:
            message += "🔴🔴🔴 *BLOCCO B TROVATO!* 🔴🔴🔴\n\n"
            for b in blocco_b:
                desc = f"{b['giorno']} {b['data']} - {b['dettagli']}"
                message += f"📅 *[{desc}]({b['url']})*\n"
                message += f"💰 {b['prezzo']}\n\n"

        # Altri blocchi
        if altri:
            if blocco_b:
                message += "---\n\n"
            message += "📋 Altri blocchi disponibili:\n\n"
            for b in altri:
                desc = f"{b['giorno']} {b['data']} - {b['dettagli']}"
                message += f"📅 *[{desc}]({b['url']})*\n"
                message += f"💰 {b['prezzo']}\n\n"

        # Se nessun biglietto trovato
        if not biglietti:
            message += "❌ Nessun biglietto trovato con Quantità ≥2 in posti numerati\n"
            message += f"📊 Eventi monitorati: {len(self.eventi)}\n"

        # Invia notifica con openclaw message tool
        # Usa chat diretta invece di gruppo+topic per semplicità
        chat_id = "506258994"  # Chat diretta Atti

        try:
            result = subprocess.run(
                [
                    "openclaw", "message", "send",
                    "--channel", "telegram",
                    "--target", chat_id,
                    "--message", message
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info("✅ Notifica Telegram inviata")
            else:
                logger.error(f"Errore invio Telegram: {result.stderr}")
        except Exception as e:
            logger.error(f"Errore invio Telegram: {e}")


async def main():
    monitor = FanSaleMonitor()
    await monitor.check_all_dates()


if __name__ == "__main__":
    asyncio.run(main())
