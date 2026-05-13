# Piano di progetto — myOCcall

**Obiettivo finale:** Ralf entra in una call (Meet, Zoom, Teams) come partecipante silenzioso, cattura l'audio, lo trascrive con Whisper e produce un riassunto strutturato. Tutto orchestrato da OpenClaw su server Linux headless.

---

## Stato attuale — 2026-05-13

### Completato
- [x] Analisi fattibilità stack su Linux headless
- [x] `pulseaudio`, `pulseaudio-utils`, `ffmpeg` installati
- [x] `~/.config/pulse/default.pa` configurato con null sink `virtual_out`
- [x] PulseAudio avviato e stabile (`--exit-idle-time=-1`)
- [x] Test cattura audio: `ffmpeg -f pulse -i virtual_out.monitor -t 5 test.mp3` → OK
- [x] Script `scripts/start-audio.sh` (avvio idempotente)
- [x] Autostart in `~/.bashrc`
- [x] Pipeline audio end-to-end verificata: sink `virtual_out` → parec cattura a -6.2 dB da browser Chromium
- [x] Playwright Chromium installato e configurato in OpenClaw (`noSandbox`, `ssrfPolicy`)

### Bloccante attuale
> **Step 4** — join automatico call (Meet, Zoom, Teams)

---

## Roadmap completa

### Step 1 — Infrastruttura audio ✅
Installazione e configurazione PulseAudio null sink su server headless.

### Step 2 — Cattura audio ✅
ffmpeg legge da `virtual_out.monitor` e produce file MP3/WAV.

### Step 3 — Browser → virtual sink ✅
Chromium (Playwright) instradia audio a PulseAudio `virtual_out`.
- Playwright Chromium installato in `~/.cache/ms-playwright/chromium-1223/` (no sudo)
- OpenClaw configurato: `executablePath`, `noSandbox: true`, `ssrfPolicy.dangerouslyAllowPrivateNetwork: true`
- Test confermato: AudioContext WebAudio → PulseAudio sink input → `virtual_out.monitor` → parec cattura a **-6.2 dB** ✅
- Nota: AudioContext richiede gesto utente (click) per avviarsi — `suspended` senza interazione
- `parec --device=virtual_out.monitor` è il tool di cattura raccomandato (più stabile di ffmpeg per PulseAudio)

### Step 4 — Join call automatico 🔲
Usare OpenClaw browser tool per entrare nei link di call.
- **Google Meet:** navigare al link, gestire schermata di anteprima, cliccare "Partecipa"
- **Zoom:** aprire link web (non app), gestire waiting room
- **Teams:** login Microsoft, gestire lobby
- Per ogni piattaforma: documentare i selettori CSS/XPath necessari in `notes/call-configs.md`

### Step 5 — Configurazione credenziali per piattaforma 🔲
- Google Meet: account Google da configurare in OpenClaw
- Teams: account Microsoft (o accesso ospite) da configurare
- Zoom: accesso via browser senza app (o account Zoom)
- Salvare le istruzioni specifiche in `notes/call-configs.md`

### Step 6 — Trascrizione Whisper 🔲
Integrare lo skill `openai-whisper-api` già disponibile in OpenClaw.
- Configurare chiave API OpenAI (verificare se già presente in OpenClaw)
- Dividere audio in chunk da max 25MB se call lunga
- Script `scripts/transcribe.sh` (o funzione Python)

### Step 7 — Pipeline end-to-end 🔲
Orchestratore che fa tutto in sequenza:
1. Avvia cattura ffmpeg in background
2. Apre il link della call nel browser
3. Attende fine call (rileva disconnessione o timeout)
4. Ferma ffmpeg
5. Trascrive con Whisper
6. Ralf produce riassunto strutturato
7. Invia riassunto via Telegram a Atti

### Step 8 — Skill dedicata 🔲
Creare una skill OpenClaw `call-summarizer` con SKILL.md dedicato, in modo che in futuro basti dire "entra in questa call e riassumila" passando il link.

---

## Note tecniche critiche

- `~/.config/pulse/default.pa` **deve** iniziare con `.include /etc/pulse/default.pa` — senza, il socket non viene creato
- PulseAudio **deve** girare con `--exit-idle-time=-1` altrimenti si spegne dopo pochi secondi
- Il systemd socket activation interferisce: usare sempre `scripts/start-audio.sh`
- Whisper skill è già disponibile in OpenClaw (path: `~/.npm-global/lib/node_modules/openclaw/skills/openai-whisper-api/`)

---

## File di progetto

```
myOCcall/
├── PLAN.md                 ← questo file (piano strutturato)
├── README.md               ← overview e stato avanzamento
├── CHANGELOG.md            ← versioni e modifiche
├── docs/
│   ├── architecture.md     ← stack e flusso completo
│   ├── functions.md        ← funzioni principali (sintetico)
│   └── setup.md            ← guida installazione con note tecniche
├── notes/
│   └── call-configs.md     ← config specifiche per Meet/Zoom/Teams
└── scripts/
    └── start-audio.sh      ← avvio PulseAudio idempotente
```

---

## Regola di aggiornamento

Ogni volta che uno step viene completato, aggiornare **subito**:
- `PLAN.md` → spuntare lo step
- `README.md` → aggiornare stato avanzamento
- `CHANGELOG.md` → aggiungere voce con dettagli tecnici

Non aspettare fine sessione.

---

## Come riprendere il progetto (da zero contesto)

1. Leggi questo file (`PLAN.md`) per capire dove si è arrivati
2. Leggi `CHANGELOG.md` per i dettagli tecnici degli step completati
3. Leggi `notes/call-configs.md` per le configurazioni specifiche delle piattaforme
4. Verifica che PulseAudio sia attivo: `pactl info`
5. Se non è attivo: `~/.openclaw/workspace/myOCcall/scripts/start-audio.sh`
6. Riprendi dallo **Step 3** (browser routing)
