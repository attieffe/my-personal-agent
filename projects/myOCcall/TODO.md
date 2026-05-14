# TODO — myOCcall

Elenco di feature, miglioramenti e task tecnici per far evolvere il sistema.

> **Scope:** Questo file traccia cosa migliorare/costruire nel progetto. Per la checklist operativa di ogni singola call, vedi `PIPELINE_TEMPLATE.md`.

---

## Setup & Piattaforme

- [ ] **Join automatico Google Meet** — test end-to-end con call reale (C1.6)
- [ ] **Join automatico Zoom** — implementare browser flow (C2)
- [ ] **Join automatico Teams** — implementare browser flow (C3)
- [ ] **Configurazione credenziali** — account Google/Microsoft per le piattaforme

---

## Feature & Miglioramenti

- [ ] **Attribuzione parlante via active speaker timeline** — identificare chi parla quando usando eventi DOM Meet/Teams + timestamp audio/Whisper (attribuzione interventi per parlante in SINTESI.md)
- [ ] **Skill OpenClaw dedicata** — `call-summarizer` con SKILL.md per invocare l'agente con semplice comando
- [ ] **Riconoscimento automatico piattaforma** — parsing URL per determinare meet/zoom/teams
- [ ] **Dashboard chiamate** — visualizzazione storico call con filtri e ricerca
- [ ] **Retry automatico Whisper** — se API fallisce, ritentare con exponential backoff
- [ ] **Concatenazione segmenti** — generare `audio.mp3` completo a fine call (opzionale, non fonte primaria)

---

## Bug & Fix

- [ ] **Watchdog audio più robusto** — verificare crescita file nel tempo, non solo size ≠ 0 (call-monitor.sh)
- [ ] **Gestione errori PulseAudio** — fallire esplicitamente se virtual_out.monitor non esiste al join
- [ ] **Timeout Whisper** — evitare hang infinito su segmenti corrotti
- [ ] **Validazione URL** — bloccare URL malformati prima del join

---

## Controlli Qualità

- [ ] **Check qualità trascrizione avanzato**
  - [ ] Rilevare contenuto ripetitivo (loop Whisper)
  - [ ] Bloccare frasi boilerplate ("Sottotitoli creati dalla comunità…")
  - [ ] Soglia minima parole per accettare trascrizione
- [ ] **Alert su audio silenzioso** — notificare se tutti i segmenti sono marcati `silent`
- [ ] **Confronto durata call vs durata audio** — warning se mismatch significativo

---

## Test & Validazione

- [ ] **Test unitari script** (T1)
  - [ ] call-start.sh crea cartella e avvia ffmpeg
  - [ ] call-stop.sh ferma ffmpeg senza corrompere segmenti
  - [ ] call-audio-manifest.sh genera manifest corretto
  - [ ] call-transcribe-segments.sh trascrive tutti i segmenti validi
- [ ] **Test browser Meet** (T2)
  - [ ] Join automatico funzionante
  - [ ] Webcam/mic disabilitati
  - [ ] Nome "Attilio F." visibile
- [ ] **Test audio + trascrizione** (T3)
  - [ ] Segmenti contengono audio riconoscibile
  - [ ] Whisper produce trascrizione corretta
  - [ ] SINTESI.md generata con contenuto valido
- [ ] **Test end-to-end** (T4)
  - [ ] Call completa 6+ minuti → almeno 2 segmenti MP3
  - [ ] Exit automatico quando tutti escono
  - [ ] SINTESI.md arriva su Telegram
- [ ] **Test robustezza** (T5)
  - [ ] Gestione PulseAudio non attivo
  - [ ] Call finita prima del monitoring
  - [ ] Whisper API fallisce → retry/log errore

---

## Implementazione in Corso

> Task tecnici specifici attualmente in sviluppo. Spostare in "Completato" quando finiti.

- [ ] **Piano sviluppo: speaker attribution v1 (Meet first)**
  - [ ] Analizzare DOM Google Meet durante una call reale e identificare selettori/attributi affidabili per active speaker (lampadina/bordo/aria-label/stato tile)
  - [ ] Salvare una timeline `speaker-events.jsonl` con eventi normalizzati: `wall_ts`, `call_sec`, `speaker_name`, `event=start|end|switch`, `source=meet_dom`, `confidence`
  - [ ] Allineare clock: registrare in `META.md` `recording_start_wall_ts`, `ffmpeg_start_wall_ts`, `bot_join_wall_ts` e usare `call_sec` come tempo canonico relativo alla registrazione
  - [ ] Estendere `audio/manifest.tsv` con timestamp assoluti/relativi già presenti (`start_sec`, `duration_sec`) e verificare che rappresentino l'offset reale rispetto a inizio registrazione
  - [ ] Cambiare trascrizione Whisper da `response_format=text` a JSON/verbose JSON con segment timestamps, salvando `transcripts/segment-XXXX.json` oltre al `.txt`
  - [ ] Generare `transcripts/transcript-events.jsonl` con eventi normalizzati: `call_start_sec`, `call_end_sec`, `text`, `segment_file`, `whisper_confidence/opzionale`
  - [ ] Implementare overlay `speaker-events.jsonl` ↔ `transcript-events.jsonl`: assegnare ogni frase al parlante con overlap temporale maggiore, con fallback `Sconosciuto`/`Ambiguo`
  - [ ] Produrre `trascrizione_attribuita.md` con formato `[HH:MM:SS] Nome: testo`
  - [ ] Aggiornare `call-post.sh` e `SINTESI.md` per usare la trascrizione attribuita nel “Dettaglio per parlante”
  - [ ] Testare casi difficili: due persone che parlano sopra, cambio speaker rapido, DOM senza nome visibile, captions disattivate, audio silenzioso

- [x] **Segmentazione audio 300s** (H1-H5)
  - [x] call-start.sh registra segmenti in `audio/segments/`
  - [x] call-audio-manifest.sh valida segmenti
  - [x] call-transcribe-segments.sh trascrive manifest
  - [x] call-post.sh usa manifest, non singolo audio.mp3
- [x] **Fix script**
  - [x] call-post.sh — corretto regex `count=0` → `count=1`
  - [x] call-monitor.sh — migliorato watchdog crescita file audio
- [x] **Riorganizzazione documentazione**
  - [x] TODO.md consolidato (BACKLOG + IMPL_TODO + TODO_AUDIO eliminati)
  - [x] PIPELINE_TEMPLATE.md creato (checklist operativa per ogni call)
  - [x] docs/AGENT_RUNBOOK.md creato (guida operativa agente)

---

## Completato ✅

- [x] Analisi fattibilità stack Linux headless
- [x] Installazione PulseAudio + ffmpeg
- [x] Configurazione null sink `virtual_out`
- [x] Test cattura audio ffmpeg → OK
- [x] Script `start-audio.sh` (avvio idempotente PulseAudio)
- [x] Autostart PulseAudio in `.bashrc`
- [x] Playwright Chromium installato
- [x] Audio browser → virtual_out verificato (parec -6.2 dB)
- [x] Struttura cartella `data/YYYYMMDD HHMM platform/` definita
- [x] Formato META.md definito
- [x] Script completi: call-start.sh, call-stop.sh, call-join-meet.js, call-monitor.sh
- [x] Flow post-call: trascrizione + sintesi + Telegram
- [x] Procedura audio segmentato (PROCEDURA_AUDIO_TRASCRIZIONE.md)

---

## Come Contribuire

1. Aggiungi nuove feature/idee nelle sezioni appropriate
2. Sposta task da "Setup/Feature" a "In Corso" quando inizi a lavorarci
3. Spunta `[x]` e sposta in "Completato" quando finito
4. Aggiungi note tecniche in `APPUNTI.md` se necessario
