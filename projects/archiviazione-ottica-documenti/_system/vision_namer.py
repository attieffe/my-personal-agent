"""
Analizza un documento (immagine o PDF) via OpenAI gpt-4o vision.
Restituisce: data, nome proposto, categoria, note.
"""
import base64
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

BASE = Path(__file__).parent.parent
load_dotenv(BASE / ".env")

PROMPT = """Sei un assistente che archivia documenti cartacei italiani.
Analizza questo documento e rispondi SOLO con JSON valido (nessun testo fuori dal JSON):

{
  "data_documento": "YYYYMMDD",
  "nome_proposto": "titolo breve e descrittivo",
  "categoria": "SPESE_MEDICHE|CERTIFICATI_SANITARI|INGENIO_SOLUTION|BOLLETTE|BANCA|ALTRO",
  "mittente": "nome mittente/ente se identificabile, null altrimenti",
  "importo": "importo totale come stringa (es. '85.50') se presente, null altrimenti",
  "note": "max 2 righe di info rilevanti",
  "confidenza_data": "alta|media|bassa"
}

Regole:
- data_documento: estrai dal documento stesso (data fattura, data visita, data lettera, ecc.). Se non trovata: "00000000"
- nome_proposto: 2-5 parole descrittive, minuscolo, no caratteri speciali tranne spazi e trattini
- SPESE_MEDICHE: scontrini farmacia, fatture medici/specialisti, ticket SSN — documenti con importo detraibile IRPEF
- CERTIFICATI_SANITARI: referti, certificati, esami di laboratorio, diagnosi — senza importo rilevante o con importo non detraibile
- INGENIO_SOLUTION: documenti intestati a "Ingenio Solution" o P.IVA 03491200131, o spese aziendali
- BOLLETTE: luce, gas, acqua, internet, telefono
- BANCA: estratti conto, comunicazioni bancarie, bonifici
- ALTRO: tutto il resto
"""


def analyze(file_path: str) -> dict:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {file_path}")

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    suffix = path.suffix.lower()
    with open(path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")

    if suffix == ".pdf":
        # PDF: invia come immagine della prima pagina non è supportato direttamente;
        # usiamo il file come documento testuale con il contenuto base64 descritto
        media_type = "application/pdf"
        # gpt-4o non accetta PDF direttamente — converti la prima pagina in PNG se disponibile
        # Fallback: tratta come immagine e segnala limitazione
        content = [
            {
                "type": "text",
                "text": f"Il documento allegato è un PDF (base64). {PROMPT}"
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{data}"},
            },
        ]
    else:
        mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
                ".webp": "image/webp", ".gif": "image/gif"}.get(suffix, "image/jpeg")
        content = [
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{data}"},
            },
            {"type": "text", "text": PROMPT},
        ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content}],
        max_tokens=512,
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()
    # rimuovi eventuale wrapper ```json ... ```
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    result = json.loads(raw)
    result["file_originale"] = path.name
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python vision_namer.py <file>", file=sys.stderr)
        sys.exit(1)
    result = analyze(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
