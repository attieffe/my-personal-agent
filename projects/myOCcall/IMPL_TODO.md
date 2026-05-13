# IMPL_TODO — myOCcall Pipeline Implementation

> File di tracciamento per l'implementazione completa della pipeline.
> Aggiornare questo file ad ogni sessione di lavoro: spuntare i task completati, aggiungere note tecniche.
> L'obiettivo è poter riprendere da qualsiasi punto senza perdere contesto.

---

## Come riprendere da una sessione interrotta

1. Leggi `PLAN.md` per capire l'architettura generale
2. Leggi questo file (`IMPL_TODO.md`) per vedere esattamente dove si era arrivati
3. Verifica che PulseAudio sia attivo: `pactl info`
4. Se non attivo: `bash ~/.openclaw/workspace/projects/myOCcall/scripts/start-audio.sh`
5. Riprendi dal primo task `[ ]` non completato

---

## BLOCCO A — Infrastruttura dati ✅ (già in PLAN.md)

- [x] Struttura cartella `data/YYYYMMDD HHMM <platform>/` definita
- [x] Formato META.md definito
- [x] PulseAudio null sink `virtual_out` attivo
- [x] Playwright Chromium installato e funzionante

---

## BLOCCO B — Script di supporto

> ✅ Gli script B1-B5 erano già presenti da sessione precedente:
> - `call-start.sh` = B1 + B2 (init + avvio ffmpeg)
> - `call-stop.sh` = B3 + B5 (stop graceful + finalizzazione)
> - `call-log-join.sh` = log join bot
> - `call-log-participant.sh` = B4 (log partecipanti, usa Python per parsing tabella)

- [x] **B1** — `scripts/call-init.sh <platform> <url>`
  - Crea cartella `data/$(date +'%Y%m%d %H%M') <platform>/`
  - Crea `META.md` con piattaforma, URL, stato "in corso", timestamp join (Europe/Rome)
  - Output: path cartella call (usato dagli step successivi)
  - _Note tecniche:_ usare `TZ=Europe/Rome date +'%Y%m%d %H%M'` per il nome cartella

- [x] **B2** — `scripts/call-start.sh` — avvio ffmpeg con PID, verifica sink PulseAudio
- [x] **B3** — `scripts/call-stop.sh` — stop graceful SIGTERM + attesa max 10s
- [x] **B4** — `scripts/call-log-participant.sh` — log partecipanti con Python parser tabella MD
- [x] **B5** — `scripts/call-stop.sh` — finalizzazione META.md + verifica integrità audio

---

## BLOCCO C — Join automatico (browser)

### C1 — Google Meet
- [x] **C1.1** — Navigare al link Meet con Playwright (`call-join-meet.js`)
- [x] **C1.2** — Gestire schermata preview (disattivare mic/cam, nome "Attilio F.")
- [x] **C1.3** — Cliccare "Partecipa" / "Chiedi di partecipare"
- [x] **C1.4** — Rilevare ammissione in sala d'attesa vs accesso diretto (polling su "in attesa")
- [x] **C1.5** — Documentare selettori CSS in `notes/call-configs.md`
- [ ] **C1.6** — Test con call reale o link di test ← **PRIMO TEST DA FARE**

### C2 — Zoom (opzionale, dopo Meet)
- [ ] **C2.1** — Aprire link web Zoom (no app)
- [ ] **C2.2** — Gestire waiting room
- [ ] **C2.3** — Documentare selettori in `notes/call-configs.md`

### C3 — Teams (opzionale, dopo Meet)
- [ ] **C3.1** — Accesso ospite o account Microsoft
- [ ] **C3.2** — Gestire lobby Teams
- [ ] **C3.3** — Documentare selettori in `notes/call-configs.md`

---

## BLOCCO D — Monitoring partecipanti

- [ ] **D1** — Polling ogni 60-90s sul badge "People" (Meet)
- [ ] **D2** — Rilevare entrate: chiamare `call-log-participant.sh join`
- [ ] **D3** — Rilevare uscite: chiamare `call-log-participant.sh leave`
- [ ] **D4** — Exit condition: se partecipanti = 1 (solo bot) per > 2 minuti → avviare exit flow
- [ ] **D5** — Watchdog: verificare ogni 60s che ffmpeg stia ancora scrivendo (file size cresce)

---

## BLOCCO E — Flow post-call (indipendente)

- [x] **E1** — `scripts/call-transcribe-segments.sh <call_dir>`
  - Verifica manifest segmenti e trascrive solo `status=valid`
  - Chiama Whisper (skill `openai-whisper-api`) sui segmenti validi
  - Salva output in `transcripts/` e `trascrizione.txt`
  - Aggiorna META.md: `trascrizione: OK` / parziale / fallita

- [x] **E2** — `scripts/call-post.sh` — genera SINTESI.md da trascrizione + template strutturato
- [x] **E3** — `scripts/call-post.sh` — invio via `openclaw sessions send main` con fallback file

---

## BLOCCO D — Monitoring partecipanti

- [x] **D1** — `scripts/call-monitor.sh` — polling ogni 60s su browser-status.json
- [x] **D2** — rileva variazioni conteggio partecipanti e logga
- [x] **D3** — verifica watchdog ffmpeg (file audio cresce)
- [x] **D4** — exit condition: partecipanti ≤ 1 per EXIT_GRACE_MIN (default 2min)
- [x] **D5** — hard timeout 4 ore (sicurezza)

---

## BLOCCO F — Orchestratore end-to-end

- [x] **F1** — `scripts/call-orchestrate.sh <platform> <url> [--no-post]`
  - Fase 1: call-start.sh (init + ffmpeg)
  - Fase 2: call-log-join.sh
  - Fase 3: call-join-meet.js (browser join)
  - Fase 4: call-monitor.sh (loop)
  - Fase 5: call-stop.sh (stop + finalize)
  - Fase 6: call-post.sh (whisper + sintesi + telegram)

- [ ] **F2** — Skill OpenClaw `call-summarizer` (SKILL.md dedicato) ← **DOPO test end-to-end**

---

## BLOCCO G — Test plan

Vedi sezione **TEST PLAN** sotto.

---

## BLOCCO H — Audio segmentato + trascrizione multi-segmento

> Revisione dopo errore reale: la pipeline ha trascritto un file audio non corretto invece dell'audio call-only. Nuova procedura in `PROCEDURA_AUDIO_TRASCRIZIONE.md`; checklist applicativa in `TODO_AUDIO_TRASCRIZIONE.md`.

- [x] **H1** — aggiornare `call-start.sh` per registrare segmenti MP3 da 300s in `audio/segments/`
- [x] **H2** — creare `call-audio-manifest.sh` per validare tutti i segmenti e generare `audio/manifest.tsv`
- [x] **H3** — aggiornare `call-stop.sh` per generare manifest e fallire se zero segmenti validi
- [x] **H4** — creare `call-transcribe-segments.sh` per trascrivere tutti i segmenti validi
- [x] **H5** — aggiornare `call-post.sh` per usare il manifest, non un singolo `audio.mp3`
- [ ] **H6** — aggiungere controlli qualità anti-trascrizione falsa/ripetitiva
- [ ] **H7** — test end-to-end con call > 6 minuti e almeno 2 segmenti

---

## TEST PLAN

### T1 — Test unitari script

| Test | Comando | Esito atteso |
|------|---------|--------------|
| T1.1 | `bash call-init.sh meet https://meet.google.com/xxx` | Cartella `data/YYYYMMDD HHMM meet/` creata, META.md presente |
| T1.2 | `bash call-start.sh meet <url>` | ffmpeg avviato, `audio/segments/segment-0000.mp3` cresce dopo 3s |
| T1.3 | `bash call-stop.sh <call_dir>` | ffmpeg terminato gracefully, segmenti intatti |
| T1.4 | `bash call-log-participant.sh <call_dir> "Mario Rossi" join` | Riga aggiunta a META.md con timestamp |
| T1.5 | `bash call-finalize.sh <call_dir>` | META.md aggiornato con leave time e durata |

### T2 — Test browser (Meet)

| Test | Azione | Esito atteso |
|------|--------|--------------|
| T2.1 | Aprire link Meet di test | Browser si apre, schermata preview visibile |
| T2.2 | Join con nome "Attilio F." | Partecipante appare nella call con nome corretto |
| T2.3 | Verificare che webcam sia spenta | Nessun video trasmesso |
| T2.4 | Verificare che mic sia spento | Nessun audio trasmesso agli altri |
| T2.5 | Leave automatico | Browser esce dalla call correttamente |

### T3 — Test audio + trascrizione

| Test | Azione | Esito atteso |
|------|--------|--------------|
| T3.1 | Join call + parlare 30s | almeno un segmento MP3 contiene audio riconoscibile |
| T3.2 | Whisper sui segmenti validi | `trascrizione.txt` contiene testo corretto |
| T3.3 | Generazione SINTESI.md | File contiene argomenti, partecipanti, orari |

### T4 — Test end-to-end (integrazione)

| Test | Azione | Esito atteso |
|------|--------|--------------|
| T4.1 | Call completa 5 minuti | Tutti i file generati correttamente |
| T4.2 | Disconnessione inaspettata del browser | ffmpeg continua a girare, file audio non corrotto |
| T4.3 | Tutti escono → exit automatico | Bot esce dopo 2 min da solo |
| T4.4 | SINTESI.md arriva su Telegram | Messaggio ricevuto con contenuto corretto |

### T5 — Test robustezza

| Test | Scenario | Esito atteso |
|------|----------|--------------|
| T5.1 | PulseAudio non attivo al join | Script rileva errore, logga in META.md, non crea file audio vuoto |
| T5.2 | Call finisce prima del monitoring | Segmenti salvati, META.md aggiornato, flow post-call funziona |
| T5.3 | Whisper fallisce (API error) | Errore loggato in META.md, segmenti audio intatti per retry |

---

## Log sessioni di lavoro

| Data | Sessione | Completati | Note |
|------|----------|------------|------|
| 2026-05-13 | Setup TODO + piano | — | Creato questo file |
| 2026-05-13 | Implementazione pipeline | B1-B5 (già esistenti), C1, D1-D5, E1-E3, F1 | Aggiunti: call-join-meet.js, call-monitor.sh, call-orchestrate.sh; aggiornato call-post.sh con Telegram |
| 2026-05-13 | Segmentazione audio + trascrizione multi-segmento | H1-H5 | Nuovi script: call-audio-manifest.sh, call-transcribe-segments.sh; post-call ora lavora sul manifest |
