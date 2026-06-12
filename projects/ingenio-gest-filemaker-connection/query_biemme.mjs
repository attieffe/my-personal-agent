#!/usr/bin/env node
import https from 'https';
import { readFileSync } from 'fs';

const env = {};
try {
  const envFile = readFileSync('.env', 'utf-8');
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
          resolve(json.response?.token);
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

async function search(token, query) {
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
          resolve(json.response?.data || []);
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

(async () => {
  try {
    console.log('🔍 Ricerca: Biemme Motori categoria auto\n');
    const token = await fmLogin();
    const records = await search(token, [{ 'Fornitore': 'Biemme Motori', 'Categoria': 'auto' }]);
    
    if (records.length === 0) {
      console.log('❌ Nessun record trovato');
    } else {
      records.forEach((r, i) => {
        const d = r.fieldData;
        console.log(`${i+1}. Data: ${d['Data']} | Doc: ${d['Nr documento']} | Fornitore: ${d['Fornitore']} | Categoria: ${d['Categoria']}`);
      });
    }
    process.exit(0);
  } catch (err) {
    console.error('❌', err.message);
    process.exit(1);
  }
})();
