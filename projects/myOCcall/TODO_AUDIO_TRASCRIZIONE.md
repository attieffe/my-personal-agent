# TODO — applicare nuova procedura audio + trascrizione

Riferimento: `PROCEDURA_AUDIO_TRASCRIZIONE.md`

## Priorità alta

- [x] Aggiornare `scripts/call-start.sh`
  - [x] creare `audio/segments/`
  - [x] creare `transcripts/`
  - [x] avviare `ffmpeg` con segmentazione da 300 secondi
  - [x] scrivere log in `audio/recording.log`
  - [x] salvare PID come prima
  - [x] aggiornare `META.md` con modalità “segmenti MP3 da 300s”

- [x] Creare `scripts/call-audio-manifest.sh <call_dir>`
  - [x] elencare tutti i segmenti `audio/segments/*.mp3`
  - [x] calcolare dimensione file
  - [x] calcolare durata con `ffprobe`
  - [x] opzionale: calcolare volume max/mean con `volumedetect`
  - [x] generare `audio/manifest.tsv`
  - [x] marcare ogni segmento come `valid`, `silent`, `too_small`, `corrupt`, `missing`

- [x] Aggiornare `scripts/call-stop.sh`
  - [x] dopo stop ffmpeg, chiamare `call-audio-manifest.sh`
  - [x] verificare che esista almeno un segmento `valid`
  - [x] aggiornare `META.md` con numero segmenti generati/validi
  - [x] se zero segmenti validi, lasciare errore esplicito in `META.md`

- [x] Creare `scripts/call-transcribe-segments.sh <call_dir>`
  - [x] leggere `audio/manifest.tsv`
  - [x] processare tutti i segmenti `status=valid`
  - [x] salvare ogni output in `transcripts/segment-XXXX.txt`
  - [x] non fermare l’intera pipeline se un singolo segmento fallisce
  - [x] generare `trascrizione.txt` ordinata con header temporali per segmento
  - [x] restituire exit code non-zero se nessun segmento viene trascritto

- [x] Aggiornare `scripts/call-post.sh`
  - [x] non usare più direttamente `audio.mp3` come input primario
  - [x] chiamare `call-transcribe-segments.sh`
  - [x] generare `SINTESI.md` solo se `trascrizione.txt` supera controlli minimi
  - [x] scrivere in `META.md` se trascrizione completa/parziale/fallita

## Controlli anti-regressione

- [ ] Aggiungere check qualità trascrizione
  - [ ] segnalare contenuto sospetto se ripetitivo
  - [ ] segnalare frasi tipo “Sottotitoli creati dalla comunità…” come warning
  - [ ] bloccare sintesi automatica se la trascrizione è troppo corta o palesemente errata

- [ ] Aggiungere test locale con audio finto
  - [ ] generare 2-3 segmenti mp3 brevi
  - [ ] creare manifest
  - [ ] trascrivere tutti i segmenti
  - [ ] verificare merge finale in `trascrizione.txt`

- [ ] Aggiungere test su call reale breve
  - [ ] durata 6-7 minuti per forzare almeno 2 segmenti
  - [ ] verificare che siano prodotti più file segmentati
  - [ ] verificare che la trascrizione contenga testo da tutti i segmenti

## Pulizia compatibilità

- [ ] Decidere cosa fare di `audio.mp3`
  - [ ] opzione A: eliminarlo dalla pipeline primaria e tenerlo solo come file derivato opzionale
  - [ ] opzione B: generarlo concatenando i segmenti validi a fine call
  - [ ] raccomandazione: B, ma mai usarlo come fonte primaria per Whisper

- [ ] Aggiornare `PIPELINE.md`
  - [ ] sostituire riferimenti “audio.mp3 → Whisper” con “manifest segmenti → Whisper”
  - [ ] indicare `PROCEDURA_AUDIO_TRASCRIZIONE.md` come procedura autorevole

- [ ] Aggiornare `IMPL_TODO.md`
  - [ ] aggiungere blocco dedicato “Audio segmentato + trascrizione multi-segmento”
  - [ ] tracciare stato implementazione fino a test end-to-end

## Definition of Done

La modifica è completata quando:

- [ ] una call di almeno 6 minuti produce almeno 2 segmenti MP3;
- [ ] `audio/manifest.tsv` elenca tutti i segmenti;
- [ ] `trascrizione.txt` contiene testo proveniente da tutti i segmenti validi;
- [ ] `SINTESI.md` viene generata solo dopo trascrizione valida;
- [ ] in caso di audio sbagliato/silenzioso la pipeline fallisce chiaramente e non invia sintesi falsa.
