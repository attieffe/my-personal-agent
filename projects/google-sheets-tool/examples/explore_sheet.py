"""
Script di esplorazione: elenca i fogli e mostra le prime righe di ciascuno.
Uso: python3 examples/explore_sheet.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _system.sheets_client import SheetsClient

client = SheetsClient()

print("=== FOGLI DISPONIBILI ===")
sheets = client.list_sheets()
for sheet_id, title in sheets:
    print(f"  [{sheet_id}] {title}")

print("\n=== PRIME RIGHE PER FOGLIO ===")
for sheet_id, title in sheets:
    print(f"\n--- {title} ---")
    rows = client.read_range(f"'{title}'!A1:Z5")
    for r in rows:
        print(r)
