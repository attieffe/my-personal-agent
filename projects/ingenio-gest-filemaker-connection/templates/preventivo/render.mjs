import { spawnSync } from 'node:child_process';
import { mkdir, writeFile, appendFile, access, constants } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { fetchAllData } from './data.mjs';
import { generateHtml } from './template.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(__dirname, '..', '..');

const EDGE_CANDIDATES = [
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
];

async function findBrowser() {
  for (const p of EDGE_CANDIDATES) {
    try {
      await access(p, constants.X_OK);
      return p;
    } catch { /* not present */ }
  }
  throw new Error('Nessun browser headless trovato (Edge/Chrome). Installare Edge oppure aggiungere il path in EDGE_CANDIDATES.');
}

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) continue;
    const key = a.slice(2);
    const next = argv[i + 1];
    if (next === undefined || next.startsWith('--')) {
      out[camel(key)] = true;
    } else {
      out[camel(key)] = next;
      i++;
    }
  }
  return out;
}

function camel(k) {
  return k.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
}

function slug(s) {
  return String(s || '')
    .toLowerCase()
    .normalize('NFD').replace(/\p{Diacritic}/gu, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 60);
}

function defaultOutputPath(testata) {
  const ragSoc = slug(testata.cliente.ragioneSociale);
  const fileName = `PRE-${testata.nr}-${testata.anno}-${ragSoc || 'cliente'}.pdf`;
  return join(PROJECT_ROOT, 'output', 'preventivi', String(testata.anno), fileName);
}

function printCandidates(candidates, prefix = '  ') {
  for (const c of candidates) {
    const dataIt = (c.data || '').replace(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/, '$2/$1/$3');
    console.error(`${prefix}- recordId ${c.recordId} | Nr ${c.nr}/${c.anno} | ${dataIt} | ${c.ragioneSociale || ''} | tot ${c.totale ?? ''}`);
    if (c.note) console.error(`${prefix}  ↳ ${c.note}`);
  }
}

async function appendLog(line) {
  const now = new Date();
  const yyyy = now.getFullYear();
  const mm = String(now.getMonth() + 1).padStart(2, '0');
  const logFile = join(PROJECT_ROOT, 'logs', `${yyyy}-${mm}.md`);
  try {
    await mkdir(dirname(logFile), { recursive: true });
    const stamp = now.toISOString().replace('T', ' ').slice(0, 16);
    await appendFile(logFile, `- ${stamp} · ${line}\n`, 'utf8');
  } catch (err) {
    console.error(`[warn] log append failed: ${err.message}`);
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.help || args.h) {
    console.log(`
Uso: npm run preventivo -- [opzioni]

Identificazione preventivo (uno dei):
  --nr <N> [--anno <YYYY>]        Numero (anno corrente se omesso, fallback anno -1)
  --record-id <ID>                recordId interno FileMaker
  --cliente <testo> --ultimo      Ultimo preventivo del cliente
  --cliente <testo> --argomento <testo>   Ultimo preventivo che contiene <testo> nelle note
  --cliente <testo> --da <MM/DD/YYYY> --a <MM/DD/YYYY>   Range data + cliente

Opzioni stampa:
  --iva-inclusa                   Mostra "Totale riga" invece di "Imponibile" per riga
  --html-only                     Salva solo l'HTML (skip PDF)
  --output <path>                 Path di output PDF (default: output/preventivi/<anno>/PRE-<nr>-<anno>-<cliente>.pdf)
  --keep-html                     Conserva l'HTML temporaneo accanto al PDF
`);
    process.exit(0);
  }

  if (args.recordId) args.recordId = String(args.recordId);
  if (args.nr) args.nr = String(args.nr);
  if (args.anno) args.anno = String(args.anno);

  console.error('🔎 Risoluzione preventivo...');
  const data = await fetchAllData(args);

  if (data.resolution.status === 'notfound') {
    console.error(`❌ ${data.resolution.hint}`);
    process.exit(1);
  }
  if (data.resolution.status === 'fallback') {
    console.error(`⚠️  ${data.resolution.hint}`);
    if (data.resolution.candidates) printCandidates(data.resolution.candidates);
    process.exit(2);
  }
  if (data.resolution.status === 'multiple') {
    console.error(`⚠️  ${data.resolution.hint}`);
    if (data.resolution.candidates) printCandidates(data.resolution.candidates);
    process.exit(2);
  }

  console.error(`✅ Trovato Nr ${data.testata.nr}/${data.testata.anno} — ${data.testata.cliente.ragioneSociale} (${data.righe.length} righe)`);

  const html = generateHtml(data, { ivaInclusa: !!args.ivaInclusa });

  const outputPath = args.output ? resolve(String(args.output)) : defaultOutputPath(data.testata);
  await mkdir(dirname(outputPath), { recursive: true });

  if (args.htmlOnly) {
    const htmlPath = outputPath.replace(/\.pdf$/i, '.html');
    await writeFile(htmlPath, html, 'utf8');
    console.error(`📄 HTML salvato: ${htmlPath}`);
    await appendLog(`HTML preventivo Nr ${data.testata.nr}/${data.testata.anno} (${data.testata.cliente.ragioneSociale}) → ${htmlPath} · OK`);
    return;
  }

  // Salva HTML temporaneo localmente (no Drive — evita lock di sync durante Edge)
  const tmpHtml = join(tmpdir(), `preventivo-${data.testata.nr}-${data.testata.anno}-${Date.now()}.html`);
  await writeFile(tmpHtml, html, 'utf8');

  const tmpPdf = join(tmpdir(), `preventivo-${data.testata.nr}-${data.testata.anno}-${Date.now()}.pdf`);
  const userDataDir = join(tmpdir(), 'edge-headless-profile-mpa');
  await mkdir(userDataDir, { recursive: true });

  const browser = await findBrowser();
  console.error(`🖨  Generazione PDF (Edge headless)...`);
  const args2 = [
    '--headless=new',
    '--disable-gpu',
    '--no-first-run',
    '--no-pdf-header-footer',
    `--user-data-dir=${userDataDir}`,
    `--print-to-pdf=${tmpPdf}`,
    `file://${tmpHtml.replace(/\\/g, '/')}`,
  ];
  const r = spawnSync(browser, args2, { encoding: 'utf8', timeout: 60000 });
  if (r.status !== 0) {
    console.error('❌ Edge fallito.');
    if (r.stderr) console.error(r.stderr);
    if (r.stdout) console.error(r.stdout);
    process.exit(3);
  }

  // Sposta il PDF nella destinazione finale
  const { copyFile, unlink } = await import('node:fs/promises');
  await copyFile(tmpPdf, outputPath);
  await unlink(tmpPdf).catch(() => {});

  if (args.keepHtml) {
    const htmlAccanto = outputPath.replace(/\.pdf$/i, '.html');
    await copyFile(tmpHtml, htmlAccanto);
    console.error(`📝 HTML conservato: ${htmlAccanto}`);
  }
  await unlink(tmpHtml).catch(() => {});

  console.error(`📄 PDF salvato: ${outputPath}`);
  await appendLog(`PDF preventivo Nr ${data.testata.nr}/${data.testata.anno} (${data.testata.cliente.ragioneSociale}) → ${outputPath} · OK`);
}

main().catch(err => {
  console.error(`❌ ${err.message}`);
  if (process.env.DEBUG) console.error(err.stack);
  process.exit(99);
});
