"""Test scrittura — aggiunge una riga di test, poi la rimuove."""
import sys
from datetime import datetime
sys.path.insert(0, "/home/openclaw/.openclaw/workspace/projects/google-sheets-tool")
from _system.sheets_client import SheetsClient

client = SheetsClient()

now = datetime.now().strftime("%Y-%m-%d %H:%M")
test_row = [now, "TEST_IACOPO", "riga di test — da rimuovere", "0"]

print(f"Aggiungendo riga di test: {test_row}")
result = client.append_rows("A:Z", [test_row])
print(f"OK: {result.get('updates', {}).get('updatedRange', 'n/a')}")
