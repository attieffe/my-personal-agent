import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SPREADSHEET_ID = "1PdJYvqA-23CiucnjwkJvQLXT1tQhQhPeuruUwlUP5fk"

BASE = "/home/openclaw/.openclaw/workspace/projects/google-sheets-tool"
TOKEN_FILE = f"{BASE}/_credentials/google_token.json"
CLIENT_FILE = f"{BASE}/_credentials/oauth_client.json"


class SheetsClient:
    def __init__(self, token_file=TOKEN_FILE, client_file=CLIENT_FILE, spreadsheet_id=SPREADSHEET_ID):
        self.token_file = token_file
        self.client_file = client_file
        self.spreadsheet_id = spreadsheet_id
        self.service = self._get_service()

    def _get_service(self):
        with open(self.token_file) as f:
            token_data = json.load(f)
        with open(self.client_file) as f:
            client_data = json.load(f)

        creds = Credentials(
            token=token_data["token"],
            refresh_token=token_data["refresh_token"],
            token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=client_data["client_id"],
            client_secret=client_data["client_secret"],
            scopes=token_data["scopes"],
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_data["token"] = creds.token
            with open(self.token_file, "w") as f:
                json.dump(token_data, f, indent=2)

        return build("sheets", "v4", credentials=creds)

    def list_sheets(self):
        meta = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
        return [s["properties"]["title"] for s in meta.get("sheets", [])]

    def get_metadata(self):
        return self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()

    def read_range(self, range_notation):
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_notation
        ).execute()
        return result.get("values", [])

    def write_range(self, range_notation, values):
        body = {"values": values}
        return self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=range_notation,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

    def append_rows(self, range_notation, values):
        body = {"values": values}
        return self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=range_notation,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()

    def clear_range(self, range_notation):
        return self.service.spreadsheets().values().clear(
            spreadsheetId=self.spreadsheet_id,
            range=range_notation
        ).execute()
