"""
OAuth2 flow per Google Sheets + Drive.
Eseguire una volta sola (o quando il token scade e non si rinnova).
Richiede browser loggato come myjob@ingeniosolution.it.

Uso: python3 _system/oauth_flow.py
"""
from google_auth_oauthlib.flow import InstalledAppFlow
import json, os

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.readonly',
]

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDS_FILE = os.path.join(BASE, '_credentials', 'oauth_client.json')
TOKEN_FILE = os.path.join(BASE, '_credentials', 'google_token.json')

with open(CREDS_FILE) as f:
    client_data = json.load(f)

CLIENT_CONFIG = {
    "installed": {
        "client_id": client_data["client_id"],
        "client_secret": client_data["client_secret"],
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
}

flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')

print("\n=== GOOGLE SHEETS OAUTH FLOW ===")
print("1. Apri questo URL nel browser loggato come myjob@ingeniosolution.it:")
print(f"\n{auth_url}\n")
print("2. Autorizza le permission richieste")
print("3. Copia il codice che appare e incollalo qui sotto\n")

code = input("Inserisci il codice: ").strip()
flow.fetch_token(code=code)
creds = flow.credentials

token_data = {
    "token": creds.token,
    "refresh_token": creds.refresh_token,
    "token_uri": creds.token_uri,
    "client_id": creds.client_id,
    "client_secret": creds.client_secret,
    "scopes": list(creds.scopes),
}

with open(TOKEN_FILE, "w") as f:
    json.dump(token_data, f, indent=2)

print(f"\nToken salvato in {TOKEN_FILE}")
print("Setup completato. Ora puoi usare sheets_client.py.")
