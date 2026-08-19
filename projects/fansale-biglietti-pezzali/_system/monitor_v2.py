#!/usr/bin/env python3
"""
FanSale Max Pezzali Monitor v2 - OpenClaw Browser Tool
Usa il browser tool di OpenClaw invece di Playwright autonomo
Bypass robusto del bot detection usando browser reale con profilo
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Path configurazione
config_path = Path(__file__).parent / "config.json"
eventi_list_path = Path(__file__).parent / "eventi_list.json"
output_dir = Path(__file__).parent.parent / "_logs"
output_dir.mkdir(parents=True, exist_ok=True)

def load_config():
    """Carica configurazione"""
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text())

def load_eventi_list():
    """Carica lista eventi"""
    if eventi_list_path.exists():
        try:
            data = json.loads(eventi_list_path.read_text())
            return data.get("eventi", [])
        except:
            pass

    # Default
    return [
        {"id": "21343215", "data": "2026-12-22", "giorno": "Martedì"},
        {"id": "21343717", "data": "2026-12-23", "giorno": "Mercoledì"},
        {"id": "21343715", "data": "2026-12-26", "giorno": "Sabato"},
        {"id": "21343722", "data": "2026-12-27", "giorno": "Domenica"},
        {"id": "21343718", "data": "2026-12-29", "giorno": "Martedì"},
        {"id": "21343719", "data": "2026-12-30", "giorno": "Mercoledì"},
        {"id": "21928067", "data": "2027-01-03", "giorno": "Domenica"},
    ]

def browser_cmd(action, **params):
    """Esegue comando browser tool"""
    cmd = ["openclaw", "browser", action]
    for k, v in params.items():
        # Converti snake_case a kebab-case per CLI
        key = k.replace("_", "-")
        cmd.extend([f"--{key}", str(v)])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Comando: {' '.join(cmd)}")
        raise Exception(f"Browser error: {result.stderr}")

    return json.loads(result.stdout)

def extract_biglietti_from_snapshot(snapshot_text: str) -> List[Dict]:
    """Estrae biglietti da snapshot browser tool"""
    biglietti = []

    # Parsing snapshot per trovare pattern biglietti
    # Formato: "Quantità" seguito da numero, poi "Ingresso ... Blocco X", poi "€ XX"
    lines = snapshot_text.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i]

        # Cerca "Quantità"
        if 'Quantità' in line and i + 2 < len(lines):
            try:
                # Prossime righe dovrebbero avere numero, dettagli, prezzo
                quantita_line = lines[i + 1] if i + 1 < len(lines) else ""
                dettagli_line = ""
                prezzo_line = ""

                # Cerca nelle prossime 10 righe
                for j in range(i + 1, min(i + 15, len(lines))):
                    if "Ingresso" in lines[j] and "Blocco" in lines[j]:
                        dettagli_line = lines[j]
                    if "€" in lines[j] and not "Prezzo fisso" in lines[j]:
                        prezzo_line = lines[j]

                # Parse quantità
                quantita = 0
                if quantita_line.strip().isdigit():
                    quantita = int(quantita_line.strip())

                # Parse blocco
                blocco = ""
                if "Blocco" in dettagli_line:
                    parts = dettagli_line.split("Blocco")
                    if len(parts) > 1:
                        blocco = parts[1].strip().split()[0] if parts[1].strip() else ""

                if quantita > 0 and dettagli_line and blocco:
                    biglietti.append({
                        "quantita": quantita,
                        "dettagli": dettagli_line.strip(),
                        "blocco": blocco,
                        "prezzo": prezzo_line.strip()
                    })
            except:
                pass

        i += 1

    return biglietti

def check_evento(evento: Dict, tab_id: str) -> List[Dict]:
    """Controlla singolo evento usando browser tool"""
    base_url = "https://www.fansale.it/tickets/all/max-pezzali/482766"
    url = f"{base_url}/{evento['id']}"

    print(f"Controllo {evento['giorno']} {evento['data']}...")

    try:
        # Naviga
        browser_cmd("navigate", targetId=tab_id, url=url, timeoutMs=20000)

        # Attendi rendering
        import time
        time.sleep(8)

        # Snapshot per vedere cosa c'è
        snapshot = browser_cmd("snapshot", targetId=tab_id, refs="aria", maxWidth=800)
        snapshot_text = snapshot.get("snapshot", "")

        # Cerca e clicca "Carica Offerte" se presente
        if "Carica Offerte" in snapshot_text:
            print("   → Cerco pulsante 'Carica Offerte'...")
            # Cerca ref del pulsante
            for line in snapshot_text.split('\n'):
                if "Carica Offerte" in line and "[ref=" in line:
                    ref = line.split("[ref=")[1].split("]")[0]
                    try:
                        browser_cmd("act", targetId=tab_id, request=json.dumps({"kind": "click", "ref": ref}))
                        print("   → Cliccato, attendo caricamento...")
                        time.sleep(6)
                        # Nuovo snapshot
                        snapshot = browser_cmd("snapshot", targetId=tab_id, refs="aria", maxWidth=800)
                        snapshot_text = snapshot.get("snapshot", "")
                        break
                    except:
                        pass

        # Estrai biglietti
        biglietti = extract_biglietti_from_snapshot(snapshot_text)

        # Filtra: solo Quantità ≥2, posti numerati (no Parterre, no Posto Unico)
        biglietti_validi = []
        for b in biglietti:
            if (b["quantita"] >= 2 and
                b["blocco"] and
                "Parterre" not in b["dettagli"] and
                "Posto Unico" not in b["dettagli"]):

                biglietti_validi.append({
                    "evento_id": evento["id"],
                    "data": evento["data"],
                    "giorno": evento["giorno"],
                    **b,
                    "url": url,
                    "timestamp": datetime.now().isoformat()
                })

        print(f"   → Trovati {len(biglietti_validi)} biglietti validi (Quantità ≥2)")
        return biglietti_validi

    except Exception as e:
        print(f"   ❌ Errore: {e}")
        return []

def send_telegram(biglietti: List[Dict]):
    """Invia notifica Telegram"""
    config = load_config()
    chat_id = "506258994"

    # Separa BLOCCO B
    blocco_b = [b for b in biglietti if b["blocco"].startswith("B")]
    altri = [b for b in biglietti if not b["blocco"].startswith("B")]

    # Costruisci messaggio
    msg = "🎫 *BIGLIETTI MAX PEZZALI DISPONIBILI*\n\n"

    if blocco_b:
        msg += "🔴🔴🔴 *BLOCCO B TROVATO!* 🔴🔴🔴\n\n"
        for b in blocco_b:
            msg += f"📅 *{b['giorno']} {b['data']}*\n"
            msg += f"🎯 {b['dettagli']}\n"
            msg += f"💰 {b['prezzo']}\n"
            msg += f"🔗 {b['url']}\n\n"

    if altri:
        if blocco_b:
            msg += "---\n\n"
        msg += "📋 Altri blocchi disponibili:\n\n"
        for b in altri:
            msg += f"📅 {b['giorno']} {b['data']}\n"
            msg += f"🎯 {b['dettagli']}\n"
            msg += f"💰 {b['prezzo']}\n\n"

    if not biglietti:
        msg += "❌ Nessun biglietto con Quantità ≥2 trovato\n"

    # Invia
    try:
        result = subprocess.run(
            ["openclaw", "message", "send", "--channel", "telegram", "--target", chat_id, "--message", msg],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print("✅ Notifica Telegram inviata")
        else:
            print(f"❌ Errore Telegram: {result.stderr}")
    except Exception as e:
        print(f"❌ Errore Telegram: {e}")

def main():
    print("=== FanSale Monitor v2 (OpenClaw Browser) ===\n")

    eventi = load_eventi_list()
    print(f"Eventi da controllare: {len(eventi)}\n")

    # Apri browser tab
    print("Apertura browser...")
    tab = browser_cmd("open", url="https://www.fansale.it/")
    tab_id = tab.get("suggestedTargetId") or tab.get("targetId")

    import time
    time.sleep(3)

    # Controlla eventi
    tutti_biglietti = []
    for evento in eventi:
        biglietti = check_evento(evento, tab_id)
        tutti_biglietti.extend(biglietti)
        time.sleep(2)  # Pausa tra eventi

    # Chiudi tab
    try:
        browser_cmd("close", targetId=tab_id)
    except:
        pass

    # Salva risultati
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"monitor_{timestamp}.json"

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "totale_biglietti": len(tutti_biglietti),
        "biglietti": tutti_biglietti
    }

    output_file.write_text(json.dumps(output_data, indent=2, ensure_ascii=False))
    print(f"\nRisultati salvati: {output_file}")

    # Telegram
    send_telegram(tutti_biglietti)

    print("\n=== Fine ===")

if __name__ == "__main__":
    main()
