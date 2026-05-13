# MEMORY.md - Long-Term Memory

_Your curated memory. The distilled essence of what you've learned._

Le prime 200 righe di questo file vengono caricate automaticamente in ogni sessione principale. Mantienilo conciso.

Per dettagli giornalieri raw → vedi `memory/YYYY-MM-DD.md`  
Per progetti specifici → vedi [progetti.md](progetti.md)

---

## 🎯 Lezioni Critiche

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
- Email inoltrate: mittente rilevante = **ultimo nella catena**, non il forwarder

### Routing Organizzativo myJob
- **REGOLA FERREA:** `COLZANI/` ≠ `ATTILIO_A_CASA/`
- Clienti diretti, agenzie, famiglia, impegni personali → **MAI in COLZANI**
- TODO cliente aggiornato → **SEMPRE aggiornare anche TODO Attilio a casa** quando pertinente

---

## 🏗️ Decisioni Architetturali

### myOCcall — Pipeline Audio
- Audio segmentato: `ffmpeg` chunk ogni **300 secondi** → `audio/segments/*.mp3`
- `audio/manifest.tsv` per tracciare segmenti validi
- Trascrizione multi-segmento → `transcripts/` → merge in `trascrizione.txt`
- Controlli anti-trascrizione falsa prima della sintesi
- Stack: PulseAudio + ffmpeg + null sink (`virtual_out`) + Whisper API
- Path call: `/home/openclaw/.openclaw/workspace/projects/myOCcall/data/YYYYMMDD HHMM <platform>/`

### myJob — Struttura Progetti
```
COLZANI/          → cliente principale (TEAM, AS400, CONSULENTI)
GET_ME_DIGITAL/   → agenzia (progetti in PROGETTI/)
SINAPPS/          → agenzia
DIRETTI/CLIENTI/  → clienti diretti (es. Davide Rizzi, Silvia Migliaccio)
ATTILIO_A_CASA/   → personale/famiglia
INGENIO_SOLUTION/ → società di Atti (non cliente)
EMAIL/            → gestione IMAP myjob@ingeniosolution.it
```

### myJob — Email IMAP Workflow
- Cron **ogni ora** (solo lettura UNSEEN)
- Notifica esiti in **chat Telegram** (formato non tecnico, sintetico)
- Workflow: `00_inbox/` → `01_to-be-defined/` → triage
- File `INBOX_WORKFLOW.md` con regole operative
- Format notifica: `Nuovo check email. Email nuove: N. Email in attesa: xxx`

### Modelli AI
- Default globale: **Claude Sonnet 4.6**
- Fallback: GPT nano → GPT mini → GPT 5.5
- Chat Telegram: Claude Code CLI
- Messaggi vocali: OpenAI API
- myJob specifico: vedi `projects/myJob/` per override

---

## 👤 Preferenze Operative (Atti)

### Identità Assistente
- Nome: **AttiBot** (ingegnere informatico, simpatico, preciso, sicuro di sé)
- Lingua: **italiano**
- Timezone: **Europe/Rome** (UTC+1 inverno, UTC+2 estate)

### Comunicazione
- Email myJob: messaggi **non tecnici, sintetici**
- No UID nei riepiloghi, solo: mittente reale + azione proposta
- Telegram: diretto e collaborativo, no fumo

### Workflow TODO
- Cliente diretto → aggiornare sia file cliente che `ATTILIO_A_CASA/README.md`
- Progetto agenzia (es. CEAM) → cartella agenzia (`GET_ME_DIGITAL/`), non `DIRETTI/`

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
File: `projects/miotesoro/docs/vendor-mapping.md` + Google Sheet CASA/PERSONALE

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

### TTS
- Provider: OpenAI TTS (`tts-1`)
- Voce default: `nova` (scelta da Atti)
- Lingua: italiano

---

## 📂 Progetti

I **progetti** sono contesti di lavoro separati con documentazione dedicata in `projects/<nome>/`.

**Registro canonico:** [progetti.md](progetti.md)

### Progetti Attivi

**miotesoro** (`projects/miotesoro/`)  
Copilot AI per gestione finanziaria personale. Registra entrate/uscite su Google Sheets (PERSONALE e CASA) con validazione automatica, controllo duplicati, integrità partita doppia.  
→ Usare per: registrazioni finanziarie, movimenti bancari, categorizzazione spese

**myOCcall** (`projects/myOCcall/`)  
Sistema per entrare automaticamente in videochiamate (Meet, Zoom, Teams), catturare audio, trascrivere con Whisper, produrre riassunto strutturato.  
→ Usare per: join automatico call, trascrizioni, sintesi meeting

**myJob** (`projects/myJob/`)  
Gestione task lavorativi e personali. Include: clienti (COLZANI, GMD, Sinapps, diretti), famiglia (ATTILIO_A_CASA), società di Atti (INGENIO_SOLUTION), email IMAP.  
→ Usare per: TODO generiche, clienti, azioni famiglia/lavoro, email triage

### Routing Richieste

- **"Registra spesa/entrata"** → miotesoro
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

_Ultimo aggiornamento: 2026-05-14_
