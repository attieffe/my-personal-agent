#!/usr/bin/env node
/**
 * Test: Crea un record nel Registro Acquisti (ciclo passivo)
 * Questo è il vero ciclo contabile per le fatture di acquisto
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

// Leggi un record di esempio
async function readSampleRegistroAcquisti(token) {
  return new Promise((resolve, reject) => {
    const url = new URL(`${BASE_URL}/databases/Fatture acq/layouts/Registro acquisti/records?_limit=1`);
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
          resolve(json.response?.data?.[0] || null);
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

// Crea un record nel Registro Acquisti
async function createRegistroAcquisti(token, data) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ fieldData: data });
    const url = new URL(`${BASE_URL}/databases/Fatture acq/layouts/Registro acquisti/records`);

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
            resolve(json.response.recordId);
          } else {
            const errorMsg = json.messages?.[0]?.message || JSON.stringify(json);
            reject(new Error(errorMsg));
          }
        } catch (e) {
          reject(new Error(`Parse error: ${respData.substring(0, 200)}`));
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
    console.log('\n🔍 Test Registro Acquisti (ciclo passivo)\n');

    const token = await fmLogin();
    console.log('✅ Autenticato\n');

    // Leggi un esempio
    console.log('📥 Leggo record di esempio...');
    const sample = await readSampleRegistroAcquisti(token);

    if (sample) {
      console.log('\n📋 Campi disponibili:\n');
      Object.entries(sample.fieldData).forEach(([k, v]) => {
        if (v && v !== '') {
          console.log(`  ✓ ${k}: ${String(v).substring(0, 50)}`);
        }
      });
    }

    // Crea un nuovo record
    console.log('\n\n📝 Creo nuovo registro acquisti test...\n');

    // Usa i campi del sample come guida
    const newRecord = {
      'Data': new Date().toLocaleDateString('it-IT'),
      'Fornitore': 'TEST FORNITORE SRL',
      'Nr documento': 'TEST-001',
      'Categoria': 'Servizi',
      'Imponibile import': '100',
      'Valore iva': '22',
      'IVA': '22'
    };

    console.log('Campi:');
    Object.entries(newRecord).forEach(([k, v]) => {
      console.log(`  • ${k}: ${v}`);
    });

    const recordId = await createRegistroAcquisti(token, newRecord);
    console.log(`\n✅ Record creato: ${recordId}`);

    process.exit(0);

  } catch (err) {
    console.error('\n❌ ERRORE:', err.message);
    process.exit(1);
  }
})();
