#!/usr/bin/env python3
"""Generate OAuth2 auth URL for manual browser flow."""
import json

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDS_FILE = '/home/openclaw/.openclaw/workspace/projects/myAgenda/_credentials/oauth_client.json'

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

from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
print(auth_url)
