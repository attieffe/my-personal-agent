#!/usr/bin/env python3
"""
Script per estrarre biglietti FanSale usando il browser tool di OpenClaw
"""
import json
import time
from datetime import datetime
from pathlib import Path
import asyncio
import subprocess

# ID eventi
EVENTI = [
    {"id": "21343215", "data": "2026-12-22", "giorno": "Martedì"},
    {"id": "21343717", "data": "2026-12-23", "giorno": "Mercoledì"},
    {"id": "21343715", "data": "2026-12-26", "giorno": "Sabato"},
    {"id": "21343722", "data": "2026-12-27", "giorno": "Domenica"},
    {"id": "21343718", "data": "2026-12-29", "giorno": "Martedì"},
    {"id": "21343719", "data": "2026-12-30", "giorno": "Mercoledì"},
    {"id": "21928067", "data": "2027-01-03", "giorno": "Domenica"},
]

BASE_URL = "https://www.fansale.it/tickets/all/max-pezzali/482766"
OUTPUT_DIR = Path(__file__).parent / "_logs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_biglietti_from_page():
    """JavaScript per estrarre biglietti dalla pagina"""
    return """
    (() => {
        const biglietti = [];
        const items = document.querySelectorAll('[role="button"]');

        for (const item of items) {
            try {
                const text = item.textContent || '';

                // Cerca pattern "Quantità" seguito da numero
                const quantitaMatch = text.match(/Quantità\\s*(\\d+)/);
                if (!quantitaMatch) continue;

                const quantita = parseInt(quantitaMatch[1]);

                // Cerca pattern "Ingresso X | ... | Blocco XX"
                const bloccoMatch = text.match(/Ingresso\\s+(\\d+)\\s*\\|[^|]*\\|[^|]*\\|\\s*Blocco\\s+([\\w]+)/);
                if (!bloccoMatch) continue;

                const ingresso = bloccoMatch[1];
                const blocco = bloccoMatch[2];

                // Estrai prezzo (€ XXX,XX)
                const prezzoMatch = text.match(/€\\s*([\\d,\\.]+)/);
                const prezzo = prezzoMatch ? prezzoMatch[1] : "N/A";

                // Estrai dettagli completi (Ingresso ... Blocco)
                const dettagliMatch = text.match(/(Ingresso\\s+\\d+\\s*\\|[^€]+Blocco\\s+\\w+)/);
                const dettagli = dettagliMatch ? dettagliMatch[1].trim() : `Ingresso ${ingresso} | Blocco ${blocco}`;

                // Filtri
                if (quantita < 2) continue;  // Solo Qty >= 2
                if (dettagli.includes('Parterre')) continue;
                if (dettagli.includes('Posto Unico')) continue;

                biglietti.push({
                    quantita: quantita,
                    dettagli: dettagli,
                    blocco: blocco,
                    prezzo: `€ ${prezzo}`,
                    alert_blocco_b: blocco.startsWith('B') ? 'YES' : 'NO'
                });
            } catch (e) {
                // ignora errori
            }
        }

        return biglietti;
    })()
    """

def scrape_events():
    """Scrapa tutti gli eventi"""
    all_biglietti = []

    # Usa il browser già aperto (tab t22)
    target_id = "t22"

    for evento in EVENTI:
        print(f"Controllando {evento['giorno']} {evento['data']}...")

        url = f"{BASE_URL}/{evento['id']}"

        # Naviga
        cmd = ["openclaw", "browser", "navigate", "--targetId", target_id, "--url", url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"  Errore navigazione: {result.stderr}")
            continue

        # Attendi rendering
        time.sleep(3)

        # Estrai biglietti con JavaScript
        js_code = extract_biglietti_from_page()
        cmd = ["openclaw", "browser", "act", "--targetId", target_id,
               "--request", json.dumps({"kind": "evaluate", "fn": js_code})]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                if isinstance(data, list):
                    biglietti = data
                else:
                    # Potrebbe essere wrappato
                    biglietti = data.get("result", []) if isinstance(data, dict) else []

                # Aggiungi metadati evento
                for b in biglietti:
                    b["evento_id"] = evento["id"]
                    b["data"] = evento["data"]
                    b["giorno"] = evento["giorno"]
                    b["url"] = url
                    b["timestamp"] = datetime.now().isoformat()

                all_biglietti.extend(biglietti)
                print(f"  → Trovati {len(biglietti)} biglietti idonei (Qty≥2)")
            except:
                print(f"  → Errore parsing JavaScript")
        else:
            print(f"  → Errore estrazione: {result.stderr}")

        time.sleep(1)

    return all_biglietti

def save_results(biglietti):
    """Salva risultati"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"monitor_{timestamp}.json"

    # Separa per BLOCCO B
    blocco_b = [b for b in biglietti if b.get("alert_blocco_b") == "YES"]
    altri = [b for b in biglietti if b.get("alert_blocco_b") != "YES"]

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "totale_biglietti_idonei": len(biglietti),
        "blocco_b_count": len(blocco_b),
        "altri_count": len(altri),
        "biglietti": biglietti
    }

    output_file.write_text(json.dumps(output_data, indent=2, ensure_ascii=False))
    print(f"\nRisultati salvati: {output_file}")
    print(f"Totale biglietti trovati: {len(biglietti)} (Blocco B: {len(blocco_b)}, altri: {len(altri)})")

    return biglietti, blocco_b

if __name__ == "__main__":
    print("=== FanSale Biglietti Monitor ===\n")

    biglietti, blocco_b = scrape_events() if scrape_events() else ([], [])
    save_results(biglietti)

    if blocco_b:
        print("\n🔴 ALERT BLOCCO B TROVATO!")
        for b in blocco_b:
            print(f"  {b['giorno']} {b['data']}: {b['dettagli']} ({b['quantita']} biglietti)")
