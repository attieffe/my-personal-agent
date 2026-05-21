#!/usr/bin/env node
/**
 * call-join-teams.js <call_dir> <teams_url>
 *
 * Entra in una Microsoft Teams call come "Attilio F." con mic e webcam disattivati.
 * Usa Playwright (Chromium) già configurato in OpenClaw.
 *
 * Fasi:
 *   1. Apre il link Teams
 *   2. Bypassa prompt "Apri app" → continua nel browser
 *   3. Gestisce pre-join (nome, disattiva mic/cam)
 *   4. Clicca "Partecipa"
 *   5. Aggiorna META.md con orario di join effettivo + bot_join_epoch_ms
 *   6. Speaker monitoring DOM ogni 2s → speaker-events.jsonl
 *   7. Scrive PID in <call_dir>/browser.pid
 *
 * Exit code: 0 OK, 1 parametri, 2 timeout/errore join, 3 file system
 */

const PLAYWRIGHT_PATH = process.env.PLAYWRIGHT_PATH ||
  require('path').join(
    process.env.npm_global || '/home/openclaw/.npm-global/lib/node_modules',
    'playwright'
  );
const { chromium } = require(PLAYWRIGHT_PATH);
const fs = require('fs');
const path = require('path');

const DISPLAY_NAME   = 'Attilio F.';
const PREJOIN_TIMEOUT = 60_000;   // ms attesa schermata pre-join
const LOBBY_TIMEOUT   = 180_000;  // ms attesa ammissione lobby (Teams ha lobby più lenta)
const STABLE_WAIT     = 4_000;    // ms dopo join per verifica stabilità

// Selettori Teams (basati su data-tid Microsoft + fallback aria-label)
// NOTA: data-tid è usato internamente da Microsoft per i test — più stabile di classi CSS
const SELECTORS = {
  // Bypass "Apri app Teams"
  continueInBrowser: [
    '[data-tid="joinOnWeb"]',
    'a[href*="launchAgent=false"]',
    'button:has-text("Continua nel browser")',
    'button:has-text("Continue on this browser")',
    'a:has-text("Continua nel browser")',
    'a:has-text("Continue on this browser")',
  ],

  // Overlay Teams: continua senza audio/video
  continueWithoutAudioVideo: [
    'button:has-text("Continua senza audio o video")',
    'button:has-text("Continue without audio or video")',
    '[data-tid="prejoin-continue-without-audio-video-button"]',
  ],

  // Pre-join: campo nome (ospite senza account)
  nameField: [
    '[data-tid="prejoin-display-name"]',
    'input[placeholder*="nome"]',
    'input[placeholder*="Name"]',
    'input[placeholder*="name"]',
  ],

  // Pre-join: toggle videocamera (clicca solo se attiva)
  cameraOn: [
    '[data-tid="toggle-video"][aria-checked="true"]',
    '[data-tid="toggle-video"][aria-pressed="true"]',
    'button[aria-label*="Disattiva videocamera"]',
    'button[aria-label*="Turn camera off"]',
    'button[aria-label*="Camera, selected"]',
  ],

  // Pre-join: toggle microfono (clicca solo se attivo)
  micOn: [
    '[data-tid="toggle-audio"][aria-checked="true"]',
    '[data-tid="toggle-audio"][aria-pressed="true"]',
    'button[aria-label*="Disattiva microfono"]',
    'button[aria-label*="Mute microphone"]',
    'button[aria-label*="Mic, selected"]',
  ],

  // Pulsante join
  joinButton: [
    '[data-tid="prejoin-join-button"]',
    'button[data-tid*="join"]',
    'button[aria-label*="Partecipa ora"]',
    'button[aria-label*="Join now"]',
    'button:has-text("Partecipa ora")',
    'button:has-text("Join now")',
  ],

  // Conferma di essere in call (qualcosa visibile solo in-call)
  inCallIndicator: [
    '[data-tid="hangup-button"]',
    '[data-tid="callingButton-hangup"]',
    '[aria-label*="Abbandona"]',
    '[aria-label*="Leave"]',
  ],

  // Speaker detection in-call (4 strategie, usate in JS evaluate)
  // vedi speakerStrategies qui sotto
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

// Prova una lista di selettori e restituisce il primo che trova
async function trySelectors(page, selectors, timeout = 8000) {
  for (const sel of selectors) {
    try {
      const el = await page.waitForSelector(sel, { timeout: 2000 });
      if (el) return el;
    } catch { /* prossimo */ }
  }
  return null;
}

async function detectJoinState(page, prejoinUrl) {
  const joinBtnVisible = await page.locator('button[data-tid="prejoin-join-button"], [data-tid="prejoin-join-button"]').count().catch(() => 0);
  const url = page.url();

  const dom = await page.evaluate(() => {
    const text = (document.body && document.body.innerText) ? document.body.innerText : '';
    const hasHangup = !!document.querySelector(
      '[data-tid="hangup-button"], [data-tid="callingButton-hangup"], [aria-label*="Abbandona"], [aria-label*="Leave"]'
    );
    const hasCallChrome = !!document.querySelector(
      '[aria-label*="Chat"], [aria-label*="Persone"], [aria-label*="People"], [aria-label*="Reazioni"], [aria-label*="Raise hand"], [aria-label*="Alza la mano"]'
    );
    return {
      text,
      hasHangup,
      hasCallChrome,
      hasRoster: !!document.querySelector('[data-tid*="roster-tile"], [data-participant-id]'),
      hasLobbyText: /attesa|waiting|sala di attesa|stiamo aspettando/i.test(text),
    };
  }).catch(() => ({ text: '', hasHangup: false, hasCallChrome: false, hasRoster: false, hasLobbyText: false }));

  if (dom.hasHangup || dom.hasCallChrome || dom.hasRoster) {
    return { joined: true, reason: dom.hasHangup ? 'hangup-button' : dom.hasCallChrome ? 'call-chrome' : 'roster' };
  }

  if (url !== prejoinUrl && joinBtnVisible === 0) {
    return { joined: true, reason: 'post-join-url-change' };
  }

  if (dom.hasLobbyText && joinBtnVisible === 0) {
    return { joined: true, reason: 'lobby-transition' };
  }

  return { joined: false, reason: 'prejoin-or-unknown' };
}

// Aggiunge parametri all'URL per ridurre prompt "apri app"
function teamsUrlBypassApp(url) {
  try {
    const u = new URL(url);
    // Parametri per forzare web client
    u.searchParams.set('directDl', 'true');
    u.searchParams.set('msLaunch', 'false');
    u.searchParams.set('enableMobilePage', 'false');
    u.searchParams.set('suppressPrompt', 'true');
    return u.toString();
  } catch {
    return url;
  }
}

(async () => {
  const [,, callDir, teamsUrl] = process.argv;

  if (!callDir || !teamsUrl) {
    console.error('Usage: call-join-teams.js <call_dir> <teams_url>');
    process.exit(1);
  }

  const metaPath = path.join(callDir, 'META.md');
  if (!fs.existsSync(metaPath)) {
    console.error(`ERROR: META.md non trovato in ${callDir}`);
    process.exit(3);
  }

  fs.writeFileSync(path.join(callDir, 'browser.pid'), String(process.pid));

  const browser = await chromium.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-gpu',
      // Riduce fingerprint anti-bot
      '--disable-blink-features=AutomationControlled',
      // Audio PulseAudio
      '--alsa-output-device=pulse',
      '--disable-features=WebRtcHideLocalIpsWithMdns',
    ],
  });

  const context = await browser.newContext({
    permissions: ['microphone', 'camera'],
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    // Locale italiano per selettori aria-label in italiano
    locale: 'it-IT',
  });

  // Evita che navigator.webdriver sia rilevabile
  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  });

  const page = await context.newPage();

  // Naviga con parametri bypass-app
  const navUrl = teamsUrlBypassApp(teamsUrl);
  console.log(`[teams] Navigazione a ${navUrl}`);
  await page.goto(navUrl, { waitUntil: 'domcontentloaded', timeout: PREJOIN_TIMEOUT });
  const prejoinUrl = page.url();
  await sleep(3000);

  // --- Bypass "Apri app Teams" ---
  const continueBtn = await trySelectors(page, SELECTORS.continueInBrowser, 10000);
  if (continueBtn) {
    await continueBtn.click();
    console.log('[teams] Cliccato "Continua nel browser"');
    await sleep(3000);
  } else {
    console.log('[teams] Prompt "Apri app" non trovato — continuo (bypass URL potrebbe aver funzionato)');
  }

  // --- Campo nome (ospite) ---
  const nameInput = await trySelectors(page, SELECTORS.nameField, 12000);
  if (nameInput) {
    await nameInput.fill('');
    await nameInput.type(DISPLAY_NAME, { delay: 80 });
    console.log(`[teams] Nome impostato: ${DISPLAY_NAME}`);
  } else {
    console.log('[teams] Campo nome non trovato (utente già autenticato?)');
  }

  await sleep(1000);

  // --- Disattiva videocamera ---
  const camBtn = await trySelectors(page, SELECTORS.cameraOn, 5000);
  if (camBtn) {
    await camBtn.click();
    console.log('[teams] Videocamera disattivata');
  } else {
    console.log('[teams] Cam già disattivata o non trovata');
  }

  // --- Disattiva microfono ---
  const micBtn = await trySelectors(page, SELECTORS.micOn, 5000);
  if (micBtn) {
    await micBtn.click();
    console.log('[teams] Microfono disattivato');
  } else {
    console.log('[teams] Mic già disattivato o non trovato');
  }

  await sleep(1500);

  // --- Chiudi eventuale overlay audio/video e continua ---
  const continueNoAv = await trySelectors(page, SELECTORS.continueWithoutAudioVideo, 3000);
  if (continueNoAv) {
    await continueNoAv.click({ force: true });
    console.log('[teams] Continuo senza audio o video');
    await sleep(2000);
  }

  // --- Clicca "Partecipa" ---
  const joinBtn = await trySelectors(page, SELECTORS.joinButton, 15000);
  if (!joinBtn) {
    console.error('[teams] ERRORE: pulsante "Partecipa" non trovato');
    await browser.close();
    process.exit(2);
  }
  await joinBtn.click({ force: true });
  console.log('[teams] Cliccato "Partecipa"');

  // --- Attendi conferma in-call (potrebbe passare per lobby) ---
  console.log(`[teams] Attesa conferma in-call (max ${LOBBY_TIMEOUT / 1000}s)...`);
  try {
    let found = false;
    const deadline = Date.now() + LOBBY_TIMEOUT;
    while (Date.now() < deadline) {
      const state = await detectJoinState(page, prejoinUrl);
      if (state.joined) {
        console.log(`[teams] Stato call rilevato: ${state.reason}`);
        found = true;
        break;
      }
      await sleep(2000);
    }
    if (!found) {
      console.error('[teams] TIMEOUT: join in-call non confermato entro il limite');
      await browser.close();
      process.exit(2);
    }
  } catch (e) {
    console.error(`[teams] ERRORE attesa in-call: ${e.message}`);
    await browser.close();
    process.exit(2);
  }

  await sleep(STABLE_WAIT);

  // --- Aggiorna META.md ---
  const joinTime = nowRome();
  await updateMeta(metaPath, 'Bot join', `${joinTime} (Europe/Rome)`);
  await updateMeta(metaPath, 'bot_join_epoch_ms', String(Date.now()));
  console.log(`[teams] Join confermato: ${joinTime}`);

  fs.writeFileSync(path.join(callDir, 'active.lock'), `pid=${process.pid}\njoin=${joinTime}\n`);

  // --- Speaker monitoring (ogni 2s) ---
  const speakerLog = path.join(callDir, 'speaker-events.jsonl');
  let lastSpeaker = null;

  const speakerLoop = setInterval(async () => {
    try {
      const result = await page.evaluate(() => {
        // Strategia 1: data-tid roster con speaking state
        const rosterSpeaking = document.querySelector(
          '[data-tid*="roster-tile"][aria-label*="sta parlando"], ' +
          '[data-tid*="roster-tile"][aria-label*="is speaking"]'
        );
        if (rosterSpeaking) {
          const name = rosterSpeaking.querySelector('[data-tid*="name"], [class*="name"]')?.textContent?.trim()
                    || rosterSpeaking.getAttribute('aria-label')?.split(',')[0]?.trim();
          if (name) return { name, source: 'roster-speaking-aria' };
        }

        // Strategia 2: data-is-speaking su tile
        const speakingTile = document.querySelector('[data-is-speaking="true"]');
        if (speakingTile) {
          const name = speakingTile.querySelector('[data-tid*="name"], [class*="name"]')?.textContent?.trim();
          if (name) return { name, source: 'data-is-speaking' };
        }

        // Strategia 3: video tile principale (stage/spotlight) — nome del parlante principale
        const stageName = document.querySelector(
          '[data-tid="video-tile-display-name"], ' +
          '[data-tid="calling-unified-presenter-name"], ' +
          '[data-tid*="active-speaker-name"]'
        );
        const name3 = stageName?.textContent?.trim();
        if (name3 && name3 !== 'Attilio F.') return { name: name3, source: 'stage-name' };

        // Strategia 4: border/classe speaking su tile con nome
        const speakingBorder = document.querySelector(
          '[class*="speaking-indicator--active"], ' +
          '[class*="active-speaker"][class*="video-tile"]'
        );
        if (speakingBorder) {
          const name = speakingBorder.querySelector('[class*="name"], [data-tid*="name"]')?.textContent?.trim();
          if (name) return { name, source: 'speaking-border' };
        }

        return null;
      });

      if (result && result.name !== lastSpeaker) {
        const event = {
          epoch_ms: Date.now(),
          speaker: result.name,
          source: result.source,
          event: 'start',
        };
        fs.appendFileSync(speakerLog, JSON.stringify(event) + '\n');
        lastSpeaker = result.name;
        console.log(`[teams] Speaker: ${result.name} (${result.source})`);
      }
    } catch { /* ignora errori DOM transienti */ }
  }, 2000);

  // --- Status loop (ogni 30s) ---
  const statusFile = path.join(callDir, 'browser-status.json');

  const statusLoop = setInterval(async () => {
    try {
      const count = await page.evaluate(() => {
        // Conta partecipanti nel roster Teams
        return document.querySelectorAll('[data-tid*="roster-tile"]').length
            || document.querySelectorAll('[data-participant-id]').length
            || 0;
      });
      fs.writeFileSync(statusFile, JSON.stringify({
        ts: nowRome(),
        participants: count,
        url: page.url(),
      }, null, 2));
    } catch (e) {
      fs.writeFileSync(statusFile, JSON.stringify({ ts: nowRome(), error: e.message }));
    }
  }, 30_000);

  // --- Shutdown pulito ---
  const shutdown = async (signal) => {
    console.log(`[teams] Ricevuto ${signal} — chiusura browser`);
    clearInterval(speakerLoop);
    clearInterval(statusLoop);
    try {
      const leaveBtn = await trySelectors(page, SELECTORS.inCallIndicator, 3000);
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

  console.log('[teams] In-call — in ascolto...');
  await new Promise(() => {});
})();
