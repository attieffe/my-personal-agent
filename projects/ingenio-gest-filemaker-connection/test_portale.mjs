#!/usr/bin/env node
/**
 * Test: leggi la fattura appena creata e vedi se il portale "Righe Vendita" è accessible
 */

import https from 'https';
import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Leggi .env
const env = {};
try {
  const envFile = readFileSync(join(__dirname, '.env'), 'utf-8');
  envFile.split('\n').forEach(line => {
    const [k, v] = line.split('=');
    if (k && v) env[k.trim()] = v.trim().replace(/^["']|["']$/g, '');
  });
} catch (e) {
  console.error('❌ .env non trovato:', e.message);
  process.exit(1);
}

const FM_HOST = env.FM_HOST || 'localhost';
const FM_PORT = env.FM_PORT || '2296';
const FM_USER = env.FM_USER;
const FM_PASSWORD = env.FM_PASSWORD;

if (!FM_USER || !FM_PASSWORD) {
  console.error('❌ FM_USER o FM_PASSWORD mancanti');
  process.exit(1);
}

const BASE_URL = `https://${FM_HOST}:${FM_PORT}/fmi/data/v2`;
const agent = new https.Agent({ rejectUnauthorized: false });

// Login
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
        try {
          const json = JSON.parse(data);
          if (json.response?.token) {
            resolve(json.response.token);
          } else {
            reject(new Error('Token non trovato'));
          }
        } catch (e) {
          reject(e);
        }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

// Leggi fattura con portale
async function readFatturaWithPortal(token, recordId) {
  return new Promise((resolve, reject) => {
    const url = new URL(`${BASE_URL}/databases/DADEGEST/layouts/V_FAT_000/records/${recordId}`);

    const req = https.request(url, {
      method: 'GET',
      agent,
      headers: { 'Authorization': `Bearer ${token}` }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          if (json.response?.data?.[0]) {
            resolve(json.response.data[0]);
          } else {
            reject(new Error('Record non trovato'));
          }
        } catch (e) {
          reject(e);
        }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

// Main
(async () => {
  try {
    console.log('\n🔍 Test lettura portale Righe Vendita...\n');

    const token = await fmLogin();
    console.log('✅ Autenticato');

    // Usa la fattura 10374 creata prima
    const recordId = '10374';
    console.log(`📥 Leggo fattura ${recordId} con portale...\n`);

    const fattura = await readFatturaWithPortal(token, recordId);

    console.log('📋 Struttura risposta:');
    console.log('  Chiavi top-level:');
    Object.keys(fattura).forEach(k => console.log(`    - ${k}`));

    if (fattura.portalData) {
      console.log('\n📊 portalData disponibile:');
      Object.keys(fattura.portalData).forEach(portalName => {
        const portalRecords = fattura.portalData[portalName];
        console.log(`  Portal: "${portalName}" (${portalRecords.length} record)`);
        if (portalRecords.length > 0) {
          console.log(`    Primo record:`, portalRecords[0].fieldData);
        }
      });
    } else {
      console.log('\n⚠️ portalData non trovato');
    }

    process.exit(0);

  } catch (err) {
    console.error('\n❌ ERRORE:', err.message);
    process.exit(1);
  }
})();
