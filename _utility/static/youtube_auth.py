#!/usr/bin/env python3
"""One-time OAuth2 flow for YouTube Data API v3. Saves token to youtube_token.json."""
import os, json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
SECRET = os.path.expanduser(
    "~/.openclaw/workspace/projects/myJob/PERSONALE/tempo_libero/youtube_client_secret.json"
)
TOKEN = os.path.expanduser(
    "~/.openclaw/workspace/projects/myJob/PERSONALE/tempo_libero/youtube_token.json"
)

flow = InstalledAppFlow.from_client_secrets_file(SECRET, SCOPES)
creds = flow.run_local_server(port=8765, open_browser=False)

with open(TOKEN, "w") as f:
    f.write(creds.to_json())
print("Token salvato in:", TOKEN)
