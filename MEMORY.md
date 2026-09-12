# MEMORY.md - Long-Term Memory

_Your curated memory. The distilled essence of what you've learned._

Le prime 200 righe di questo file vengono caricate automaticamente in ogni sessione principale. Mantienilo conciso.

Per dettagli giornalieri raw → vedi `memory/YYYY-MM-DD.md`  
Per progetti specifici → vedi [progetti.md](progetti.md)

---

## 🎯 Lezioni Critiche

### Cron — Timeout agentTurn
- Job cron `agentTurn` che fanno chiamate al modello/web_fetch: timeout **generoso** (300s+)
- **Caso 2026-09-02/03**: meteo 7:30 con timeout 60s → 2 timeout → auto-retry → doppio messaggio + errori in chat. Fix: 60→300s
- **Ricaduta 2026-09-07**: meteo Sab-Dom 8:30 stesso pattern (60s → 3 retry falliti). Fix: 60→240s. Entrambi i job meteo ora ≥240s
- Stesso pattern "TODO scadenze light": timeout 20s → 120s
- Job `systemEvent` su main session: ~10-30ms, nessun rischio timeout
- Sintomo tipico: messaggi doppi + notifiche errore = run scaduto che completa comunque in background + retry riuscito

### mio-tesoro — Naming varianti
- Nomi canonici delle proposte: `mio-tesoro-file` (full privacy), `mio-tesoro-paas` (full service), `mio-tesoro-cloud` (cloud personale ibrido), `mio-tesoro-sheet` (Google Sheet senza webapp HTML)

### Date e Timezone
- **SEMPRE usare `Europe/Rome`** per campi data/ora creazione/modifica
- **MAI UTC** (offset di 2 ore in estate causa confusione per Atti)

### Validazione Dati
- Verificare SEMPRE conti su Google Sheet specifici: **CASA ≠ PERSONALE**
- Hanno piani dei conti differenti, non sono intercambiabili
- Aggiornare sia file locali che Google Sheet (non solo uno dei due)

### Sicurezza Operativa
- **MAI azioni distruttive** senza permesso esplicito
- `trash` > `rm` (recoverable beats gone forever)

### Sicurezza Git — Segreti nei link firmati
- **2026-09-07**: push bloccato da GitHub Push Protection — "Tencent Cloud Secret ID" nel preview email (fattura Z.ai): i parametri `q-ak` di link COS firmati contengono credenziali
- Link firmati ricorrenti (query-string con token): fatture Z.ai mensili, cloud storage → **mai incollarli integri nei file tracciati da git**
- `.eml` non tracciati (gitignore) OK; i file `.md` di preview vanno sanitizzati — TODO prevenzione attivo in [[projects/myJob/TODO_GENERALE]]

### ⭐ File Esistenti — LEGGI PRIMA DI CREARE
**REGOLA ASSOLUTA:** Prima di creare **qualsiasi** file `.md`:
1. **Cerca sempre** il file `.md` esistente più adatto (per tema, cartella, tipo di dato)
2. Se esiste → **aggiorna quello**, non crearne uno nuovo
3. Se non esiste → **chiedi conferma** a Atti prima di crearne uno nuovo, proponendo il path

**Perché:** Un file aggiornato vale più di dieci file sparsi. Riduci proliferazione. Atti legge i file canonici; nuovi file vengono ignorati.

**Caso di studio:** Ho creato `BMW_X1_GA258HL.md` ignorando `BMW_X1_2020.md` che c'era già. Atti ha dovuto correggere. Mai più.

### Struttura Idee vs Implementazione
- **Idee/brainstorming progetti** → [idee_progetti](projects/myJob/PERSONALE/lavori_a_casa/idee_progetti/INDEX) (indice + una cartella per idea)
- **Implementazione operativa** → `projects/<nomeprogetto>/` (il progetto vero e proprio)
- Ogni idea può linkare al progetto `projects/` corrispondente quando esiste già un'implementazione

### Routing Organizzativo myJob
- **REGOLA FERREA:** `COLZANI/` workspace separato — non esiste in myOcSync
- Clienti diretti, agenzie, famiglia, impegni personali → questo workspace (myOcSync)
- TODO cliente [AGENZIA o DIRETTO] → **SEMPRE in TODO_GENERALE.md** + opzionale in file specifico
- **Parole chiave:** agenzie freelance (GMD, Sinapps, Newu, Studio Visual), famiglia/hobby → `PERSONALE/`
- **Sinapps e GET_ME_DIGITAL = lavoro da CASA** → TODO agenzie in `TODO_GENERALE.md` + opzionale sezione TODO in `FREELANCE/<AGENZIA>/<AGENZIA>_INDEX.md` + registro in [[PERSONALE/lavori_a_casa/41_clienti_agenzie]]

---

## 🏗️ Decisioni Architetturali

### myOCcall — Pipeline Audio
- Audio segmentato: `ffmpeg` chunk ogni **300 secondi** → `audio/segments/*.mp3`
- `audio/manifest.tsv` per tracciare segmenti validi
- Trascrizione multi-segmento → `transcripts/` → merge in `trascrizione.txt`
- Controlli anti-trascrizione falsa prima della sintesi
- Stack: PulseAudio + ffmpeg + null sink (`virtual_out`) + Whisper API
- Path call: `/home/openclaw/.openclaw/workspace/projects/myOCcall/data/YYYYMMDD HHMM <platform>/`

### AttiBot — File intake
- Pagina riusabile: `https://attibot.ingeniosolution.it/upload`
- Ogni upload genera un ref tipo `UP-YYYYMMDD-HHMMSS-XXXXXX`
- I pacchetti finiscono in `/home/openclaw/attibot/uploads/<ref>/` con `manifest.json`

### myJob — Routing TODO ⚠️ LEGGERE PRIMA DI QUALSIASI OPERAZIONE SU TODO
**REGOLA PRIMARIA:** Ogni task va SEMPRE in `projects/myJob/TODO_GENERALE.md` (fonte di verità unica).  
File specifici (TODO_PERSONALE, sezioni agenzie) sono opzionali per organizzazione.

**REGOLA SECONDARIA:** Prima di aggiungere/modificare qualsiasi task, leggere [[projects/myJob/ROUTING]] per mappa completa contesti.

Workflow corretto:
1. **SEMPRE** inserire in `TODO_GENERALE.md`
2. **OPZIONALE** duplicare/linkare in file specifico per organizzazione dettagliata

Routing rapido (tutti + TODO_GENERALE obbligatorio):
- Task freelance/ingenio → `TODO_GENERALE.md` + opzionale sezione TODO in `FREELANCE/<AGENZIA>/<AGENZIA>_INDEX.md`
- Task personali/hobby/famiglia → `TODO_GENERALE.md` + opzionale `PERSONALE/TODO_PERSONALE.md`
- **Se ambiguo → CHIEDERE AD ATTI prima di scrivere**
- **MAI toccare file in `_TEMPLATE/`** per task reali
- **COLZANI è workspace separato** — non gestito in questo workspace myOcSync

### myJob — Struttura Progetti
```
FREELANCE/
  GET_ME_DIGITAL/   → agenzia (socio dal 2017 — riunioni settimanali) — GMD_INDEX.md
  SINAPPS/          → agenzia T PROJECT SRL (Marco Viganò) — BLANCONE, GOSETUPS, NANOSILK — SINAPPS_INDEX.md
  NEWU_SRL/         → agenzia (dal 2023 — landing page + QR, Plenitude) — NEWU_INDEX.md
  STUDIO_VISUAL/    → collaborazione occasionale (Mario Maglie) — STUDIO_VISUAL_INDEX.md
  DIRETTI/          → clienti diretti freelance
PERSONALE/          → personale/famiglia (ex ATTILIO_A_CASA) — TODO_PERSONALE.md
INGENIO_SOLUTION/   → società di Atti (non cliente)
EMAIL/              → gestione IMAP myjob@ingeniosolution.it
```

**NOTA:** COLZANI è gestito in workspace separato (non in myOcSync)

Registro agenzie: [[PERSONALE/lavori_a_casa/41_clienti_agenzie]]  
Convenzione creazione nuova agenzia: [[projects/myJob/CONVENTIONS]] sezione 10

### myJob — Email IMAP Workflow
- Cron **ogni ora** (solo lettura UNSEEN)
- Notifica esiti in **chat Telegram** (formato non tecnico, sintetico)
- Workflow: `00_inbox/` → `incoming_untriaged.md` (proposta) → conferma Atti → azione eseguita → `90_archive/`
- **REGOLA POST-CONFERMA:** dopo che Atti conferma un'azione e la si esegue → email in `90_archive/`, rimossa da `incoming_untriaged.md`, link all'eml archiviato nel task creato
- Non devono mai restare email in `incoming_untriaged.md` con azione già eseguita
- File `INBOX_WORKFLOW.md` con regole operative
- Format notifica: `Nuovo check email. Email nuove: N. Email in attesa: xxx`
- Quando sintetizzo azioni da fare, aggiungo sempre un link al contenuto originale della email e una % di confidenza sull'azione proposta; la useremo come metrica da migliorare prima dell'automatico.

### Stato Servizi (2026-09-06)
- **Cron email myJob** (`01d3cd46`): **disabled** da ~21 ago (rate limit, reset 27 ago). In attesa conferma Atti per riattivazione. Check manuali in attesa.
- **google_meet calendar_events**: non configurato (OAuth mancante) — check calendario via heartbeat in skip fino a configurazione.

### Modelli AI (aggiornato 2026-09-06)
- Runtime corrente: **zai/glm-4.7** (default_model)
- Cron `agentTurn`: modelli leggeri/nano preferiti per costi e tempi (vedi lezione timeout)
- Chat Telegram: modello di sessione corrente
- Messaggi vocali: OpenAI API
- myJob specifico: vedi `projects/myJob/` per override
- ⚠️ Sezione storicizzata (pre-2026-09): default "Claude Sonnet 4.6", fallback GPT nano/mini/5.5 — verificare se ancora validi prima di riusarli

---

## 👤 Preferenze Operative (Atti)

### Identità Assistente
- Nome: **IAcopo** (ingegnere informatico, simpatico, preciso, sicuro di sé)
- Lingua: **italiano**
- Timezone: **Europe/Rome** (UTC+1 inverno, UTC+2 estate)

### Comunicazione
- Email myJob: messaggi **non tecnici, sintetici**
- No UID nei riepiloghi, solo: mittente reale + azione proposta
- Telegram: diretto e collaborativo, no fumo
- Quando invio routine padel via cron, la formatto in modo **Telegram-friendly** (non flat file)

### MyAgenda — Slot liberi
- Quando Atti chiede uno slot libero, deve specificare se la verifica è per una call o per una città specifica.
- Se è una call, il luogo di partenza non conta molto.
- Se è una città specifica, devo considerare anche spostamenti e durata degli eventi successivi.
- Per slot nel calendario Colzani: parto dagli orari base Colzani, li incrocio col calendario Colzani e propongo solo slot interni a quegli orari, evitando eventi già presenti.
- Per slot personali: considero solo i giorni/slot dedicati al personale, ignorando gli orari Colzani e le attività già previste altrove.
- In generale, per attività lavorative l'orario di inizio di default difficilmente può andare oltre le 18.

### Workflow TODO
- Cliente diretto → aggiornare sia file cliente che `PERSONALE/README.md`
- Progetto agenzia (es. CEAM) → cartella agenzia (`FREELANCE/GET_ME_DIGITAL/`), non `DIRETTI/`
- Per i file personali di myJob vuole una riorganizzazione migliore: separare chiaramente lavoro Colzani, casa/tempo libero, hobby e checklist operative.
- Cron OpenClaw update check: ogni giorno alle 20:00, se c'è una nuova release, aggiorna/crea il TODO in `projects/myJob/TODO_GENERALE.md`.
- Scontrini benzinaio: quando arriva un audio/foto di uno scontrino del distributore, estrarre e annotare almeno distributore/codice punto vendita, nome stazione, indirizzo, numero scontrino o post number, data, orario, importo, volume e tipo di benzina; poi creare il TODO con scadenza **domani**.
- Checklist padel da censire: borsone, bibita, fascia braccio/spalla, orologio.
- Vuole anche una checklist padel separata per cose da ricordare prima di partita/torneo/allenamento, con data e ora di inserimento per ogni voce.
- Voci già dette per la checklist padel mentale: vibora con palla davanti, impugnatura continental, palla profonda che rimbalza dopo la linea; se è lontano dalla rete, a volte usare palla lenta per riconquistarla invece di tirare sempre forte.
- Vuole aggiungere una routine di allenamento individuale padel per dare continuità a smash, 3, volée, smorzata, risposta di rovescio, vibora e altri colpi.
- Nella checklist di concentrazione/preparazione partita padel vuole includere anche: provare i rovesci piatti forti.
- La routine padel inviata via cron va riformattata per Telegram, non incollata come file grezzo.

### Sessioni Telegram
- Stessa chat = stesso contesto (no reset automatico)
- Per separare: esplicito `NUOVO CONTESTO: <tema>` / `USA FILO: <tema>`

---

## 🔧 Informazioni Tecniche

### myJob Email
```
Host: mail.ingsoftware.it
IMAP: 993 | SMTP: 465
User: myjob@ingeniosolution.it
Pass: [in .env privato]
```

### Miotesoro — Vendor Mapping Critici
File: `projects/miotesoro-sheet-agent/docs/vendor-mapping.md` + Google Sheet CASA/PERSONALE

Mapping frequenti:
- Acqua & Sapone → Supermercati vari
- Osteria del Gelato → Uscite
- Alperia ~90-100€ → Corrente, altrimenti Gas
- OVS/D115 Carugo → Abbigliamento (Cura persona)
- Corsico HFB → Arredamento (IKEA)
- Pepco Cantù / Max Factory → Supermercati vari
- Shopsi Srl → Alimenti qualità (NaturaSì)
- Tri Malnatt → Alimenti qualità

### Claude Code
- Autenticato: account Pro
- Modelli: `sonnet` (4.6), `opus`, `haiku`
- CLI: `claude --model <model>`
- Default agenti non-Colzani: `anthropic/claude-sonnet-4-6`
- Agente Colzani: `github-copilot/claude-sonnet-4.6`

### TTS
- Provider: OpenAI TTS (`tts-1`)
- Voce default: `nova` (scelta da Atti)
- Lingua: italiano

---

## 📂 Progetti

I **progetti** sono contesti di lavoro separati con documentazione dedicata in `projects/<nome>/`.

**Registro canonico:** [progetti.md](progetti.md)

### Progetti Attivi

**miotesoro-sheet-agent** (`projects/miotesoro-sheet-agent/`)  
Copilot AI per gestione finanziaria personale. Registra entrate/uscite su Google Sheets (PERSONALE e CASA) con validazione automatica, controllo duplicati, integrità partita doppia.  
→ Usare per: registrazioni finanziarie, movimenti bancari, categorizzazione spese

**myOCcall** (`projects/myOCcall/`)  
Sistema per entrare automaticamente in videochiamate (Meet, Zoom, Teams), catturare audio, trascrivere con Whisper, produrre riassunto strutturato.  
→ Usare per: join automatico call, trascrizioni, sintesi meeting

**myJob** (`projects/myJob/`)  
Gestione task lavorativi e personali. Include: clienti (COLZANI, GMD, Sinapps, diretti), famiglia (ATTILIO_A_CASA), società di Atti (INGENIO_SOLUTION), email IMAP.  
→ Usare per: TODO generiche, clienti, azioni famiglia/lavoro, email triage

### Routing Richieste

- **"Registra spesa/entrata"** → miotesoro-sheet-agent
- **"Trascrivi questa call"** → myOCcall
- **"TODO" / "cliente X" / "email"** → myJob
- **Dubbio?** → Chiedere o consultare [progetti.md](progetti.md)

### Convenzioni Nuovi Progetti

Quando creare nuovo progetto:
1. Ambito distinto dai 3 esistenti
2. Richiede file di configurazione dedicati
3. Ha ciclo di vita autonomo

Procedura:
1. Creare cartella `projects/nomeprogetto/`
2. File obbligatori: `CHANGELOG.md`, `TODO.md`, `TECNICO.md`, `SINTESI.md`, `APPUNTI.md`
3. Aggiungere voce in [progetti.md](progetti.md)

---

## 🔄 Manutenzione

### Quando Aggiornare Questo File
- Lezioni importanti apprese (errori critici, pattern ripetuti)
- Nuove decisioni architetturali sui progetti
- Cambiamenti nelle preferenze di Atti
- Info tecniche che servono spesso

### Quando Usare File Giornalieri
- Log sessioni (`memory/YYYY-MM-DD-HHMM.md`)
- Note temporanee, work-in-progress
- Dettagli che non servono a lungo termine

### Heartbeat Review
Durante heartbeats periodici:
1. Leggere file giornalieri recenti
2. Identificare cosa va conservato a lungo termine
3. Aggiornare MEMORY.md con distillato
4. Rimuovere info obsolete

**Limite righe:** mantenere sotto 200 righe (auto-caricamento)

---

_Ultimo aggiornamento: 2026-09-12 (consolidate lezioni 07/09: timeout meteo sab-dom, segreti nei link firmati)_
