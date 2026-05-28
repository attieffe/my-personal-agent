import sys
sys.path.insert(0, "/home/openclaw/.openclaw/workspace/projects/google-sheets-tool")
from _system.sheets_client import SheetsClient

client = SheetsClient()

print("=== Fogli disponibili ===")
for sheet in client.list_sheets():
    print(f"  - {sheet}")

print("\n=== Prime 10 righe del foglio principale ===")
rows = client.read_range("A1:Z10")
for i, row in enumerate(rows, 1):
    print(f"  [{i}] {row}")
