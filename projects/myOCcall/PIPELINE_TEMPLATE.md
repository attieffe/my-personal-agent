# PIPELINE — Call [DATA ORA PIATTAFORMA]

> **Checklist operativa per questa registrazione.**  
> Spunta `[x]` ogni task completato. Aggiungi note operative in fondo se necessario.

**Procedura audio/trascrizione:** [../../PROCEDURA_AUDIO_TRASCRIZIONE.md](../../PROCEDURA_AUDIO_TRASCRIZIONE.md)  
**Reference flow completo:** [../../PIPELINE.md](../../PIPELINE.md)

---

## Stato Generale

- [ ] Pre-join completato
- [ ] Join effettuato
- [ ] Monitoring attivo
- [ ] Exit completato
- [ ] Post-call completato

---

## Fase 1 — Pre-join

**Script:** `call-start.sh <platform> <url>`

- [ ] Cartella call creata (`data/YYYYMMDD HHMM platform/`)
- [ ] `META.md` generato con piattaforma, URL, stato "in corso"
- [ ] Sottocartelle create: `audio/segments/`, `transcripts/`
- [ ] PulseAudio attivo: `pactl info` risponde
- [ ] Source `virtual_out.monitor` esiste: `pactl list short sources | grep virtual_out`
- [ ] ffmpeg avviato in background (segmenti 300s)
- [ ] PID ffmpeg salvato in `ffmpeg.pid`
- [ ] Verifica primo segmento creato dopo 3-5s: `ls -lh audio/segments/`

---

## Fase 2 — Join

**Script:** `call-join-meet.js <call_dir> <url>` (o equivalente per zoom/teams)

- [ ] Browser aperto su URL call
- [ ] Webcam disabilitata / input video disattivato (nessun video trasmesso)
- [ ] Microfono disabilitato (nessun audio trasmesso)
- [ ] Nome visualizzato: **"Attilio F."**
- [ ] Click "Partecipa" / join eseguito
- [ ] Orario join loggato in `META.md` (timezone Europe/Rome)
- [ ] Audio browser → `virtual_out` verificato: `pactl list sink-inputs | grep -i chromium`
- [ ] Livello audio non silenzioso: `ffmpeg -f pulse -i virtual_out.monitor -t 3 -filter:a volumedetect -f null - 2>&1 | grep max_volume`

---

## Fase 3 — Monitoring (loop ogni 60s)

**Script:** `call-monitor.sh <call_dir>`

- [ ] Polling partecipanti attivo (`browser-status.json` aggiornato)
- [ ] Log entrate/uscite in `META.md` con timestamp
- [ ] Log cronologia call completo disponibile o ricostruibile: join browser, start/end segmenti, ingressi/uscite, partecipanti esterni
- [ ] Watchdog audio: segmenti MP3 crescono nel tempo
- [ ] Exit condition monitorata: solo bot per > 2 minuti → trigger exit
- [ ] Hard timeout 4h configurato (sicurezza anti-hang)

---

## Fase 4 — Exit

**Script:** `call-stop.sh <call_dir>`

- [ ] ffmpeg fermato gracefully (SIGTERM, non SIGKILL)
- [ ] Browser chiuso
- [ ] Orario leave loggato in `META.md` (Europe/Rome)
- [ ] Durata totale calcolata e loggata
- [ ] Manifest segmenti generato: `audio/manifest.tsv`
- [ ] Almeno 1 segmento `status=valid` verificato
- [ ] Se zero segmenti validi → errore esplicito in `META.md`

---

## Fase 5 — Post-call

> Può essere eseguita in differita. Richiede solo `audio/manifest.tsv` e `META.md`.

**Script:** `call-post.sh <call_dir>`

### 5.1 — Trascrizione

- [ ] Whisper chiamato su tutti i segmenti `status=valid`
- [ ] Output salvati in `transcripts/segment-XXXX.txt`
- [ ] `trascrizione.txt` aggregata creata con header temporali
- [ ] Controlli qualità superati:
  - [ ] Almeno 10 parole totali
  - [ ] Non ripetitiva (ratio unique/total < 3)
  - [ ] Non contiene boilerplate ("Sottotitoli creati dalla comunità…")
- [ ] `META.md` aggiornato: trascrizione ✓ / parziale / fallita

### 5.2 — Sintesi

- [ ] `SINTESI.md` generata con template strutturato:
  - [ ] Info call (piattaforma, URL, orari, durata)
  - [ ] Cronistoria sintetica (join browser, segmenti, variazioni partecipanti)
  - [ ] Contesto e inizio riunione
  - [ ] Argomenti trattati
  - [ ] Decisioni prese
  - [ ] Partecipanti presenti + durata approssimativa di partecipazione se ricostruibile
  - [ ] Estratto trascrizione (solo frasi utili; escludere battute, commenti, parti non comprese)
  - [ ] `META.md` aggiornato: sintesi ✓

### 5.3 — Invio

- [ ] SINTESI.md inviata ad Atti via Telegram
- [ ] Se invio fallisce → salvata in `sintesi-pending-send.txt`

---

## Note Operative

_(Aggiungi qui anomalie, problemi tecnici, workaround applicati, osservazioni specifiche di questa call)_

**Esempio:**
- `[HH:MM]` PulseAudio source non trovato → riavviato con `start-audio.sh`
- `[HH:MM]` Whisper timeout su segment-0003 → saltato, trascrizione parziale
- `[HH:MM]` Browser crash dopo 45min → riavviato manualmente, audio non perso

---

## Troubleshooting Rapido

**PulseAudio non attivo:**
```bash
bash ../../scripts/start-audio.sh
pactl info
```

**ffmpeg non scrive segmenti:**
```bash
ps aux | grep ffmpeg
ls -lh audio/segments/
tail -f audio/recording.log
```

**Audio silenzioso:**
```bash
pactl list sink-inputs | grep -i chromium
pactl move-sink-input <ID> virtual_out
```

**Whisper fallisce:**
```bash
# Verifica connessione API
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Retry manuale singolo segmento
bash ../../scripts/call-transcribe-segments.sh .
```
