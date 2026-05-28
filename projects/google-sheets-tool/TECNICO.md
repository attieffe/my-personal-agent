# google-sheets-tool — TECNICO

## Scopo
Tool per leggere e scrivere il foglio Google Sheets "Lavori attilio" condiviso da Atti (`ralf00@gmail.com`) con `myjob@ingeniosolution.it`.

## Spreadsheet
- **Nome:** Lavori attilio
- **ID:** `1PdJYvqA-23CiucnjwkJvQLXT1tQhQhPeuruUwlUP5fk`
- **URL:** https://docs.google.com/spreadsheets/d/1PdJYvqA-23CiucnjwkJvQLXT1tQhQhPeuruUwlUP5fk/edit

## Autenticazione
- **Metodo:** OAuth2 (Installed App) — progetto Google Cloud `attibot`
- **Client ID:** `75976842589-493eej3rh5htvopn14cucimhsji3eb22.apps.googleusercontent.com`
- **Account:** `myjob@ingeniosolution.it`
- **Scopes:** `spreadsheets` (read+write) + `drive.readonly`
- **Token:** `_credentials/google_token.json` (access + refresh token)

## Struttura
```
_system/
  sheets_client.py    — classe SheetsClient (read/write/append/clear)
  oauth_flow.py       — script OAuth una-tantum (richiede browser)
_credentials/
  oauth_client.json   — client_id + client_secret (dal progetto GCP attibot)
  google_token.json   — token attivo (da generare con oauth_flow.py)
examples/
  read_sheet.py       — legge fogli + prime 10 righe
  write_test.py       — aggiunge riga di test
docs/
  STRUTTURA_FOGLIO.md — documentazione dei fogli e colonne (da aggiornare dopo primo accesso)
```

## Setup iniziale
1. Abilitare **Google Sheets API** e **Google Drive API** su Google Cloud Console (progetto `attibot`)
2. Verificare che `myjob@ingeniosolution.it` sia in lista utenti di test (OAuth consent screen)
3. Eseguire `python3 _system/oauth_flow.py` e autorizzare dal browser
4. Testare con `python3 examples/read_sheet.py`

## Dipendenze Python
```
google-auth
google-auth-oauthlib
google-api-python-client
```
Verifica: `pip3 list | grep google`

## Uso
```python
from _system.sheets_client import SheetsClient

client = SheetsClient()
fogli = client.list_sheets()
righe = client.read_range("FoglioX!A1:Z100")
client.append_rows("FoglioX!A:Z", [["val1", "val2", "val3"]])
```
