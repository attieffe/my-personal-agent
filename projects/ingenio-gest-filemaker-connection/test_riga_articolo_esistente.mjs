#!/usr/bin/env node
/**
 * Crea riga usando un articolo ESISTENTE (non creando un nuovo articolo)
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

// Prova con solo ID_ARTICOLO (lookup)
async function createRigaWithArticolo(token, idTesta) {
  return new Promise((resolve, reject) => {
    // Usa articolo ESISTENTE dal sample: SER.S.002
    const rigaData = {
      'ID_ARTICOLO': 'SER.S.002',
      'QTA': '2'
    };

    const body = JSON.stringify({
      fieldData: { ...rigaData, IDTESTA: idTesta }
    });

    const url = new URL(`${BASE_URL}/databases/DADEGEST/layouts/Righe_Vendita/records`);

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
        console.log(`Status: ${res.statusCode}`);
        console.log(`Preview: ${respData.substring(0, 300)}`);

        try {
          const json = JSON.parse(respData);
          if (json.response?.recordId) {
            console.log('✅ Riga creata:', json.response.recordId);
            resolve(json.response.recordId);
          } else {
            const errorMsg = json.messages?.[0]?.message || JSON.stringify(json);
            reject(new Error(`Errore: ${errorMsg}`));
          }
        } catch (e) {
          reject(new Error(`Parse error: ${e.message}`));
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
    console.log('\n🔍 Test: riga con articolo ESISTENTE...\n');

    const token = await fmLogin();
    console.log('✅ Autenticato\n');

    const idTesta = '10374';
    console.log(`Creo riga in fattura ${idTesta} con articolo SER.S.002...\n`);

    const rigaId = await createRigaWithArticolo(token, idTesta);

    console.log('\n✅ SUCCESSO!');
    process.exit(0);

  } catch (err) {
    console.error('\n❌ ERRORE:', err.message);
    process.exit(1);
  }
})();
