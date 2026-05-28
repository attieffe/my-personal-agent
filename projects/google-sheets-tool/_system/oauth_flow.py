"""
OAuth flow una-tantum per ottenere token con scope Google Sheets.
Eseguire manualmente: python3 _system/oauth_flow.py
Richiede: browser aperto su myjob@ingeniosolution.it
"""
import json
import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]

BASE = "/home/openclaw/.openclaw/workspace/projects/google-sheets-tool"
CLIENT_FILE = f"{BASE}/_credentials/oauth_client.json"
TOKEN_FILE = f"{BASE}/_credentials/google_token.json"

with open(CLIENT_FILE) as f:
    client_data = json.load(f)

CLIENT_CONFIG = {
    "installed": {
        "client_id": client_data["client_id"],
        "client_secret": client_data["client_secret"],
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

print("\n=== Google Sheets OAuth Flow ===")
print(f"\nApri questo URL nel browser loggato come myjob@ingeniosolution.it:\n\n{auth_url}\n")

code = input("Incolla il codice di autorizzazione: ").strip()
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

print(f"\nToken salvato in: {TOKEN_FILE}")
print(f"refresh_token: {creds.refresh_token[:20]}...")
