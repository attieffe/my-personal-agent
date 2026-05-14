# Pre-analisi: Integrazione Zoom e Microsoft Teams

> Documento di analisi tecnica per la futura implementazione dei join automatici e speaker attribution su Zoom e Microsoft Teams, in parallelo con l'architettura già funzionante per Google Meet.

---

## Architettura comune (riferimento Meet)

Il flow già implementato per Meet è:

```
call-start.sh          → crea cartella, avvia ffmpeg su virtual_out.monitor
call-join-{platform}.js → entra nella call, disattiva mic/cam, rileva speaker DOM
call-monitor.sh        → watchdog audio
call-stop.sh           → ferma ffmpeg e browser
call-post.sh           → manifest → whisper verbose_json → overlay speaker → SINTESI.md
```

Le parti che rimangono **invariate** per Zoom e Teams:
- `call-start.sh` — audio ffmpeg da PulseAudio, nessuna dipendenza da piattaforma
- `call-audio-manifest.sh`, `call-transcribe-segments.sh`, `call-speaker-overlay.py`
- `call-post.sh`, `call-monitor.sh`, `call-stop.sh`

Le parti che richiedono **implementazione specifica per piattaforma**:
- Script di join (`call-join-zoom.js`, `call-join-teams.js`)
- Selettori DOM per speaker attribution
- Gestione pre-join (nome ospite, mic/cam, lobby)

---

## Zoom Web Client

### Caratteristiche tecniche

| Aspetto | Dettaglio |
|---|---|
| URL web client | `https://app.zoom.us/wc/{meeting_id}/join?pwd={password}` |
| URL da link diretto | `https://zoom.us/j/{meeting_id}?pwd={password}` (redirect al web client) |
| Auth guest | Sì, con display name |
| Auth account | Opzionale (può entrare come guest) |
| Anti-bot | **Attenzione**: Zoom ha rilevamento headless → serve `--headless=new` o `xvfb` |

### Headless Chromium e Zoom

Zoom web client usa fingerprinting aggressivo. Con Playwright headless standard può mostrare errore "browser non supportato" o bloccare il join. Soluzioni note:
- `--headless=new` (Chrome 112+) riduce il fingerprint
- User-agent Chrome standard (già fatto per Meet) — necessario
- `--disable-blink-features=AutomationControlled` — evita che `navigator.webdriver` sia `true`
- Opzione alternativa: **Xvfb headless display** → Playwright `headless: false` con display virtuale (già disponibile su questo host con PulseAudio)

### Pre-join flow Zoom Web

1. Navigare all'URL (eventuale redirect da `zoom.us/j/...` a `app.zoom.us/wc/...`)
2. Schermata "Enter your name": `input[placeholder*="name"]` o `#inputname`
3. Schermata preview video/audio:
   - Disattiva cam: `[aria-label="Stop Video"]` o `.btn-camera-on`
   - Disattiva mic: `[aria-label="Mute"]` o `.btn-audio-on`
4. Pulsante join: `.join-btn`, `[aria-label="Join"]`, o `#joinBtn`
5. Eventuale lobby (host deve ammettere): attesa come su Meet

### DOM in-call: Active Speaker Detection (Zoom)

**Approccio 1 — Tile layout:**
```javascript
// Il tile attivo ha spesso un bordo verde o classe "active"
document.querySelector('.video-tile--active [class*="display-name"]')
document.querySelector('.active-video .video-avatar__name')
document.querySelector('[class*="active-speaker"] [class*="name"]')
```

**Approccio 2 — Speaker indicator:**
```javascript
// Zoom mostra un'icona microfono animata accanto al nome del parlante
document.querySelector('[aria-label*="is speaking"]')?.closest('[class*="participant"]')
  ?.querySelector('[class*="display-name"]')
```

**Approccio 3 — Participant list:**
```javascript
// La lista partecipanti può avere uno stato "speaking"
document.querySelector('[class*="participant-item"][class*="speaking"] [class*="display-name"]')
```

**NOTA CRITICA**: Zoom usa molto rendering su `<canvas>` per i video. I nomi sopra i tile possono essere overlay DOM separati, non sempre stabili. Testare con `page.evaluate()` in devtools durante una call reale prima di fissare i selettori.

### Audio Zoom

Zoom web routing audio già coperto da PulseAudio `virtual_out.monitor` — nessuna modifica necessaria. Verificare che l'opzione "Join Audio by Computer" venga accettata automaticamente (di solito compare un dialog).

---

## Microsoft Teams Web Client

### Caratteristiche tecniche

| Aspetto | Dettaglio |
|---|---|
| URL | Link diretto meeting Teams (es. `https://teams.microsoft.com/l/meetup-join/...`) |
| Auth guest | Sì, con display name (nessun account Microsoft richiesto) |
| Auth account | Supportato (se già loggati) |
| Anti-bot | **Basso**: Teams usa Playwright internamente per i test, ha `data-tid` stabili |
| Headless | Funziona bene con Playwright headless standard |

### Pre-join flow Teams Web

1. Navigare al link meeting
2. Scelta "Continua senza account" / "Continue on this browser"
3. Campo nome: `[data-tid="prejoin-display-name"]` o `input[placeholder*="Name"]`
4. Disattiva cam: `[data-tid="prejoin-cam-toggle"]` o `[aria-label*="Camera off"]`
5. Disattiva mic: `[data-tid="prejoin-mic-toggle"]` o `[aria-label*="Mute"]`
6. Pulsante join: `[data-tid="prejoin-join-button"]`
7. Lobby: attesa con `waitForFunction` finché non si entra

### DOM in-call: Active Speaker Detection (Teams)

Teams usa attributi `data-tid` relativamente stabili (usati anche nei test Microsoft):

**Approccio 1 — Speaking indicator roster:**
```javascript
// Partecipante con stato "speaking" nella lista
document.querySelector('[data-tid*="roster"][data-is-speaking="true"] [data-tid*="name"]')
document.querySelector('[data-tid="participant-is-speaking"] ~ [data-tid*="name"]')
```

**Approccio 2 — Stage/main speaker:**
```javascript
// Il parlante principale è in posizione prominente nello stage
document.querySelector('[data-tid="video-tile-display-name-main"]')
document.querySelector('[data-tid="active-speaker-name"]')
```

**Approccio 3 — Aria-label locale:**
```javascript
// Con locale italiano
document.querySelector('[aria-label*="sta parlando"]')
  ?.closest('[class*="participant"]')
  ?.querySelector('[class*="name"]')
```

**Approccio 4 — Border/glow CSS class:**
```javascript
// Teams aggiunge una classe o attributo al tile del parlante attivo
document.querySelector('[class*="speaking-indicator--active"]')?.textContent?.trim()
```

**VANTAGGIO Teams**: I `data-tid` di Microsoft sono pensati per l'accessibilità e i test automatizzati — molto più stabili dei selettori di Zoom e Meet (che cambiano con ogni deploy).

### Audio Teams

Identico a Meet e Zoom — PulseAudio `virtual_out.monitor`. Teams può chiedere permesso microfono/camera: gestire con le stesse opzioni Playwright già usate per Meet (`permissions: ['microphone', 'camera']`).

---

## Confronto piattaforme

| Feature | Google Meet | Zoom Web | Teams Web |
|---|---|---|---|
| Join guest (no account) | Sì | Sì | Sì |
| Headless Playwright | ✓ (implementato) | Difficile (anti-bot) | ✓ facile |
| Selettori DOM stabili | Medio | Basso (canvas) | Alto (data-tid) |
| Speaker attribution DOM | 4 strategie | 3 strategie (da verificare) | 4 strategie (data-tid) |
| Lobby/attesa ammissione | Sì | Sì | Sì |
| Dialog audio al join | No | Sì ("Join by Computer") | No |

---

## Tool aggiuntivi da valutare

### Zoom
- **Xvfb** (`Xvfb :99 -screen 0 1280x720x24`) se headless Chrome viene bloccato da Zoom → Playwright con `headless: false` + `DISPLAY=:99`
- **`playwright-extra` + `puppeteer-extra-plugin-stealth`** (port Playwright): riduce fingerprint anti-bot. Disponibile come npm package.

### Teams
- Nessun tool aggiuntivo necessario — Teams è Playwright-friendly by design.

---

## File da creare per ogni piattaforma

### Zoom
```
scripts/call-join-zoom.js         # join + speaker monitoring
docs/ZOOM_SELECTORS.md            # selettori verificati (da compilare dopo test)
```

### Teams
```
scripts/call-join-teams.js        # join + speaker monitoring
docs/TEAMS_SELECTORS.md           # selettori verificati (da compilare dopo test)
```

Entrambi i file dovranno esporre la stessa interfaccia di `call-join-meet.js`:
- Argomenti: `<call_dir> <url>`
- Output: `active.lock`, `browser.pid`, `browser-status.json`, `speaker-events.jsonl`
- META.md: aggiornare `Bot join`, `bot_join_epoch_ms`
- Segnali: SIGTERM → shutdown pulito

---

> Aggiornare questo documento dopo ogni test reale con selettori confermati.
