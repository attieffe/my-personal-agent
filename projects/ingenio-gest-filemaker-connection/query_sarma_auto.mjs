#!/usr/bin/env node
/**
 * Query: Cerca fatture di acquisto
 * Fornitore: Sarma | Categoria: auto | Anno: 2025
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
} catch (e) {
  console.error('❌ Errore lettura .env:', e.message);
  process.exit(1);
}

const BASE_URL = `https://${env.FM_HOST}:${env.FM_PORT}/fmi/data/v2`;
const agent = new https.Agent({ rejectUnauthorized: false });

async function fmLogin() {
  return new Promise((resolve, reject) => {
    const auth = Buffer.from(`${env.FM_USER}:${env.FM_PASSWORD}`).toString('base64');
    const url = new URL(`${BASE_URL}/databases/Fatture%20acq/sessions`);
    const req = https.request(url, {
      method: 'POST',
      agent,
      headers: { 'Authorization': `Basic ${auth}`, 'Content-Type': 'application/json', 'Content-Length': '0' }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          const token = json.response?.token;
          if (!token) {
            reject(new Error(`Autenticazione fallita: ${JSON.stringify(json)}`));
          } else {
            resolve(token);
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

async function searchRegistroAcquisti(token, query) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ query });
    const url = new URL(`${BASE_URL}/databases/Fatture%20acq/layouts/Registro%20acquisti/_find`);

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
          if (res.statusCode !== 200) {
            const errorMsg = json.messages?.[0]?.message || JSON.stringify(json);
            reject(new Error(`Status ${res.statusCode}: ${errorMsg}`));
          } else {
            resolve(json.response?.data || []);
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
    console.log('\n🔍 Ricerca fatture acquisto Sarma categoria auto 2025\n');

    const token = await fmLogin();
    console.log('✅ Autenticato\n');

    // Ricerca: Fornitore "Sarma", Categoria "auto", Data contiene "2025"
    const query = [
      {
        'Fornitore': 'Sarma',
        'Categoria': 'auto'
        // La data la filtramo dopo poiché FM potrebbe avere formati diversi
      }
    ];

    console.log('📝 Query:');
    console.log(`  • Fornitore: Sarma`);
    console.log(`  • Categoria: auto`);
    console.log(`  • Anno: 2025\n`);

    const records = await searchRegistroAcquisti(token, query);

    if (records.length === 0) {
      console.log('❌ Nessun record trovato');
      process.exit(0);
    }

    console.log(`✅ Trovati ${records.length} record:\n`);

    // Filtra per anno 2025 (in caso la data sia in formato italiano o altri)
    const filtered = records.filter(r => {
      const data = r.fieldData?.['Data'] || '';
      return data.includes('2025');
    });

    if (filtered.length === 0) {
      console.log('⚠️ Nessuno contiene "2025" nel campo Data.');
      console.log('Record trovati (senza filtro anno):\n');
      records.forEach((r, i) => {
        const d = r.fieldData;
        console.log(`${i+1}. Data: ${d['Data'] || 'N/A'} | Fornitore: ${d['Fornitore'] || 'N/A'} | Doc: ${d['Nr documento'] || 'N/A'} | Cat: ${d['Categoria'] || 'N/A'}`);
      });
    } else {
      console.log('📋 Risultati anno 2025:\n');
      filtered.forEach((r, i) => {
        const d = r.fieldData;
        console.log(`${i+1}. Data: ${d['Data'] || 'N/A'} | Fornitore: ${d['Fornitore'] || 'N/A'} | Doc: ${d['Nr documento'] || 'N/A'} | Cat: ${d['Categoria'] || 'N/A'}`);
        console.log(`   Imponibile: ${d['Imponibile import'] || 'N/A'} | IVA: ${d['IVA'] || 'N/A'}\n`);
      });
    }

    process.exit(0);

  } catch (err) {
    console.error('\n❌ ERRORE:', err.message);
    process.exit(1);
  }
})();
