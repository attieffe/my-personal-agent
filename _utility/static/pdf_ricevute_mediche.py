#!/usr/bin/env python3
"""
pdf_ricevute_mediche.py
Estrae dati da un PDF di ricevute mediche scansionate e produce un file XLSX.

Strategia: pymupdf → immagine per pagina → Claude Haiku Vision (OCR + parsing in uno)
Zero dipendenze da tesseract. Costo stimato: ~$0.05-0.10 per 60 pagine.

Uso:
    python pdf_ricevute_mediche.py [input.pdf] [output.xlsx]

Dipendenze:
    pip install pymupdf openpyxl pillow anthropic
"""

import base64
import io
import json
import logging
import re
import sys
from difflib import get_close_matches
from pathlib import Path

import fitz  # pymupdf
from PIL import Image
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
import anthropic


def _get_anthropic_client() -> anthropic.Anthropic:
    """Usa auth_token OAuth di Claude Code se ANTHROPIC_API_KEY non è impostata."""
    import os
    if os.environ.get("ANTHROPIC_API_KEY"):
        return anthropic.Anthropic()
    creds_path = Path.home() / ".claude" / ".credentials.json"
    if creds_path.exists():
        with open(creds_path) as f:
            tok = json.load(f).get("claudeAiOauth", {}).get("accessToken", "")
        if tok:
            return anthropic.Anthropic(auth_token=tok)
    raise RuntimeError("Nessuna credenziale Anthropic trovata. Imposta ANTHROPIC_API_KEY.")

# ─── CONFIGURAZIONE ────────────────────────────────────────────────────────────

INPUT_PDF    = "ricevute.pdf"
OUTPUT_XLSX  = "ricevute_mediche.xlsx"

# Whitelist CF famiglia — fuzzy match corregge errori OCR di 1-2 caratteri
KNOWN_CF = {
    "FMNTTL87T11D976U": "Attilio",
    "MSCCHR81M66E951K": "Chiara",
    "FMNLSN20E27D286P": "Alessandro",
    "FMNLCA22L65B729C": "Alice",   # ← verificare su codicefiscale.it
}

LLM_MODEL = "claude-haiku-4-5-20251001"
DPI       = 200  # 200 DPI bilancia qualità/peso immagine (150 troppo basso, 300 troppo pesante)

# ─── LOGGING ───────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

# ─── CORE ──────────────────────────────────────────────────────────────────────

def pdf_to_images(pdf_path: str) -> list:
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=DPI)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    doc.close()
    return images


def image_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.standard_b64encode(buf.getvalue()).decode()


def resolve_cf(raw_cf: str) -> tuple:
    """Ritorna (cf_canonico, nome). Fuzzy match se OCR ha storpiato 1-2 caratteri."""
    raw_cf = raw_cf.upper().strip()
    if raw_cf in KNOWN_CF:
        return raw_cf, KNOWN_CF[raw_cf]
    candidates = get_close_matches(raw_cf, KNOWN_CF.keys(), n=1, cutoff=0.82)
    if candidates:
        cf = candidates[0]
        return cf, KNOWN_CF[cf]
    return raw_cf, "?"


PROMPT = """Sei un estrattore di dati da ricevute mediche italiane.
Analizza questa immagine ed estrai esattamente questi 4 campi:
1. data — la data della ricevuta (formato GG/MM/AAAA)
2. cf — il codice fiscale del paziente (16 caratteri alfanumerici maiuscoli)
3. importo — l'importo totale pagato (solo cifre con virgola decimale, es: 45,50)
4. struttura — nome della farmacia, studio medico o struttura sanitaria

Rispondi SOLO con JSON valido, nessun testo aggiuntivo:
{"data": "...", "cf": "...", "importo": "...", "struttura": "..."}
Se un campo non è leggibile usa null."""


def extract_page(client: anthropic.Anthropic, page_num: int, img: Image.Image) -> dict:
    log.info(f"Pagina {page_num:>3}: invio a Haiku Vision...")
    b64 = image_to_b64(img)

    msg = client.messages.create(
        model=LLM_MODEL,
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/jpeg", "data": b64},
                },
                {"type": "text", "text": PROMPT},
            ],
        }],
    )

    raw = msg.content[0].text.strip()
    m = re.search(r"\{.*?\}", raw, re.DOTALL)
    parsed = {}
    if m:
        try:
            parsed = json.loads(m.group())
        except json.JSONDecodeError:
            log.warning(f"  Pagina {page_num}: JSON non valido → {raw[:100]}")

    # Fuzzy match sul CF estratto
    cf_raw = parsed.get("cf") or ""
    cf, persona = resolve_cf(cf_raw) if cf_raw else ("", "?")

    row = {
        "pagina":    page_num,
        "data":      parsed.get("data") or "",
        "cf":        cf,
        "persona":   persona,
        "importo":   parsed.get("importo") or "",
        "struttura": parsed.get("struttura") or "",
    }
    log.info(f"          → {row}")
    return row


def write_xlsx(rows: list, output_path: str):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ricevute"

    headers = ["Pagina", "Data", "Codice Fiscale", "Persona", "Importo (€)", "Struttura/Farmacia"]
    hfill = PatternFill("solid", fgColor="2E74B5")
    hfont = Font(bold=True, color="FFFFFF")

    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill      = hfill
        cell.font      = hfont
        cell.alignment = Alignment(horizontal="center")

    for r, row in enumerate(rows, 2):
        ws.cell(r, 1, row["pagina"])
        ws.cell(r, 2, row["data"])
        ws.cell(r, 3, row["cf"])
        ws.cell(r, 4, row["persona"])
        ws.cell(r, 5, row["importo"])
        ws.cell(r, 6, row["struttura"])

    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 14
    ws.column_dimensions["E"].width = 14
    ws.column_dimensions["F"].width = 40
    ws.auto_filter.ref = ws.dimensions

    wb.save(output_path)
    log.info(f"Salvato: {output_path}")


def main():
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else INPUT_PDF
    out_path = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_XLSX

    if not Path(pdf_path).exists():
        log.error(f"File non trovato: {pdf_path}")
        sys.exit(1)

    client = _get_anthropic_client()

    log.info(f"PDF: {pdf_path}")
    images = pdf_to_images(pdf_path)
    log.info(f"Pagine totali: {len(images)}")

    rows = [extract_page(client, i, img) for i, img in enumerate(images, 1)]

    write_xlsx(rows, out_path)
    log.info(f"Completato. {len(rows)} ricevute → {out_path}")


if __name__ == "__main__":
    main()
