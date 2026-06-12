#!/usr/bin/env python3
"""
Query fatture vendita da FileMaker DADEGEST per cliente specifico.
Cerca per cliente, anno, e filtra per parole chiave nella descrizione righe.

Uso:
  python query_fatture_cliente.py --cliente "NEWU" --anno 2025 --keyword "hosting"
  python query_fatture_cliente.py --cliente "CEAM" --anno 2026
"""

import os
import sys
import json
import ssl
import urllib.request
import urllib.parse
import base64
import argparse
from urllib.error import URLError
from pathlib import Path

# Carica credenziali da .env (cerca dal progetto ingenio-gest-filemaker-connection)
def load_env():
    """Carica variabili da .env in workspace root."""
    env_file = Path(__file__).parent.parent.parent / '.env'
    env_vars = {}
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env_vars[k.strip()] = v.strip().strip('"\'')
    return env_vars

ENV = load_env()
FM_HOST = ENV.get('FM_HOST', 'localhost')
FM_PORT = ENV.get('FM_PORT', '2296')
FM_USER = ENV.get('FM_USER', '')
FM_PASSWORD = ENV.get('FM_PASSWORD', '')

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
        headers={'Authorization': f'Basic {auth}', 'Content-Length': '0', 'Content-Type': 'application/json'},
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
    """Esegui una ricerca FileMaker sulla tabella fatture."""
    url = f"{BASE_URL}/databases/DADEGEST/layouts/{layout}/_find"
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

def fm_get_record(token, recordId):
    """Recupera il dettaglio completo di una fattura con portale righe."""
    url = f"{BASE_URL}/databases/DADEGEST/layouts/V_FAT_000/records/{recordId}"

    req = urllib.request.Request(
        url,
        method='GET',
        headers={'Authorization': f'Bearer {token}'}
    )

    try:
        with urllib.request.urlopen(req, context=ssl_context) as resp:
            data = json.loads(resp.read())
            return data.get('response', {}).get('data', [{}])[0]
    except URLError as e:
        print(f"❌ GET record fallita: {e}", file=sys.stderr)
        return {}

def fm_find_righe_by_idtesta(token, idtesta):
    """Cerca righe vendita per IDTESTA (numero fattura testata)."""
    # Le righe vivono nel file "righe vendita", non in DADEGEST
    # URL-encode il nome del database (con spazio)
    db_encoded = urllib.parse.quote('righe vendita', safe='')
    layout_encoded = urllib.parse.quote('Righe_Vendita', safe='')
    url = f"{BASE_URL}/databases/{db_encoded}/layouts/{layout_encoded}/_find"
    body = json.dumps({'query': [{'IDTESTA': str(idtesta)}]}).encode()

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
        print(f"⚠️  Query righe fallita per IDTESTA {idtesta}: {e}", file=sys.stderr)
        return []

def main():
    parser = argparse.ArgumentParser(description='Cerca fatture vendita FileMaker per cliente')
    parser.add_argument('--cliente', type=str, required=True, help='Nome/Codice cliente (es. NEWU)')
    parser.add_argument('--anno', type=int, required=True, help='Anno (es. 2025)')
    parser.add_argument('--keyword', type=str, default='', help='Filtra righe per parola chiave (es. hosting)')

    args = parser.parse_args()

    print(f"\n🔍 Cerco fatture per cliente '{args.cliente}' anno {args.anno}...\n", file=sys.stderr)
    if args.keyword:
        print(f"   Filtro: righe contengono '{args.keyword}'", file=sys.stderr)

    token = fm_login()

    # Ricerca per cliente (wildcard) e anno
    query = [
        {'Ragione Sociale': f"*{args.cliente}*"},
        {'Anno': str(args.anno)}
    ]

    print(f"📥 Ricerca in V_FAT_000...", file=sys.stderr)
    fatture = fm_find(token, 'V_FAT_000', query)

    if not fatture:
        print(f"❌ Nessuna fattura trovata per '{args.cliente}' / {args.anno}", file=sys.stderr)
        return

    print(f"📊 Trovate {len(fatture)} fatture", file=sys.stderr)

    # Per ogni fattura, leggi il dettaglio con righe
    results = []
    for fat in fatture:
        recordId = fat.get('recordId') or fat.get('id')
        fields = fat.get('fieldData', {})

        # Leggi il record completo per accedere ai dati testata e IDTESTA
        detail = fm_get_record(token, recordId)
        detail_fields = detail.get('fieldData', {})

        # Cerca righe dalla tabella Righe_Vendita usando IDTESTA
        idtesta = detail_fields.get('IDTESTA') or detail_fields.get('Nr')
        righe_db = fm_find_righe_by_idtesta(token, str(idtesta)) if idtesta else []

        print(f"\n📄 Fattura #{detail_fields.get('Nr', '?')} del {detail_fields.get('Data', '?')}", file=sys.stderr)
        print(f"   Cliente: {detail_fields.get('Ragione Sociale', '?')}", file=sys.stderr)
        print(f"   Totale: €{detail_fields.get('Totale', '0')}", file=sys.stderr)
        print(f"   Righe DB: {len(righe_db)}", file=sys.stderr)

        # Estrai righe dai dati del database
        righe = []
        for riga in righe_db:
            riga_fields = riga.get('fieldData', {})
            righe.append({
                'codice_articolo': riga_fields.get('CODICE_ARTICOLO'),
                'descrizione': riga_fields.get('DESCRIZIONE'),
                'qta': riga_fields.get('QTA'),
                'um': riga_fields.get('UM'),
                'prezzo_unitario': riga_fields.get('Prezzo'),
                'prezzo_netto': riga_fields.get('Prezzo_Netto'),
                'prezzo_finale': riga_fields.get('Prezzo f'),
                'imponibile': riga_fields.get('imponibile'),
                'codice_iva': riga_fields.get('Codice Iva f'),
                'aliquota_iva': riga_fields.get('Aliquota Iva'),
                'iva': riga_fields.get('Iva'),
                'totale_riga': riga_fields.get('Totale riga')
            })

        # Filtra righe se keyword specificato
        righe_filtrate = righe
        if args.keyword:
            righe_filtrate = [
                r for r in righe
                if args.keyword.lower() in (r.get('descrizione') or '').lower()
            ]
            if not righe_filtrate:
                print(f"   ⚠️  Nessuna riga contiene '{args.keyword}'", file=sys.stderr)
                continue

        # Estrai dati fattura
        fattura_data = {
            'numero': detail_fields.get('Nr'),
            'anno': detail_fields.get('Anno'),
            'data': detail_fields.get('Data'),
            'cliente': detail_fields.get('Ragione Sociale'),
            'totale_imponibile': detail_fields.get('Totale Imponibile'),
            'totale_iva': detail_fields.get('Totale Iva'),
            'totale': detail_fields.get('Totale'),
            'stato': detail_fields.get('Stato'),
            'righe': righe_filtrate
        }

        results.append(fattura_data)

    # Output JSON
    print("\n" + "="*70)
    print("📋 FATTURE TROVATE", file=sys.stderr)
    print("="*70, file=sys.stderr)
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
