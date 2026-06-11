#!/usr/bin/env node
/**
 * Test completo: crea fattura V_FAT_000 + riga Righe_Vendita
 * 1. Leggi un record esistente per capire la struttura
 * 2. Prova a creare una nuova fattura (NORMALE, non reverse charge)
 * 3. Crea la riga collegata
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
            console.log('✅ Autenticato su FM');
            resolve(json.response.token);
          } else {
            reject(new Error('Token non trovato: ' + JSON.stringify(json)));
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

// Leggi un record completo da V_FAT_000 per capire la struttura
async function readSampleFattura(token) {
  return new Promise((resolve, reject) => {
    const url = new URL(`${BASE_URL}/databases/DADEGEST/layouts/V_FAT_000/records?_limit=1`);
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
            console.log('📄 Record di esempio trovato');
            resolve(json.response.data[0]);
          } else {
            reject(new Error('Nessun record trovato'));
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

// Crea una nuova fattura
async function createFattura(token, data) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ fieldData: data });
    const url = new URL(`${BASE_URL}/databases/DADEGEST/layouts/V_FAT_000/records`);

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
        try {
          const json = JSON.parse(respData);
          if (json.response?.recordId) {
            console.log('✅ Fattura creata:', json.response.recordId);
            resolve(json.response.recordId);
          } else {
            const errorMsg = json.messages?.[0]?.message || JSON.stringify(json);
            reject(new Error(`Errore creazione fattura: ${errorMsg}`));
          }
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// Leggi una riga di esempio per capire la struttura
async function readSampleRiga(token) {
  return new Promise((resolve, reject) => {
    const url = new URL(`${BASE_URL}/databases/DADEGEST/layouts/Righe_Vendita/records?_limit=1`);
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
            console.log('📄 Riga di esempio trovata');
            resolve(json.response.data[0]);
          } else {
            reject(new Error('Nessuna riga trovata'));
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

// Crea riga in Righe_Vendita
async function createRigaVendita(token, idTesta, rigaData) {
  return new Promise((resolve, reject) => {
    const fieldData = { ...rigaData, IDTESTA: idTesta };
    const body = JSON.stringify({ fieldData });
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
        try {
          const json = JSON.parse(respData);
          if (json.response?.recordId) {
            console.log('✅ Riga creata:', json.response.recordId);
            resolve(json.response.recordId);
          } else {
            const errorMsg = json.messages?.[0]?.message || JSON.stringify(json);
            reject(new Error(`Errore creazione riga: ${errorMsg}`));
          }
        } catch (e) {
          reject(e);
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
    console.log('\n🔍 Test creazione fattura...\n');

    const token = await fmLogin();

    // Step 1: Leggi un record di esempio
    console.log('📥 Leggo record di esempio da V_FAT_000...');
    const sample = await readSampleFattura(token);

    // Analizza i campi con valore
    console.log('\n📋 Campi del record di esempio:\n');
    const fieldsWithValue = {};
    Object.entries(sample.fieldData).forEach(([key, val]) => {
      if (val && val !== '') {
        fieldsWithValue[key] = val;
        console.log(`  ✓ ${key}: ${typeof val === 'string' ? val.substring(0, 50) : val}`);
      }
    });

    // Step 2: Crea una fattura TEST semplice
    console.log('\n\n📝 Creo fattura di TEST (NORMALE)...\n');

    // Prova SOLO con campi scrivibili (evita Totale*, Tabella, percorso, IdTesta)
    const randNr = String(Math.floor(Math.random() * 10000) + 1000);
    const testFattura = {
      'Anno': new Date().getFullYear().toString(),
      'Nr': randNr,
      'Data': new Date().toLocaleDateString('it-IT'),
      'Cod Cliente': 'C00001', // Uso un cliente esistente dal sample
      'CAUSALE CONTABILE': 'Fattura di Vendita Test',
      'Cod Esenzione iva': '22',
      'Cod Pagamento': '007'
    };

    console.log('Campi inviati:');
    Object.entries(testFattura).forEach(([k, v]) => {
      console.log(`  • ${k}: ${v}`);
    });

    const fatturaNr = await createFattura(token, testFattura);

    // Step 2b: Leggi un riga di esempio per capire la struttura
    console.log('\n📥 Leggo riga di esempio da Righe_Vendita...');
    const sampleRiga = await readSampleRiga(token);

    console.log('\n📋 Campi della riga di esempio:\n');
    Object.entries(sampleRiga.fieldData).forEach(([key, val]) => {
      if (val && val !== '') {
        console.log(`  ✓ ${key}: ${typeof val === 'string' ? val.substring(0, 50) : val}`);
      }
    });

    // Step 3: Crea riga collegata
    console.log('\n\n📝 Creo riga in Righe_Vendita...\n');

    // Prova SOLO con campi veramente atomici (non calcolati)
    // Evita: Prezzo_Netto, imponibile, Iva, Totale riga, Data (auto), anno (auto), etc.
    const testRiga = {
      'CODICE_ARTICOLO': 'TESTPROD',
      'DESCRIZIONE': 'Prodotto di Test',
      'QTA': '1',
      'Prezzo': '100'
    };

    console.log('Campi riga (minimal):');
    Object.entries(testRiga).forEach(([k, v]) => {
      console.log(`  • ${k}: ${v}`);
    });

    const rigaNr = await createRigaVendita(token, fatturaNr, testRiga);

    console.log('\n\n✅ TEST COMPLETATO!\n');
    console.log(`  Fattura creata: recordId=${fatturaNr}`);
    console.log(`  Riga creata: recordId=${rigaNr} con IDTESTA=${fatturaNr}`);

    process.exit(0);

  } catch (err) {
    console.error('\n❌ ERRORE:', err.message);
    process.exit(1);
  }
})();
