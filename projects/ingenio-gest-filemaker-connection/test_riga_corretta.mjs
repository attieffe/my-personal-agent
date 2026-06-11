#!/usr/bin/env node
/**
 * Crea riga in R_FAT_000 CON i campi CORRETTI
 * Senza CODICE_ARTICOLO e ID_ARTICOLO
 */

import https from 'https';
import { readFileSync } from 'fs';

const env = {};
try {
  const envFile = readFileSync('/home/openclaw/.openclaw/workspace/projects/ingenio-gest-filemaker-connection/.env', 'utf-8');
  envFile.split('\n').forEach(line => {
    const [k, v] = line.split('=');
    if (k && v) env[k.trim()] = v.trim().replace(/^["']|["']$/g, '');
  });
} catch (e) { process.exit(1); }

const BASE_URL = `https://${env.FM_HOST}:${env.FM_PORT}/fmi/data/v2`;
const agent = new https.Agent({ rejectUnauthorized: false });

async function fmLogin() {
  return new Promise((resolve, reject) => {
    const auth = Buffer.from(`${env.FM_USER}:${env.FM_PASSWORD}`).toString('base64');
    const url = new URL(`${BASE_URL}/databases/DADEGEST/sessions`);
    const req = https.request(url, {
      method: 'POST',
      agent,
      headers: { 'Authorization': `Basic ${auth}`, 'Content-Type': 'application/json', 'Content-Length': '0' }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(JSON.parse(data).response?.token));
    });
    req.on('error', reject);
    req.end();
  });
}

async function createRiga(token, idTesta) {
  return new Promise((resolve, reject) => {
    // MINIMALISTA: solo campi veramente atomici
    const rigaData = {
      'IDTESTA': idTesta,
      'DESCRIZIONE': 'Servizio test minimalista',
      'QTA': '1',
      'Prezzo': '50'
    };

    const body = JSON.stringify({ fieldData: rigaData });
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
        try {
          const json = JSON.parse(respData);
          if (json.response?.recordId) {
            console.log('✅ Riga creata:', json.response.recordId);
            resolve(json.response.recordId);
          } else {
            const errorMsg = json.messages?.[0]?.message || JSON.stringify(json);
            reject(new Error(errorMsg));
          }
        } catch (e) {
          reject(new Error(`Parse: ${respData.substring(0, 200)}`));
        }
      });
    });

    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

(async () => {
  try {
    console.log('\n🔍 Test riga R_FAT_000 (campi corretti)\n');

    const token = await fmLogin();
    console.log('✅ Autenticato\n');

    const idTesta = 'FA10338'; // IdTesta ESISTENTE nel database
    console.log(`Creo riga in fattura ${idTesta}...\n`);
    console.log('Campi (minimalisti):');
    console.log('  • IDTESTA: FA10338');
    console.log('  • DESCRIZIONE: Servizio test minimalista');
    console.log('  • QTA: 1');
    console.log('  • Prezzo: 50\n');

    const rigaId = await createRiga(token, idTesta);

    console.log(`\n✅ SUCCESSO!`);
    console.log(`   Riga creata: ${rigaId}`);

    process.exit(0);

  } catch (err) {
    console.error('\n❌ ERRORE:', err.message);
    process.exit(1);
  }
})();
