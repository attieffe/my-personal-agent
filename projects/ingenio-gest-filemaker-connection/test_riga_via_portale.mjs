#!/usr/bin/env node
/**
 * Crea riga via PORTALE della fattura (invece che direttamente su Righe_Vendita)
 */

import https from 'https';
import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const env = {};
try {
  const envFile = readFileSync(join(__dirname, '.env'), 'utf-8');
  envFile.split('\n').forEach(line => {
    const [k, v] = line.split('=');
    if (k && v) env[k.trim()] = v.trim().replace(/^["']|["']$/g, '');
  });
} catch (e) {
  console.error('❌ .env non trovato');
  process.exit(1);
}

const FM_HOST = env.FM_HOST || 'localhost';
const FM_PORT = env.FM_PORT || '2296';
const FM_USER = env.FM_USER;
const FM_PASSWORD = env.FM_PASSWORD;

const BASE_URL = `https://${FM_HOST}:${FM_PORT}/fmi/data/v2`;
const agent = new https.Agent({ rejectUnauthorized: false });

async function fmLogin() {
  return new Promise((resolve, reject) => {
    const auth = Buffer.from(`${FM_USER}:${FM_PASSWORD}`).toString('base64');
    const url = new URL(`${BASE_URL}/databases/DADEGEST/sessions`);

    const req = https.request(url, {
      method: 'POST',
      agent,
      headers: {
        'Authorization': `Basic ${auth}`,
        'Content-Type': 'application/json',
        'Content-Length': '0'
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const json = JSON.parse(data);
        resolve(json.response?.token);
      });
    });
    req.on('error', reject);
    req.end();
  });
}

async function createRigaViaPortale(token, faturaRecordId, rigaData) {
  return new Promise((resolve, reject) => {
    const portalName = 'Righe Vendita Fatture';
    const body = JSON.stringify({ fieldData: rigaData });
    const url = new URL(`${BASE_URL}/databases/DADEGEST/layouts/V_FAT_000/records/${faturaRecordId}/${portalName}`);

    const req = https.request(url, {
      method: 'POST',
      agent,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body)
      }
    }, (res) => {
      let respData = '';
      res.on('data', chunk => respData += chunk);
      res.on('end', () => {
        // Debug: mostra status e prime 200 caratteri della risposta
        console.log(`Response status: ${res.statusCode}`);
        console.log(`Response headers:`, res.headers);
        console.log(`Response preview: ${respData.substring(0, 200)}`);

        try {
          const json = JSON.parse(respData);
          if (json.response?.recordId) {
            console.log('✅ Riga creata via portale:', json.response.recordId);
            resolve(json.response.recordId);
          } else {
            const errorMsg = json.messages?.[0]?.message || JSON.stringify(json);
            reject(new Error(`Errore: ${errorMsg}`));
          }
        } catch (e) {
          reject(new Error(`JSON parse error: ${e.message}. Full response: ${respData.substring(0, 500)}`));
        }
      });
    });

    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// Main
(async () => {
  try {
    console.log('\n🔍 Crea riga via PORTALE...\n');

    const token = await fmLogin();
    console.log('✅ Autenticato');

    const faturaRecordId = '10374';
    const rigaData = {
      'CODICE_ARTICOLO': 'DOMINIO.TEST',
      'DESCRIZIONE': 'Test Dominio',
      'QTA': '1',
      'Prezzo': '50'
    };

    console.log(`\n📝 Creo riga nella fattura ${faturaRecordId}...\n`);
    console.log('Dati:');
    Object.entries(rigaData).forEach(([k, v]) => {
      console.log(`  • ${k}: ${v}`);
    });

    const rigaId = await createRigaViaPortale(token, faturaRecordId, rigaData);

    console.log('\n✅ TEST COMPLETATO!');
    console.log(`   Fattura: ${faturaRecordId}`);
    console.log(`   Riga: ${rigaId}`);

    process.exit(0);

  } catch (err) {
    console.error('\n❌ ERRORE:', err.message);
    console.error(err.stack);
    process.exit(1);
  }
})();
