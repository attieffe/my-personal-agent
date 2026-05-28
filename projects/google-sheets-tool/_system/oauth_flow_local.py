"""
OAuth flow con server locale su porta 8085.
Stampa l'URL, aspetta il redirect di Google, salva il token.
"""
import json
import threading
import webbrowser
from wsgiref.simple_server import make_server, WSGIRequestHandler
from urllib.parse import urlparse, parse_qs
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
        "redirect_uris": ["http://localhost:8085/"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
flow.redirect_uri = "http://localhost:8085/"

auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

print("\n=== Google Sheets OAuth Flow ===")
print(f"\nApri questo URL nel browser (loggato come myjob@ingeniosolution.it):\n\n{auth_url}\n")
print("In attesa del redirect su http://localhost:8085/ ...\n")

# Server minimo per catturare il callback
code_holder = {}

class SilentHandler(WSGIRequestHandler):
    def log_message(self, *args):
        pass

def app(environ, start_response):
    qs = parse_qs(urlparse(environ.get("PATH_INFO", "") + "?" + (environ.get("QUERY_STRING") or "")).query)
    code = qs.get("code", [None])[0]
    if code:
        code_holder["code"] = code
        start_response("200 OK", [("Content-Type", "text/html")])
        return [b"<h1>Autorizzazione completata! Puoi chiudere questa finestra.</h1>"]
    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"Attesa codice..."]

httpd = make_server("localhost", 8085, app, handler_class=SilentHandler)
httpd.handle_request()  # blocca finché non arriva una richiesta

code = code_holder.get("code")
if not code:
    print("Nessun codice ricevuto.")
    exit(1)

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

print(f"Token salvato in: {TOKEN_FILE}")
print(f"refresh_token: {creds.refresh_token[:20]}...")
