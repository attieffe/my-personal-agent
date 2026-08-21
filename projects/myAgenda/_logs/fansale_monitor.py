#!/usr/bin/env python3
"""
FanSale Max Pezzali Monitor
Monitoraggio biglietti per concerti Max Pezzali a Milano
"""

import json
import time
from datetime import datetime
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

BASE_URL = "https://www.fansale.it"
MASTER_URL = f"{BASE_URL}/tickets/all/max-pezzali/482766"

# Eventi Milano da monitorare
EVENTI_MILANO = [
    {
        "data": "22 Dicembre 2026",
        "descrizione": "Max Pezzali Milano Unipol Dome",
        "url": f"{BASE_URL}/tickets/all/max-pezzali/482766/21343215"
    },
    {
        "data": "22 Dicembre 2026",
        "descrizione": "Max Pezzali - Unipol Dome Party Terrace Milano",
        "url": f"{BASE_URL}/tickets/all/max-pezzali/482766/21353575"
    },
    {
        "data": "23 Dicembre 2026",
        "descrizione": "Max Pezzali Milano Unipol Dome",
        "url": f"{BASE_URL}/tickets/all/max-pezzali/482766/21343717"
    },
    {
        "data": "26 Dicembre 2026",
        "descrizione": "Max Pezzali Milano Unipol Dome",
        "url": f"{BASE_URL}/tickets/all/max-pezzali/482766/21343715"
    },
    {
        "data": "27 Dicembre 2026",
        "descrizione": "Max Pezzali Milano Unipol Dome",
        "url": f"{BASE_URL}/tickets/all/max-pezzali/482766/21343722"
    },
    {
        "data": "29 Dicembre 2026",
        "descrizione": "Max Pezzali Milano Unipol Dome",
        "url": f"{BASE_URL}/tickets/all/max-pezzali/482766/21343718"
    },
    {
        "data": "30 Dicembre 2026",
        "descrizione": "Max Pezzali Milano Unipol Dome",
        "url": f"{BASE_URL}/tickets/all/max-pezzali/482766/21343719"
    },
    {
        "data": "3 Gennaio 2027",
        "descrizione": "Max Pezzali Milano Unipol Dome",
        "url": f"{BASE_URL}/tickets/all/max-pezzali/482766/21928067"
    }
]

def check_evento(page, evento):
    """Controlla un singolo evento per biglietti disponibili"""
    risultato = {
        "data": evento["data"],
        "descrizione": evento["descrizione"],
        "url": evento["url"],
        "biglietti_trovati": [],
        "blocco_b_presente": False,
        "errore": None,
        "timestamp": datetime.now().isoformat()
    }

    try:
        print(f"⏳ Controllo: {evento['descrizione']}")
        page.goto(evento["url"], timeout=30000, wait_until="networkidle")
        time.sleep(2)

        # Cerca e clicca il bottone "Carica Offerte" se presente
        try:
            carica_btn = page.locator("button:has-text('Carica Offerte')").first
            if carica_btn.is_visible(timeout=5000):
                print("   Clic su 'Carica Offerte'...")
                carica_btn.click()
                time.sleep(3)
        except Exception:
            pass  # Bottone non presente o già caricato

        # Cerca biglietti con Qtà >= 2
        # Pattern: cerca elementi che mostrano quantità e settore
        biglietti_elements = page.locator("[class*='offer'], [class*='ticket']").all()

        for el in biglietti_elements:
            try:
                testo = el.text_content()
                if not testo:
                    continue

                # Cerca pattern di quantità (es. "2x", "Qtà: 2", ecc.)
                # E settore (es. "BLOCCO B", "B5", ecc.)
                testo_lower = testo.lower()

                # Verifica quantità >= 2
                # (logica semplificata, da raffinare)
                if any(q in testo for q in ["2x", "3x", "4x", "Qtà: 2", "Qtà: 3", "Qtà: 4"]):
                    # Esclude Parterre e Posto Unico
                    if "parterre" not in testo_lower and "posto unico" not in testo_lower:
                        risultato["biglietti_trovati"].append({
                            "testo": testo.strip()[:200],  # Primi 200 char
                        })

                        # Verifica BLOCCO B
                        if "blocco b" in testo_lower or "b5" in testo_lower or "b6" in testo_lower:
                            risultato["blocco_b_presente"] = True
            except Exception:
                continue

        print(f"   ✅ Trovati {len(risultato['biglietti_trovati'])} biglietti")

    except PlaywrightTimeout:
        risultato["errore"] = "Timeout navigazione"
        print(f"   ⚠️  Timeout")
    except Exception as e:
        risultato["errore"] = str(e)[:200]
        print(f"   ❌ Errore: {str(e)[:100]}")

    return risultato

def main():
    """Funzione principale di monitoraggio"""
    print("🎵 FanSale Max Pezzali Monitor")
    print("=" * 50)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    risultati = {
        "timestamp": timestamp,
        "master_url": MASTER_URL,
        "eventi": []
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = context.new_page()

        for evento in EVENTI_MILANO:
            risultato = check_evento(page, evento)
            risultati["eventi"].append(risultato)

            # Attendi 10 secondi tra un evento e l'altro
            time.sleep(10)

        browser.close()

    # Salva risultati
    log_file = f"/home/openclaw/.openclaw/workspace/projects/myAgenda/_logs/monitor_{timestamp}.json"
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(risultati, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Report salvato: {log_file}")

    # Prepara messaggio Telegram
    messaggio = genera_messaggio_telegram(risultati)

    # Salva anche il messaggio
    msg_file = f"/home/openclaw/.openclaw/workspace/projects/myAgenda/_logs/telegram_message_{timestamp}.txt"
    with open(msg_file, "w", encoding="utf-8") as f:
        f.write(messaggio)

    print("\n📱 MESSAGGIO TELEGRAM:")
    print("=" * 50)
    print(messaggio)
    print("=" * 50)

    return messaggio

def genera_messaggio_telegram(risultati):
    """Genera il messaggio formattato per Telegram"""
    msg = f"📌 [Max Pezzali]({MASTER_URL})\n\n"

    totali_testati = 0
    totali_errori = 0
    totali_biglietti = 0
    blocco_b_trovato = False

    for evento in risultati["eventi"]:
        # Link descrittivo
        msg += f"• [{evento['data']} - {evento['descrizione']}]({evento['url']})\n"

        if evento["errore"]:
            msg += f"  ⚠️ Visita fallita: {evento['errore']}\n"
            totali_errori += 1
        else:
            totali_testati += 1
            n_biglietti = len(evento["biglietti_trovati"])
            totali_biglietti += n_biglietti

            if n_biglietti > 0:
                msg += f"  ✅ Trovati {n_biglietti} biglietti (Qtà≥2)\n"
            else:
                msg += f"  ➖ Nessun biglietto trovato\n"

            # BLOCCO B
            if evento["blocco_b_presente"]:
                msg += f"  ⚠️ BLOCCO B PRESENTE!\n"
                blocco_b_trovato = True
            else:
                msg += f"  ℹ️ BLOCCO B: NO\n"

        msg += "\n"

    # Riepilogo
    msg += "📊 RIEPILOGO FINALE:\n"
    msg += f"• Eventi totali trovati: {len(risultati['eventi'])}\n"
    msg += f"• Eventi testati: {totali_testati}\n"
    msg += f"• Eventi con errori: {totali_errori}\n"
    msg += f"• Biglietti trovati (Qtà≥2): {totali_biglietti}\n"
    msg += f"• BLOCCO B: {'SÌ ⚠️' if blocco_b_trovato else 'NO'}\n"

    return msg

if __name__ == "__main__":
    main()
