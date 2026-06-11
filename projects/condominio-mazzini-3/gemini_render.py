#!/usr/bin/env python3
"""
Condominio Mazzini 3 — Gemini Rendering Pipeline
Legge RENDERING_QUEUE.json, genera una proposta completa (3 foto),
salva le immagini, marca il task come done, restituisce msg di notifica.

Exit codes: 0=ok, 1=errore, 2=no pending, 3=billing required
"""
import json
import os
import sys
import pathlib
import datetime
import time

BASE_DIR  = "/home/openclaw/attibot/condominio"
QUEUE     = "/home/openclaw/.openclaw/workspace/projects/condominio-mazzini-3/RENDERING_QUEUE.json"
IMG_DIR   = f"{BASE_DIR}/img"
ORIG_DIR  = f"{BASE_DIR}/img/originali"

GEMINI_KEY = None
env_file = f"{BASE_DIR}/.env"
if os.path.exists(env_file):
    for line in pathlib.Path(env_file).read_text().splitlines():
        if line.startswith("GEMINI_API_KEY="):
            GEMINI_KEY = line.split("=", 1)[1].strip()

MODELS = [
    "gemini-3.1-flash-image",
    "gemini-3.1-flash-image-preview",
    "gemini-3-pro-image",
    "gemini-3-pro-image-preview",
]

PHOTOS = [
    {"file": "foto1.jpg", "focus": "facciata"},
    {"file": "foto2.jpg", "focus": "balconi"},
    {"file": "foto3.jpg", "focus": "dettagli"},
]

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

def make_prompt(proposal, focus):
    dom = proposal["dominant"]
    sec = proposal["secondary"]
    acc = proposal.get("accessory", {})
    acc_line = ""
    if acc.get("hex"):
        acc_line = f"• ACCESSORI — contorni finestre, pilastri, bordi strutturali, soglie: {acc['hex']} · {acc['name']} · {acc.get('code','')}"

    focus_desc = {
        "facciata": (
            "Inquadratura FACCIATA PRINCIPALE — visione d'insieme dell'edificio. "
            "In questa vista si deve vedere la palette completa applicata: il colore DOMINANTE copre "
            "le grandi superfici murarie, il colore SECONDARIO appare sulle fasce orizzontali "
            "tra i piani, il colore ACCESSORIO è visibile su contorni finestre e bordi strutturali."
        ),
        "balconi": (
            "Inquadratura BALCONI E FASCE — focus sulle fasce interpiano e sui balconi. "
            "La palette completa deve essere visibile: il colore DOMINANTE sulle pareti principali "
            "fa da sfondo, il colore SECONDARIO risalta sulle fasce orizzontali e sui soffitti dei "
            "balconi, il colore ACCESSORIO appare sui bordi e contorni. "
            "La palette è identica alla foto 1, cambia solo l'angolazione."
        ),
        "dettagli": (
            "Inquadratura DETTAGLI ARCHITETTONICI — vista ravvicinata o allargata che mostra "
            "l'insieme cromatico con chiarezza. "
            "La palette completa deve essere coerente con le foto precedenti: colore DOMINANTE "
            "sulle superfici murarie, SECONDARIO sulle fasce, ACCESSORIO su contorni e pilastri. "
            "I tre colori devono essere riconoscibili e identici per tinta agli esadecimali indicati."
        ),
    }[focus]

    return f"""Sei un visualizzatore architettonico professionale specializzato in rendering cromatici per condomini italiani degli anni '80.

EDIFICIO: Condominio Mazzini 3, Via Pacini 77/79/81, Seregno — edificio residenziale anni '80, facciate in intonaco, con fasce orizzontali decorative tra i piani, balconi a sbalzo, serramenti e tapparelle marrone Douglas.

PROPOSTA CROMATICA: {proposal['title']}

PALETTE CROMATICA — APPLICARE IN MODO IDENTICO IN TUTTE E 3 LE FOTO:
• DOMINANTE — superfici murarie principali, pannelli di facciata: {dom['hex']} · {dom['name']} · {dom.get('code','')}
• SECONDARIO — fasce orizzontali interpiano, soffitti balconi, cornici: {sec['hex']} · {sec['name']} · {sec.get('code','')}
{acc_line}

REGOLA DI COERENZA CROMATICA (CRITICA):
Le 3 foto rappresentano la STESSA proposta cromatica da angolazioni diverse.
Il colore dominante DEVE essere identico in tutte e 3 le foto.
Il colore secondario DEVE essere identico in tutte e 3 le foto.
Il colore accessorio DEVE essere identico in tutte e 3 le foto.
NON cambiare, variare o omettere nessuno dei 3 colori tra una foto e l'altra.

ISTRUZIONE DI RENDERING (ANGOLAZIONE):
{focus_desc}

VINCOLI ASSOLUTI — NON MODIFICARE MAI:
- Geometria, struttura, proporzioni e prospettiva del palazzo (nessuna aggiunta/rimozione di elementi)
- Finestre: vetri (riflessi, trasparenze) e telai
- Tapparelle e persiane marrone Douglas (colore invariato)
- Cielo, nuvole, luce, ombre
- Vegetazione, alberi, aiuole
- Strada, marciapiede, auto, persone, pavimentazione
- Qualsiasi elemento non appartenente alla facciata dell'edificio

OUTPUT ATTESO: rendering fotorealistico ad alta qualità, come se fosse una simulazione cromatica professionale per approvazione in assemblea condominiale. I colori devono essere uniformi, puliti e fedeli agli esadecimali indicati."""


# ---------------------------------------------------------------------------
# Generazione Gemini
# ---------------------------------------------------------------------------

def generate_images(proposal):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GEMINI_KEY)
    code = proposal["code"]
    results = []

    for i, photo in enumerate(PHOTOS, 1):
        src = os.path.join(ORIG_DIR, photo["file"])
        dst = os.path.join(IMG_DIR, f"{code}_foto{i}.jpg")

        img_bytes = pathlib.Path(src).read_bytes()
        prompt_text = make_prompt(proposal, photo["focus"])

        last_err = None
        for model in MODELS:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=[
                        types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                        types.Part.from_text(text=prompt_text),
                    ],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE", "TEXT"]
                    ),
                )
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "inline_data") and part.inline_data:
                        pathlib.Path(dst).write_bytes(part.inline_data.data)
                        results.append(f"img/{code}_foto{i}.jpg")
                        print(f"  ✅ {code}_foto{i}.jpg ({model})")
                        last_err = None
                        break
                if last_err is None:
                    break
            except Exception as e:
                err_str = str(e)
                last_err = err_str
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    # Billing required — stop immediately, no point trying other models
                    raise RuntimeError(f"BILLING_REQUIRED: {err_str[:200]}")
                print(f"  ⚠️  {model}: {err_str[:120]}")
                time.sleep(2)

        if last_err and "BILLING_REQUIRED" not in last_err:
            raise RuntimeError(f"All Gemini models failed for foto{i}: {last_err}")

    return results


# ---------------------------------------------------------------------------
# Queue management
# ---------------------------------------------------------------------------

def read_queue():
    with open(QUEUE) as f:
        return json.load(f)

def write_queue(data):
    data["last_updated"] = now_iso()
    with open(QUEUE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def now_iso():
    tz = datetime.timezone(datetime.timedelta(hours=2))
    return datetime.datetime.now(tz).isoformat()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not GEMINI_KEY:
        print("ERROR: GEMINI_API_KEY not found in .env")
        return 1

    data = read_queue()
    pending = [item for item in data["queue"] if item["status"] == "pending"]

    if not pending:
        print("NO_PENDING: Queue is empty, nothing to do.")
        return 2

    proposal = pending[0]
    code = proposal["code"]
    print(f"\n→ Processing {code} — {proposal['title']}")
    print(f"  Remaining after this: {len(pending)-1}")

    try:
        images = generate_images(proposal)

        # Mark done
        for item in data["queue"]:
            if item["code"] == code:
                item["status"] = "done"
                item["done"] = now_iso()
                item["output_images"] = images
        write_queue(data)

        remaining = len(pending) - 1
        url = f"https://attibot.ingeniosolution.it/reports/condominio/proposte_facciate.html#{code}"
        print(f"\nNOTIFY: ✅ Rendering {code} completato ({proposal['title'][:35]}). "
              f"Rimangono {remaining} proposte. Vedi: {url}")
        return 0

    except RuntimeError as e:
        err = str(e)
        if "BILLING_REQUIRED" in err:
            print(f"\nBILLING_REQUIRED: Gemini image generation richiede fatturazione attiva su Google AI Studio.")
            return 3
        print(f"\nERROR: {err}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
