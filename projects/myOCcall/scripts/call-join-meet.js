#!/usr/bin/env node
/**
 * call-join-meet.js <call_dir> <meet_url>
 *
 * Entra in una Google Meet come "Attilio F." con mic e webcam disattivati.
 * Usa Playwright (Chromium) già configurato in OpenClaw.
 *
 * Fasi:
 *   1. Apre il link Meet
 *   2. Gestisce schermata di anteprima (disattiva mic/cam, imposta nome)
 *   3. Clicca "Partecipa" o "Chiedi di partecipare"
 *   4. Aggiorna META.md con orario di join effettivo
 *   5. Scrive il proprio PID in <call_dir>/browser.pid
 *
 * Exit code: 0 OK, 1 parametri, 2 timeout/errore join, 3 file system
 */

// Playwright installato in npm-global — risoluzione esplicita del path
const PLAYWRIGHT_PATH = process.env.PLAYWRIGHT_PATH ||
  require('path').join(
    process.env.npm_global || '/home/openclaw/.npm-global/lib/node_modules',
    'playwright'
  );
const { chromium } = require(PLAYWRIGHT_PATH);
const fs = require('fs');
const path = require('path');

const DISPLAY_NAME  = 'Attilio F.';
const JOIN_TIMEOUT  = 60_000;   // ms attesa massima per la schermata preview
const ADMIT_TIMEOUT = 120_000;  // ms attesa per essere ammessi dalla lobby
const STABLE_WAIT   = 3_000;    // ms dopo il join per verificare stabilità

// Selettori Google Meet (verificati su layout 2025-2026)
// NOTA: Meet cambia frequentemente i selettori — aggiornare in call-configs.md se rompono
const SELECTORS = {
  // Schermata preview (pre-join)
  nameField:          'input[placeholder*="nome"]',   // campo nome ospite
  micButton:          '[data-is-muted="false"][aria-label*="microfono"]',
  camButton:          '[data-is-muted="false"][aria-label*="fotocamera"]',
  joinButton:         '[data-idom-class="nCP5yc"][jsname]',  // "Partecipa ora"
  askToJoinButton:    '[jsname="Qx7uuf"]',                   // "Chiedi di partecipare"
  // Schermata in-call
  participantsBadge:  '[data-participant-id]',               // badge persone
  leaveButton:        '[aria-label*="Abbandona"]',
  // Sala d'attesa
  waitingRoomText:    'text=in attesa',
};

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function updateMeta(metaPath, key, value) {
  try {
    let text = fs.readFileSync(metaPath, 'utf8');
    const re = new RegExp(`^(- \\*\\*${key}:\\*\\*).*$`, 'm');
    if (re.test(text)) {
      text = text.replace(re, `$1 ${value}`);
    } else {
      text += `\n- **${key}:** ${value}`;
    }
    fs.writeFileSync(metaPath, text);
  } catch (e) {
    console.error(`[WARN] META update fallita per ${key}: ${e.message}`);
  }
}

function nowRome() {
  return new Date().toLocaleString('it-IT', {
    timeZone: 'Europe/Rome',
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
    hour12: false,
  }).replace(',', '');
}

(async () => {
  const [,, callDir, meetUrl] = process.argv;

  if (!callDir || !meetUrl) {
    console.error('Usage: call-join-meet.js <call_dir> <meet_url>');
    process.exit(1);
  }

  const metaPath = path.join(callDir, 'META.md');
  if (!fs.existsSync(metaPath)) {
    console.error(`ERROR: META.md non trovato in ${callDir}`);
    process.exit(3);
  }

  // Salva PID browser
  fs.writeFileSync(path.join(callDir, 'browser.pid'), String(process.pid));

  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.CHROMIUM_PATH || undefined,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-gpu',
      // Routing audio verso PulseAudio virtual_out
      '--alsa-output-device=pulse',
      '--disable-features=WebRtcHideLocalIpsWithMdns',
      // Necessario per permettere uso mic/cam virtuali
      '--use-fake-device-for-media-stream',
      '--use-fake-ui-for-media-stream',
    ],
  });

  const context = await browser.newContext({
    permissions: ['microphone', 'camera'],
    // User agent Chrome standard — Meet blocca bot agent
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
  });

  const page = await context.newPage();

  console.log(`[meet] Navigazione a ${meetUrl}`);
  await page.goto(meetUrl, { waitUntil: 'domcontentloaded', timeout: JOIN_TIMEOUT });
  await sleep(3000);

  // --- Gestione campo nome (quando Meet chiede il nome da ospite) ---
  try {
    const nameInput = await page.waitForSelector(SELECTORS.nameField, { timeout: 8000 });
    if (nameInput) {
      await nameInput.fill('');
      await nameInput.type(DISPLAY_NAME, { delay: 80 });
      console.log(`[meet] Nome impostato: ${DISPLAY_NAME}`);
    }
  } catch {
    // Il campo nome non compare se già loggato — non è un errore
    console.log('[meet] Campo nome non trovato (probabile utente già autenticato)');
  }

  // --- Disattiva microfono se attivo ---
  try {
    const mic = await page.$(SELECTORS.micButton);
    if (mic) {
      await mic.click();
      console.log('[meet] Microfono disattivato');
    }
  } catch {
    console.log('[meet] Mic già disattivato o non trovato');
  }

  // --- Disattiva webcam se attiva ---
  try {
    const cam = await page.$(SELECTORS.camButton);
    if (cam) {
      await cam.click();
      console.log('[meet] Webcam disattivata');
    }
  } catch {
    console.log('[meet] Cam già disattivata o non trovata');
  }

  await sleep(1500);

  // --- Clicca "Partecipa" o "Chiedi di partecipare" ---
  let joined = false;

  // Prova prima "Partecipa ora"
  try {
    const joinBtn = await page.waitForSelector(SELECTORS.joinButton, { timeout: 10000 });
    await joinBtn.click();
    joined = true;
    console.log('[meet] Cliccato "Partecipa ora"');
  } catch {
    // Prova "Chiedi di partecipare" (quando c'è un host che deve ammettere)
    try {
      const askBtn = await page.waitForSelector(SELECTORS.askToJoinButton, { timeout: 10000 });
      await askBtn.click();
      joined = true;
      console.log('[meet] Cliccato "Chiedi di partecipare" — in attesa ammissione lobby');

      // Attende ammissione (max ADMIT_TIMEOUT)
      console.log(`[meet] In lobby — attesa ammissione (max ${ADMIT_TIMEOUT/1000}s)...`);
      await page.waitForFunction(
        () => !document.body.innerText.toLowerCase().includes('in attesa'),
        { timeout: ADMIT_TIMEOUT }
      );
      console.log('[meet] Ammesso dalla lobby');
    } catch {
      console.error('[meet] ERRORE: nessun pulsante di join trovato e/o timeout lobby');
      await browser.close();
      process.exit(2);
    }
  }

  if (!joined) {
    await browser.close();
    process.exit(2);
  }

  await sleep(STABLE_WAIT);

  // --- Aggiorna META.md con timestamp di join effettivo ---
  const joinTime = nowRome();
  await updateMeta(metaPath, 'Bot join', `${joinTime} (Europe/Rome)`);
  console.log(`[meet] Join confermato: ${joinTime}`);

  // Scrivi anche il path del call_dir in un file per il monitoring
  fs.writeFileSync(path.join(callDir, 'active.lock'), `pid=${process.pid}\njoin=${joinTime}\n`);

  // --- Il processo rimane vivo finché non viene ucciso da call-stop.sh ---
  // Il monitoring (D) viene fatto dall'orchestratore che legge la pagina periodicamente
  // Qui esportiamo l'oggetto page attraverso un IPC semplice: scriviamo uno stato in loop
  console.log('[meet] In-call — in ascolto...');

  const statusFile = path.join(callDir, 'browser-status.json');

  const statusLoop = setInterval(async () => {
    try {
      // Conta i partecipanti visibili (badge persone in call)
      const count = await page.evaluate(() => {
        const els = document.querySelectorAll('[data-participant-id]');
        return els.length;
      });

      const status = {
        ts: nowRome(),
        participants: count,
        url: page.url(),
      };
      fs.writeFileSync(statusFile, JSON.stringify(status, null, 2));
    } catch (e) {
      fs.writeFileSync(statusFile, JSON.stringify({ ts: nowRome(), error: e.message }));
    }
  }, 30_000);  // ogni 30s aggiorna browser-status.json

  // Gestione segnali per shutdown pulito
  const shutdown = async (signal) => {
    console.log(`[meet] Ricevuto ${signal} — chiusura browser`);
    clearInterval(statusLoop);
    try {
      // Prova a cliccare "Abbandona" prima di chiudere
      const leaveBtn = await page.$(SELECTORS.leaveButton);
      if (leaveBtn) {
        await leaveBtn.click();
        await sleep(1000);
      }
    } catch { /* ignore */ }
    try { await browser.close(); } catch { /* ignore */ }
    fs.rmSync(path.join(callDir, 'active.lock'), { force: true });
    fs.rmSync(path.join(callDir, 'browser.pid'), { force: true });
    process.exit(0);
  };

  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT',  () => shutdown('SIGINT'));

  // Tieni vivo il processo
  await new Promise(() => {});
})();
