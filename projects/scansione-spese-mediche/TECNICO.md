# TECNICO — Scansione Spese Mediche

## Stack

| Libreria | Ruolo |
|----------|-------|
| `pymupdf` (fitz) | Rendering PDF → immagini PNG a 300 DPI |
| `pytesseract` | OCR locale (tesseract-ocr + lang ita) |
| `Pillow` | Gestione immagini PIL |
| `openpyxl` | Generazione file XLSX |
| `anthropic` | Fallback LLM (Haiku) per campi non trovati da regex |

## Script principale

`_utility/static/pdf_ricevute_mediche.py`

## Flusso pagina per pagina

1. `pdf_to_images()` — converte ogni pagina in `PIL.Image` a 300 DPI
2. `ocr_image()` — tesseract con lang=ita, PSM 6 (blocco uniforme)
3. `parse_with_regex()` — estrae CF (pattern fisso), data, importo
4. `resolve_cf()` — fuzzy match (cutoff 0.85) contro `KNOWN_CF`
5. `parse_with_llm()` — chiamata Haiku solo per campi ancora mancanti + struttura
6. `write_xlsx()` — XLSX con header colorato, auto-filter, larghezze colonne

## Pattern regex usati

```python
RE_CF   = r'\b([A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z])\b'
RE_DATE = r'\b(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4})\b'
RE_AMT  = r'(?:totale|tot\.?|importo)[^\d]{0,20}?(\d{1,6}[.,]\d{2})|(\d{1,6}[.,]\d{2})\s*€'
```

## Modello LLM

`claude-haiku-4-5-20251001` — il più economico. Invia solo testo (max 2500 chars), mai immagini.

## Note OCR

- DPI 300 è il minimo raccomandato per tesseract su testo stampato
- `--psm 6` assume blocco di testo uniforme (buono per ricevute)
- Se la qualità OCR è bassa, provare `--psm 4` (colonna singola) o aumentare DPI a 400
