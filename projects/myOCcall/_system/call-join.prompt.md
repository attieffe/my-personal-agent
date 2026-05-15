---
description: >
  Prompt per l'agente che gestisce il join della call, il monitoring dei partecipanti
  e il rilevamento della condizione di exit. Usato in fase di esecuzione call in tempo reale.
  Algoritmo stabile — modificare solo su richiesta esplicita.
---

# call-join.prompt.md — Agente Join & Monitoring

## Scopo

Gestire le fasi 1–4 della pipeline call:
1. Preparazione (PulseAudio, cartella call)
2. Join browser (Google Meet / Teams / Zoom)
3. Monitoring partecipanti + speaker attribution live
4. Exit (exit condition raggiunta)

## Riferimenti

- Flow completo: `_system/PIPELINE.md`
- Stack tecnico e regole: `_system/TECNICO.md`
- Configurazione audio: `_system/PROCEDURES/audio-capture.md`
- Speaker attribution: `_system/PROCEDURES/speaker-attribution.md`
- Template META.md: `_system/SCHEMAS/meta-template.md`
- Configurazioni piattaforme (selettori DOM): `_knowledge/PLATFORMS.md`

## Input richiesto

```
piattaforma: meet | zoom | teams
url: <link completo della call>
orario_fine: <HH:MM> (opzionale — se assente, usare solo condizione "tutti usciti")
```

## Procedura

### 1. Pre-join

- [ ] Verificare PulseAudio attivo: `pactl info`
  - Se non attivo: `bash _system/scripts/start-audio.sh`
  - Verificare: `pactl list short sources | grep virtual_out`
- [ ] Creare cartella call: `bash _system/scripts/call-start.sh <platform> <url>`
- [ ] Copiare template checklist: `cp _system/SCHEMAS/pipeline-checklist.md "$CALL_DIR/PIPELINE.md"`
- [ ] Compilare META.md con info call (vedi template: `_system/SCHEMAS/meta-template.md`)

### 2. Join browser

- [ ] Usare il **browser tool di OpenClaw** (NON Playwright diretto)
  - Per Google Meet: vedi `_knowledge/PLATFORMS.md` → sezione Meet
  - Per Teams: vedi `_knowledge/PLATFORMS.md` → sezione Teams
  - Per Zoom: vedi `_knowledge/PLATFORMS.md` → sezione Zoom
- [ ] Verificare routing audio post-join: `_system/PROCEDURES/audio-capture.md` → "Routing audio post-join"
- [ ] Aggiornare META.md: `bot_join`, `bot_join_epoch_ms`

### 3. Monitoring

- Polling DOM ogni 60–90 secondi
- Loggare entrate/uscite in META.md (`Partecipanti`)
- Salvare eventi speaker in `$CALL_DIR/transcripts/speaker-events.jsonl`
  (schema: `_system/SCHEMAS/speaker-events-schema.md`)
- Aggiornare checklist `$CALL_DIR/PIPELINE.md`

### 4. Exit

**Exit condition (la prima delle due che si verifica):**
- Orario di fine previsto raggiunto (se fornito)
- Solo il bot rimasto da > 2 minuti (tutti gli altri partecipanti usciti)

- [ ] Eseguire `bash _system/scripts/call-stop.sh "$CALL_DIR"`
- [ ] Aggiornare META.md: `bot_leave`, `bot_leave_epoch_ms`

### 5. Handoff post-call

Al termine del join, invocare `_system/call-summarize.prompt.md` con `$CALL_DIR`.

## Output atteso

- `$CALL_DIR/META.md` compilato
- `$CALL_DIR/PIPELINE.md` (checklist aggiornata)
- `$CALL_DIR/audio/segments/` (segmenti MP3)
- `$CALL_DIR/transcripts/speaker-events.jsonl`
- `$CALL_DIR/active.lock` rimosso allo shutdown
