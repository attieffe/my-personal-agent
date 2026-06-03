# Archiviazione Ottica Documenti — Tecnico

## Stack

- **Vision AI:** Claude API (claude-sonnet-4-6) — analisi immagini e PDF
- **Drive upload:** rclone CLI, remote `gdrive` (già configurato in `~/.config/rclone/rclone.conf`)
- **Canale Telegram:** chat_id `-1003877516285`, topic_id `2069`
- **AttiBot upload intake:** `/home/openclaw/attibot/uploads/<ref>/`

## Flusso principale

```
INPUT
  ├── Telegram topic attachment → salva in input/
  ├── AttiBot upload ref → link/copia in input/
  └── File già in input/ (copia manuale)
         ↓
ANALISI (_system/vision_namer.py)
  - Identifica tipo documento
  - Estrae data documento (OCR se necessario)
  - Propone nome: YYYYMMDD titolo.ext
  - Identifica categoria → cerca regole in ROUTING_RULES.md
         ↓
PROPOSTA AD ATTI (via Telegram)
  - Nome proposto
  - Categoria identificata
  - Destinazioni Drive (1 o più)
  - Richiede conferma
         ↓
ARCHIVIAZIONE (_system/drive_uploader.py)
  - rclone copy verso ogni destinazione confermata
  - Append su history.md
  - Sposta originale in 90_processed/ (mai cancella)
```

## Naming convention

`YYYYMMDD titolo documento.estensione`

- Data: estratta dal documento (non dalla data di ricezione)
- Titolo: proposto da AI se non già parlante
- Sempre minuscolo, spazi come spazi (no underscore forzati)

## Struttura cartelle

```
input/              ← intake (gitignored, mai committato)
90_processed/       ← originali dopo archiviazione (gitignored)
history.md          ← log append di ogni archiviazione
_system/            ← codice algoritmo
_knowledge/         ← dati e regole (autoapprendimento)
```

## Drive paths (rclone)

rclone usa `gdrive:` come prefisso per Google Drive.

Esempi:
- `gdrive:Atti/Documenti/Archiviazione ottica/2026/`
- `gdrive:Atti/Documenti/DICHIARAZIONE DEI REDDITI/2026x2025/`
- `gdrive:Atti/Documenti/Sanità/`
- `gdrive:Ingenio/DOCUMENTI FISCALI/2026/`

## Dipendenze

- `rclone` (già installato, remote `gdrive` configurato)
- `python3` con `anthropic` SDK
- Accesso Telegram per notifiche e ricezione allegati
