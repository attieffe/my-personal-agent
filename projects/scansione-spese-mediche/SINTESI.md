# 🏥 Scansione Spese Mediche

Estrae automaticamente i dati dalle ricevute mediche scansionate (PDF multi-pagina) e produce un file Excel strutturato.

---

## Cosa fa

- Legge un PDF dove ogni pagina è una ricevuta medica scansionata
- Per ogni pagina estrae: **data**, **codice fiscale**, **persona**, **importo**, **struttura/farmacia**
- Riconosce i 4 CF di famiglia tramite whitelist + fuzzy match (corregge errori OCR)
- Produce un file `.xlsx` pronto per Google Sheets o analisi manuale

## Quando usarlo

Una o più volte l'anno, quando si raccoglie un nuovo blocco di ricevute mediche da classificare (es. per 730, rimborsi, archivio personale).

---

## Istruzioni di utilizzo

### 1. Installazione dipendenze (solo la prima volta)

```bash
pip install pymupdf pytesseract openpyxl pillow anthropic
sudo apt install tesseract-ocr tesseract-ocr-ita
```

### 2. Caricare il PDF

Copia il PDF scansionato nel workspace, ad esempio:

```
/home/openclaw/.openclaw/workspace/_attachments/temp/ricevute.pdf
```

### 3. Lanciare lo script

```bash
python /home/openclaw/.openclaw/workspace/_utility/static/pdf_ricevute_mediche.py \
  /path/to/ricevute.pdf \
  /path/to/output/ricevute_mediche.xlsx
```

Esempio concreto:
```bash
python /home/openclaw/.openclaw/workspace/_utility/static/pdf_ricevute_mediche.py \
  /home/openclaw/.openclaw/workspace/_attachments/temp/ricevute.pdf \
  /home/openclaw/.openclaw/workspace/_attachments/temp/ricevute_mediche.xlsx
```

### 4. Output

Il file `.xlsx` contiene una riga per ricevuta con:

| Pagina | Data | Codice Fiscale | Persona | Importo (€) | Struttura/Farmacia |
|--------|------|----------------|---------|-------------|-------------------|
| 1 | 12/03/2025 | FMNTTL87T11D976U | Attilio | 45,50 | Farmacia Centrale |

---

## Configurazione

Lo script `_utility/static/pdf_ricevute_mediche.py` ha in testa la sezione `CONFIGURAZIONE` con:

- **`KNOWN_CF`** — dizionario CF → nome persona (4 membri famiglia)
- **`INPUT_PDF`** / **`OUTPUT_XLSX`** — path default se non passati da riga di comando

Se cambia un CF o si aggiunge un familiare, modificare solo quella sezione.

### CF configurati

| CF | Persona |
|----|---------|
| FMNTTL87T11D976U | Attilio |
| MSCCHR81M66E951K | Chiara |
| FMNLSN20E27D286P | Alessandro |
| FMNLCA22L65B729C | Alice ⚠️ verificare su codicefiscale.it |

---

## Architettura rapida

```
PDF scansionato
    ↓ pymupdf (300 dpi)
Immagine per pagina
    ↓ pytesseract (OCR italiano, locale)
Testo grezzo
    ↓ regex
CF / data / importo
    ↓ fuzzy match whitelist
Persona identificata
    ↓ Claude Haiku (solo se regex fallisce)
Struttura/farmacia + campi mancanti
    ↓ openpyxl
ricevute_mediche.xlsx
```

**Token spesi:** quasi zero per i campi con pattern fisso (CF, data, importo). Haiku usato solo per struttura/farmacia e casi non trovati da regex.
