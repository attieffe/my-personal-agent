# CHANGELOG

## 2026-06-21 — v2.0
- DPI aumentato: 200 → 300 (migliora lettura testo piccolo)
- Prompt Haiku riformulato: più esplicito su dove cercare CF, data, importo
- Normalizzazione date: qualsiasi formato → DD/MM/YYYY
- Normalizzazione importi: punto anglosassone → virgola italiana
- Fuzzy match CF: soglia abbassata 0.82 → 0.72 (cattura più errori OCR)
- Retry automatico con backoff su errori 429 (rate limit OAuth)
- Delay 1s tra pagine per evitare rate limit
- Risultato: CF identificati 22/46 (48%) → 28/46 (61%)
- Output: `ricevute_mediche_v2.xlsx`

## 2026-06-21 — v1.0
- Prima versione script `pdf_ricevute_mediche.py`
- Stack: pymupdf + Claude Haiku Vision + openpyxl
- Whitelist 4 CF famiglia con fuzzy match (cutoff 0.82)
- DPI 200, output XLSX con header colorato e auto-filter
- Risultato: CF identificati 22/46 (48%)
- Output: `ricevute_mediche_v1.xlsx` (originale: v1, rinominato dopo v2)
