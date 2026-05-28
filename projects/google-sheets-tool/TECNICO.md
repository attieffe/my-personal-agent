# google-sheets-tool — Documentazione Tecnica

## Scopo
Accesso programmato (lettura/scrittura) al foglio Google Sheets "Lavori attilio" di Atti.
Foglio condiviso con `myjob@ingeniosolution.it` (account Google Workspace).

## Spreadsheet
- **ID:** `1PdJYvqA-23CiucnjwkJvQLXT1tQhQhPeuruUwlUP5fk`
- **URL:** https://docs.google.com/spreadsheets/d/1PdJYvqA-23CiucnjwkJvQLXT1tQhQhPeuruUwlUP5fk/
- **Account Google:** `myjob@ingeniosolution.it`

## Autenticazione
- **Metodo:** OAuth2 (Installed App flow)
- **Progetto GCP:** `attibot` (stesso usato per myAgenda/Calendar)
- **Client ID:** `75976842589-493eej3rh5htvopn14cucimhsji3eb22.apps.googleusercontent.com`
- **Scope:** `spreadsheets` (read+write) + `drive.readonly`
- **Token:** `_credentials/google_token.json` — refresh automatico gestito da `sheets_client.py`

## Struttura

```
google-sheets-tool/
├── _system/
│   ├── oauth_flow.py      ← flow OAuth (eseguire una volta per ottenere il token)
│   └── sheets_client.py   ← classe SheetsClient riutilizzabile
├── _credentials/
│   ├── oauth_client.json  ← client_id + client_secret (app attibot GCP)
│   └── google_token.json  ← token attivo (generato da oauth_flow.py)
├── examples/
│   └── explore_sheet.py   ← esplora struttura e prime righe del foglio
└── docs/
    └── struttura_foglio.md ← documentazione fogli (da aggiornare dopo prima lettura)
```

## Setup iniziale (da fare una volta)

### 1. Prerequisiti su Google Cloud Console (progetto `attibot`)
- Abilitare **Google Sheets API**
- Abilitare **Google Drive API**
- Verificare che `myjob@ingeniosolution.it` sia negli utenti di test (OAuth consent screen)

### 2. Generare il token
```bash
cd /home/openclaw/.openclaw/workspace/projects/google-sheets-tool
python3 _system/oauth_flow.py
```
Aprire l'URL nel browser loggato come `myjob@ingeniosolution.it`, autorizzare, incollare il codice.

### 3. Verificare l'accesso
```bash
python3 examples/explore_sheet.py
```

## Uso da altri script/agenti

```python
import sys
sys.path.insert(0, '/home/openclaw/.openclaw/workspace/projects/google-sheets-tool')
from _system.sheets_client import SheetsClient

client = SheetsClient()

# Leggi un range
rows = client.read_range("NomeFoglio!A1:Z100")

# Scrivi valori
client.write_range("NomeFoglio!A1", [["valore1", "valore2"]])

# Aggiungi riga in fondo
client.append_rows("NomeFoglio!A:Z", [["2026-05-28", "Descrizione", "100"]])

# Lista fogli
sheets = client.list_sheets()  # [(id, title), ...]
```

## Struttura del foglio
→ Vedi `docs/struttura_foglio.md` (da compilare dopo prima lettura)

## Aggiornamenti token
Il token si rinnova automaticamente via refresh_token. Se scade definitivamente
(raro, solo se l'app viene revocata), rieseguire `oauth_flow.py`.
