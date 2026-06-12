# Google Sheets API — Piano Infrastruttura

**Data:** 2026-05-28  
**Contesto:** Atti ha condiviso il foglio "Lavori attilio" con `myjob@ingeniosolution.it`  
**Spreadsheet ID:** `1PdJYvqA-23CiucnjwkJvQLXT1tQhQhPeuruUwlUP5fk`

---

## Cosa esiste già ✅

| Elemento | Stato | Dettaglio |
|---|---|---|
| Progetto Google Cloud | ✅ Esiste | `attibot` — già usato per Google Calendar |
| Client OAuth2 (Installed App) | ✅ Esiste | `client_id`: `75976842589-493eej3r...` |
| File `client_secret` | ✅ Consegnato | `/home/openclaw/.openclaw/media/inbound/client_secret_75976842589_...json` |
| Account `myjob@ingeniosolution.it` | ✅ Configurato | credenziali in `projects/myAgenda/_credentials/.google_account.env` |
| Librerie Python | ✅ Installate | `google-auth`, `google-api-python-client`, `google-auth-oauthlib` |
| OAuth flow scripts | ✅ Presenti | `oauth_flow.py`, `get_auth_url.py` in `projects/myAgenda/_credentials/` |
| Token Google Calendar | ⚠️ Mancante | `google_token.json` non trovato — l'OAuth flow per Calendar non è stato completato |
| Scope Sheets sull'OAuth app | ❌ Da aggiungere | Attualmente solo `calendar` scope — bisogna aggiungere `spreadsheets` |

---

## Cosa NON bisogna fare (semplificazioni)

- **NON serve creare un nuovo progetto Google Cloud** — `attibot` è già lì
- **NON serve un Service Account** — OAuth2 con `myjob@ingeniosolution.it` è più semplice e già impostato per Calendar; estendere gli scope è il percorso minimo
- **NON serve una nuova app Google Cloud** — stessa app, scope aggiuntivi

---

## Piano Step-by-Step

### FASE 1 — Abilitare Google Sheets API su Google Cloud (manuale con Atti)

**Dove:** [console.cloud.google.com](https://console.cloud.google.com) → progetto `attibot`

1. Vai su **"API e servizi" → "Libreria"**
2. Cerca **"Google Sheets API"** → Abilita
3. Cerca **"Google Drive API"** → Abilita (necessario per listing/metadata)
4. In **"Credenziali"** verifica che l'OAuth Client ID `75976842589-...` sia ancora attivo

> **Nota:** Se il progetto è in stato "Testing" (non pubblicato), `myjob@ingeniosolution.it` deve essere nella lista degli utenti di test. Vai su **"Schermata consenso OAuth" → "Utenti di test"** e aggiungi `myjob@ingeniosolution.it` se non c'è già.

---

### FASE 2 — Creare struttura cartella progetto

```
projects/google-sheets-tool/
├── _system/
│   ├── FLOW.md              ← come funziona il tool
│   ├── sheets_client.py     ← classe Python riutilizzabile (read/write)
│   ├── auth.py              ← gestione token OAuth (condivide con myAgenda)
│   └── oauth_flow.py        ← re-autorizzazione manuale (scope Sheets)
├── _credentials/
│   ├── oauth_client.json    ← client_id + client_secret (da client_secret file)
│   └── google_token.json    ← token attivo (access + refresh, scope Sheets)
├── examples/
│   ├── read_sheet.py        ← esempio lettura
│   └── write_sheet.py       ← esempio scrittura
├── TECNICO.md
├── TODO.md
└── CHANGELOG.md
```

> **Decisione architetturale:** Le credenziali Sheets stanno in `google-sheets-tool/_credentials/` separato da myAgenda per chiarezza di scope. Il `oauth_client.json` è lo stesso client app `attibot`, ma il `google_token.json` avrà scope diversi.

---

### FASE 3 — Setup credenziali (semi-automatico)

```bash
# 1. Copia client_secret nella cartella progetto
cp "/home/openclaw/.openclaw/media/inbound/client_secret_75976842589_*.json" \
   /home/openclaw/.openclaw/workspace/projects/google-sheets-tool/_credentials/oauth_client_raw.json

# 2. Estrai client_id e client_secret in formato semplice
python3 -c "
import json
with open('_credentials/oauth_client_raw.json') as f:
    d = json.load(f)['installed']
out = {'client_id': d['client_id'], 'client_secret': d['client_secret']}
with open('_credentials/oauth_client.json', 'w') as f:
    json.dump(out, f, indent=2)
print('OK:', out['client_id'][:30])
"
```

---

### FASE 4 — OAuth flow per ottenere token con scope Sheets

Lo script `oauth_flow.py` da creare userà **scope combinati**:

```python
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',   # read + write Sheets
    'https://www.googleapis.com/auth/drive.readonly',  # per accesso al file condiviso
]
```

**Flow manuale (una tantum con Atti):**

1. Eseguire `python3 oauth_flow.py` da terminale
2. Aprire l'URL nel browser **loggato come `myjob@ingeniosolution.it`**
3. Autorizzare le permission richieste
4. Incollare il codice → token salvato automaticamente in `google_token.json`
5. Verifica: `python3 examples/read_sheet.py` → deve mostrare le prime righe del foglio

---

### FASE 5 — Script Python base

#### `_system/sheets_client.py` (classe riutilizzabile)

```python
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json

SPREADSHEET_ID = "1PdJYvqA-23CiucnjwkJvQLXT1tQhQhPeuruUwlUP5fk"

class SheetsClient:
    def __init__(self, token_file, client_file):
        self.token_file = token_file
        self.client_file = client_file
        self.service = self._get_service()

    def _get_service(self):
        with open(self.token_file) as f:
            token_data = json.load(f)
        with open(self.client_file) as f:
            client_data = json.load(f)

        creds = Credentials(
            token=token_data['token'],
            refresh_token=token_data['refresh_token'],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_data['client_id'],
            client_secret=client_data['client_secret'],
            scopes=token_data['scopes'],
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_data['token'] = creds.token
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f, indent=2)

        return build('sheets', 'v4', credentials=creds)

    def read_range(self, range_notation):
        result = self.service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=range_notation
        ).execute()
        return result.get('values', [])

    def write_range(self, range_notation, values):
        body = {'values': values}
        result = self.service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_notation,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        return result

    def append_rows(self, range_notation, values):
        body = {'values': values}
        result = self.service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=range_notation,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        return result
```

#### `examples/read_sheet.py`

```python
from _system.sheets_client import SheetsClient

client = SheetsClient(
    token_file='_credentials/google_token.json',
    client_file='_credentials/oauth_client.json'
)
rows = client.read_range('Sheet1!A1:Z10')
for row in rows:
    print(row)
```

#### `examples/write_sheet.py`

```python
from _system.sheets_client import SheetsClient

client = SheetsClient(
    token_file='_credentials/google_token.json',
    client_file='_credentials/oauth_client.json'
)
# Aggiunge una riga
client.append_rows('Sheet1!A:Z', [['2026-05-28', 'Test scrittura', '100']])
print("Riga aggiunta")
```

---

## Azioni che richiedono Atti (interazione manuale)

| # | Azione | Dove | Tempo stimato |
|---|---|---|---|
| 1 | Abilitare Google Sheets API su `attibot` | Google Cloud Console | 2 min |
| 2 | Abilitare Google Drive API su `attibot` | Google Cloud Console | 1 min |
| 3 | Verificare che `myjob@ingeniosolution.it` sia tra gli utenti di test | OAuth Consent Screen | 1 min |
| 4 | Eseguire OAuth flow e autorizzare dal browser `myjob` | Terminale + browser | 3 min |

---

## Azioni che può fare IAcopo in autonomia

- [ ] Creare struttura cartella `projects/google-sheets-tool/`
- [ ] Copiare e normalizzare `oauth_client.json` dalle credenziali esistenti
- [ ] Scrivere `oauth_flow.py` con scope Sheets
- [ ] Scrivere `sheets_client.py` e script di esempio
- [ ] Testare la lettura dopo che Atti completa il flow OAuth

---

## Note importanti

- **`myjob@ingeniosolution.it` è un account Google Workspace** — account Google completo, NON solo IMAP. Atti ha condiviso il foglio direttamente con questo account. Il flusso OAuth2 si autentica come `myjob@ingeniosolution.it` — metodo corretto e sufficiente, nessun Service Account necessario.
- **Se l'app OAuth è in modalità "testing":** aggiungere `myjob@ingeniosolution.it` come utente di test nella Schermata Consenso. Gli account Google Workspace standard sono trattati come normali account Google in questo contesto.
- **Il foglio "Lavori attilio" è già condiviso** — non serve ulteriore configurazione lato Drive
- **Spreadsheet ID:** `1PdJYvqA-23CiucnjwkJvQLXT1tQhQhPeuruUwlUP5fk`
- **Riutilizzo infra esistente:** stessa app OAuth `attibot`, stesso pattern di myAgenda — zero nuovi setup su GCP

---

*Piano generato da IAcopo subagent — 2026-05-28*
