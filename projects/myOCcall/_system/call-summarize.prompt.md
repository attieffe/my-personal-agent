---
description: >
  Prompt per l'agente che gestisce la fase post-call: trascrizione Whisper,
  speaker attribution, generazione SINTESI.md, invio Telegram.
  Algoritmo stabile — modificare solo su richiesta esplicita.
---

# call-summarize.prompt.md — Agente Post-Call

## Scopo

Gestire la Fase 5 della pipeline: dall'audio registrato alla SINTESI.md inviata via Telegram.

## Riferimenti

- Flow completo: `_system/PIPELINE.md`
- Procedura audio: `_system/PROCEDURES/audio-capture.md`
- Speaker attribution: `_system/PROCEDURES/speaker-attribution.md`
- Quality checks: `_system/PROCEDURES/quality-checks.md`
- Template SINTESI: `_system/SCHEMAS/summary-template.md`
- Parlanti noti: `_knowledge/SPEAKERS.md`

## Input richiesto

```
call_dir: <path assoluto alla cartella call>
```

## Procedura

### 1. Quality checks (prima di trascrivere)

Eseguire i check da `_system/PROCEDURES/quality-checks.md`:
- Audio non silenzioso
- Segmenti validi nel manifest
- META.md compilato

Se check critici falliscono: notificare Atti e fermarsi.

### 2. Generazione manifest

```bash
bash _system/scripts/call-audio-manifest.sh "$CALL_DIR"
```

Verifica: `audio/manifest.tsv` deve contenere almeno 1 riga `valid`.

### 3. Trascrizione Whisper

```bash
bash _system/scripts/call-transcribe-segments.sh "$CALL_DIR"
```

- Output: `transcripts/segment-XXXX.txt` + `segment-XXXX.json` (verbose_json per timestamp)
- Aggregato: `trascrizione.txt`

### 4. Speaker attribution (se speaker-events.jsonl disponibile)

```bash
python _system/scripts/call-speaker-overlay.py "$CALL_DIR"
```

- Input: `transcripts/speaker-events.jsonl` + `transcripts/segment-XXXX.json`
- Output: `transcripts/transcript-events.jsonl` + `trascrizione_attribuita.md`
- Se speaker-events vuoto: skip attribution, nota in SINTESI

### 5. HUMAN.md check

Prima di generare la SINTESI, verificare se esiste `$CALL_DIR/HUMAN.md`:
- Se presente: integrare le note di Atti nella sezione "Note di Attilio" della SINTESI

### 6. Generazione SINTESI.md

Usare il template `_system/SCHEMAS/summary-template.md`.

- Fonte primaria: `trascrizione_attribuita.md` (se disponibile) o `trascrizione.txt`
- Integrare: META.md (partecipanti, durata), HUMAN.md (note Atti)
- Consultare `_knowledge/SPEAKERS.md` per matching nomi → ruoli/contesto
- Estrarre azioni/follow-up e presentarle ad Atti per conferma

### 7. Azioni IT — conferma ad Atti

Prima di scrivere TODO:
- Presentare ad Atti la lista di azioni estratte dalla SINTESI
- Attendere conferma/rettifica prima di aggiornare file TODO

### 8. Invio Telegram

```bash
bash _system/scripts/call-post.sh "$CALL_DIR"
```

Se invio fallisce: salvare in `$CALL_DIR/sintesi-pending-send.txt`.

## Output atteso

- `$CALL_DIR/trascrizione.txt`
- `$CALL_DIR/transcripts/transcript-events.jsonl`
- `$CALL_DIR/trascrizione_attribuita.md`
- `$CALL_DIR/SINTESI.md`
- Messaggio Telegram inviato ad Atti

## Messaggio di conferma ad Atti

```
✅ Call registrata e trascritta
📁 Cartella: calls/YYYYMMDD HHMM platform
⏱️ Durata: HH:MM
📊 Segmenti audio: X validi / Y totali
📝 Trascrizione: XXX parole
```
