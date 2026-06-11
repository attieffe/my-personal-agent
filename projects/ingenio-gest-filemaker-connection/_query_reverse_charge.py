#!/usr/bin/env python3
"""
Query fatture acquisto da FileMaker DADEGEST.
Cerca reverse charge (codice IVA 22R) ed EXTRA UE.
"""

import os
import sys
import json
import ssl
import urllib.request
import base64
from urllib.error import URLError

# Carica credenziali da .env
env_file = os.path.join(os.path.dirname(__file__), '.env')
env_vars = {}
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env_vars[k.strip()] = v.strip().strip('"\'')

FM_HOST = env_vars.get('FM_HOST', 'localhost')
FM_PORT = env_vars.get('FM_PORT', '2296')
FM_USER = env_vars.get('FM_USER', '')
FM_PASSWORD = env_vars.get('FM_PASSWORD', '')

if not FM_USER or not FM_PASSWORD:
    print("❌ FM_USER o FM_PASSWORD mancanti in .env", file=sys.stderr)
    sys.exit(1)

BASE_URL = f"https://{FM_HOST}:{FM_PORT}/fmi/data/v2"

# Bypass SSL per self-signed
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def fm_login():
    """Autentica su FM e ritorna il bearer token."""
    url = f"{BASE_URL}/databases/DADEGEST/sessions"
    auth = base64.b64encode(f"{FM_USER}:{FM_PASSWORD}".encode()).decode()

    req = urllib.request.Request(
        url,
        method='POST',
        headers={'Authorization': f'Basic {auth}', 'Content-Length': '0'},
        data=b''
    )

    try:
        with urllib.request.urlopen(req, context=ssl_context) as resp:
            data = json.loads(resp.read())
            token = data['response']['token']
            print(f"✅ Autenticato su FM. Token: {token[:20]}...", file=sys.stderr)
            return token
    except URLError as e:
        print(f"❌ Connessione fallita: {e}", file=sys.stderr)
        sys.exit(1)

def fm_find(token, layout, query):
    """Esegui una ricerca FileMaker."""
    url = f"{BASE_URL}/databases/Fatture acq/layouts/{layout}/_find"
    body = json.dumps({'query': query}).encode()

    req = urllib.request.Request(
        url,
        method='POST',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        data=body
    )

    try:
        with urllib.request.urlopen(req, context=ssl_context) as resp:
            data = json.loads(resp.read())
            return data.get('response', {}).get('data', [])
    except URLError as e:
        print(f"❌ Query fallita: {e}", file=sys.stderr)
        return []

def fm_get_all(token, layout):
    """Recupera tutti i record da un layout (con limite)."""
    url = f"{BASE_URL}/databases/Fatture acq/layouts/{layout}/records?_limit=100"

    req = urllib.request.Request(
        url,
        method='GET',
        headers={'Authorization': f'Bearer {token}'}
    )

    try:
        with urllib.request.urlopen(req, context=ssl_context) as resp:
            data = json.loads(resp.read())
            return data.get('response', {}).get('data', [])
    except URLError as e:
        print(f"❌ GET fallita: {e}", file=sys.stderr)
        return []

def main():
    print("\n🔍 Cerco fatture acquisto con reverse charge o EXTRA UE...\n", file=sys.stderr)

    token = fm_login()

    # Primo: leggi TUTTI i record di Fatture Acq
    print("📥 Leggo fatture acquisto...", file=sys.stderr)
    fatture = fm_get_all(token, 'A_FAT_000')

    if not fatture:
        print("❌ Nessuna fattura trovata", file=sys.stderr)
        return

    print(f"📊 Totale fatture acquisto: {len(fatture)}", file=sys.stderr)

    # Secondo: per ogni fattura, leggi le righe acquisto
    results = []
    for fat in fatture:
        recordId = fat['id']
        fields = fat.get('fieldData', {})

        # Cerca righe di questa fattura con CodiceIva = 22R (reverse charge)
        # Vedi: il layout per le righe è accesibile da un portale in A_FAT_000
        # Alternativamente, query diretta il file righe vendita

        print(f"\n📄 Fattura Acq #{recordId}:", file=sys.stderr)
        print(f"   - Fornitore: {fields.get('Ragione Sociale Fornitore', 'N/A')}", file=sys.stderr)
        print(f"   - Data: {fields.get('Data', 'N/A')}", file=sys.stderr)
        print(f"   - Totale: {fields.get('Totale', 'N/A')}", file=sys.stderr)

        results.append({
            'recordId': recordId,
            'fornitore': fields.get('Ragione Sociale Fornitore'),
            'data': fields.get('Data'),
            'totale': fields.get('Totale'),
            'numero': fields.get('Nr'),
            'anno': fields.get('Anno'),
            'campi_debugprint': {k: v for k, v in fields.items() if 'iva' in k.lower() or 'nazione' in k.lower()}
        })

    # Output JSON per Atti
    print("\n" + "="*60)
    print("📋 RISULTATI FATTURE ACQUISTO", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
