from google_auth_oauthlib.flow import InstalledAppFlow
import json, os

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDS_FILE = '/home/openclaw/.openclaw/workspace/projects/myAgenda/_credentials/oauth_client.json'
TOKEN_FILE = '/home/openclaw/.openclaw/workspace/projects/myAgenda/_credentials/google_token.json'

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
print(f"AUTH URL: {auth_url}")

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
    "calendar_id": "07a5eeed6b895609bd39fd703368155e5c4f81f59ab7952c21677fcfcb548108@group.calendar.google.com"
}

with open(TOKEN_FILE, "w") as f:
    json.dump(token_data, f, indent=2)
print(f"Token salvato in {TOKEN_FILE}")
print(f"refresh_token: {creds.refresh_token}")
