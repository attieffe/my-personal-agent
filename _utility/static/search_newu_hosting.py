#!/usr/bin/env python3
"""
Cerca fatture NEWU 2025 con hosting/dominio.
Usa il portale Righe Vendita Fatture per estrarre dettagli riga.
"""

import os, json, ssl, urllib.request, base64
from pathlib import Path

# Load env
env = {}
for line in open(Path('/home/openclaw/.openclaw/workspace/.env')):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"\'')

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# Login
def fm_login():
    url = f"https://{env['FM_HOST']}:{env['FM_PORT']}/fmi/data/v2/databases/DADEGEST/sessions"
    req = urllib.request.Request(url, method='POST', headers={
        'Authorization': f'Basic {base64.b64encode(f"{env["FM_USER"]}:{env["FM_PASSWORD"]}".encode()).decode()}',
        'Content-Type': 'application/json'
    }, data=b'')
    with urllib.request.urlopen(req, context=ssl_ctx) as r:
        return json.load(r)['response']['token']

token = fm_login()
print(f"✅ Autenticato", flush=True)

# Ricerca: clienti NEWU, anno 2025
url = f"https://{env['FM_HOST']}:{env['FM_PORT']}/fmi/data/v2/databases/DADEGEST/layouts/V_FAT_000/_find"
body = json.dumps({'query': [{'Ragione Sociale': '*NEWU*'}, {'Anno': '2025'}]})
req = urllib.request.Request(url, method='POST', headers={
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}, data=body.encode())

with urllib.request.urlopen(req, context=ssl_ctx) as r:
    data = json.load(r)
    fatture_base = data['response']['data']

print(f"📥 Trovate {len(fatture_base)} fatture NEWU del 2025\n")

results = []

# Per ogni fattura, leggi il dettaglio dal GET per accedere al portale
for fat_base in fatture_base:
    recordId = fat_base['recordId']
    fields = fat_base['fieldData']

    url2 = f"https://{env['FM_HOST']}:{env['FM_PORT']}/fmi/data/v2/databases/DADEGEST/layouts/V_FAT_000/records/{recordId}"
    req2 = urllib.request.Request(url2, method='GET', headers={'Authorization': f'Bearer {token}'})

    with urllib.request.urlopen(req2, context=ssl_ctx) as r2:
        fat_detail = json.load(r2)['response']['data'][0]

    fattura = {
        'numero': fat_detail['fieldData'].get('Nr'),
        'data': fat_detail['fieldData'].get('Data'),
        'cliente': fat_detail['fieldData'].get('Ragione Sociale'),
        'totale_imponibile': fat_detail['fieldData'].get('Totale Imponibile'),
        'totale_iva': fat_detail['fieldData'].get('Totale Iva'),
        'totale': fat_detail['fieldData'].get('Totale'),
        'righe': []
    }

    # Estrai righe dal portale
    righe_portal = fat_detail.get('portalData', {}).get('Righe Vendita Fatture', [])

    has_hosting = False
    for riga in righe_portal:
        desc = riga.get('Righe Vendita Fatture::DESCRIZIONE', '').lower()
        qta = riga.get('Righe Vendita Fatture::QTA', '')
        prezzo_finale = riga.get('Righe Vendita Fatture::Prezzo f', '')
        imponibile = riga.get('Righe Vendita Fatture::imponibile', '')

        riga_data = {
            'descrizione': riga.get('Righe Vendita Fatture::DESCRIZIONE'),
            'codice': riga.get('Righe Vendita Fatture::CODICE_ARTICOLO'),
            'qta': qta,
            'um': riga.get('Righe Vendita Fatture::UM'),
            'prezzo_unitario': riga.get('Righe Vendita Fatture::Prezzo'),
            'prezzo_finale': prezzo_finale,
            'imponibile': imponibile,
            'iva': riga.get('Righe Vendita Fatture::Iva'),
            'totale_riga': riga.get('Righe Vendita Fatture::Totale riga')
        }

        fattura['righe'].append(riga_data)

        # Controlla se contiene hosting o dominio
        if 'hosting' in desc or 'dominio' in desc or 'dominii' in desc:
            has_hosting = True

    # Mostra fattura se contiene hosting
    if has_hosting or not righe_portal:
        print(f"📄 Fattura #{fattura['numero']} del {fattura['data']}")
        print(f"   Totale: €{fattura['totale']} (imponibile: €{fattura['totale_imponibile']}, IVA: €{fattura['totale_iva']})")
        print(f"   Righe:")

        for riga in fattura['righe']:
            desc = riga['descrizione'] or '(senza descrizione)'
            print(f"     • {desc}")
            if riga['qta']:
                print(f"       Qta: {riga['qta']} {riga.get('um', '')} | Prezzo: €{riga['prezzo_finale']} | Imponibile: €{riga['imponibile']}")

        results.append(fattura)
        print()

print(f"\n✅ Trovate {len(results)} fatture NEWU 2025 con hosting\n")
print(json.dumps(results, indent=2, ensure_ascii=False))
