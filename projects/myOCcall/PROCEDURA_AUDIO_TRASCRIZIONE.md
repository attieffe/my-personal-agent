# PROCEDURA AUDIO + TRASCRIZIONE — myOCcall

Data revisione: 2026-05-13

Questa procedura sostituisce il flusso “un solo `audio.mp3` → Whisper”.
Serve a evitare errori come quello visto nella call: file audio sbagliato/contaminato mandato in trascrizione mentre il file corretto era `audio-call-only.mp3`.

## Obiettivo

Per ogni call, il sistema deve:

1. registrare l’audio reale della call in modo verificabile;
2. salvarlo in segmenti MP3 da 300 secondi;
3. creare un manifest dei segmenti;
4. trascrivere **tutti** i segmenti validi, in ordine;
5. unire le trascrizioni in `trascrizione.txt`;
6. fallire in modo esplicito se nessun segmento valido è disponibile;
7. non usare mai automaticamente un file audio “di fallback” se non supera i controlli minimi.

## Decisione tecnica

Sì: è corretto far campionare/ruotare `ffmpeg` ogni **300 secondi**.

Vantaggi:

- se una trascrizione fallisce, si ritenta solo il segmento;
- si capisce subito quale parte della call è silenziosa o corrotta;
- i file sono più piccoli e più facili da inviare/processare;
- la pipeline non dipende da un unico MP3 lungo;
- Whisper/processi API lavorano meglio su chunk prevedibili.

## Struttura cartella call

Ogni call deve produrre questa struttura:

```text
projects/myOCcall/data/YYYYMMDD HHMM <platform>/
  META.md
  audio/
    segments/
      segment-0001.mp3
      segment-0002.mp3
      segment-0003.mp3
      ...
    manifest.tsv
    recording.log
  transcripts/
    segment-0001.txt
    segment-0002.txt
    segment-0003.txt
    ...
  trascrizione.txt
  SINTESI.md
```

`audio.mp3` può essere mantenuto solo come compatibilità/derivato opzionale, ma **non deve più essere la fonte primaria della trascrizione**.

## Registrazione audio

### Fonte corretta

La fonte deve essere l’audio in uscita della call, non audio generico di sistema.

Fonte prevista attuale:

```text
virtual_out.monitor
```

Prima di iniziare la registrazione bisogna verificare:

- `pactl info` risponde;
- il source `virtual_out.monitor` esiste;
- Chromium/Meet viene instradato verso `virtual_out`;
- il livello audio non è completamente silenzioso quando la call ha audio.

### Segmentazione ffmpeg

`ffmpeg` deve scrivere segmenti da 300 secondi:

```bash
ffmpeg \
  -hide_banner -loglevel warning -nostdin -y \
  -f pulse -i virtual_out.monitor \
  -ac 1 -ar 44100 -b:a 128k \
  -f segment \
  -segment_time 300 \
  -reset_timestamps 1 \
  "audio/segments/segment-%04d.mp3"
```

Nota: la numerazione ffmpeg parte di solito da `0000`; la pipeline può accettare `segment-0000.mp3` oppure rinominare a `segment-0001.mp3`. L’importante è ordinare lessicograficamente/numericamente.

## Manifest segmenti

A fine call, o durante il monitoraggio, deve essere generato `audio/manifest.tsv`.

Formato:

```tsv
index	file	start_sec	duration_sec	size_bytes	status	note
0001	audio/segments/segment-0001.mp3	0	300	1234567	valid	
0002	audio/segments/segment-0002.mp3	300	300	1234567	valid	
0003	audio/segments/segment-0003.mp3	600	81	456789	valid	last segment
```

Status ammessi:

- `valid` — file presente, durata > 0, dimensione > soglia minima;
- `silent` — file tecnicamente valido ma probabilmente silenzioso;
- `too_small` — file troppo piccolo;
- `corrupt` — ffprobe/ffmpeg non riesce a leggerlo;
- `missing` — atteso ma assente.

## Validazione segmenti

Per ogni segmento:

1. verificare che il file esista;
2. verificare `size_bytes > 0`;
3. leggere durata con `ffprobe`;
4. opzionale ma consigliato: misurare volume con `volumedetect`;
5. marcare `valid` solo se supera i controlli.

Se tutti i segmenti risultano invalidi, la pipeline deve fermarsi con errore chiaro:

```text
ERRORE: nessun segmento audio valido da trascrivere
```

Non deve generare una trascrizione finta, vuota o da file sbagliato.

## Trascrizione

La trascrizione lavora su `audio/manifest.tsv`, non su un singolo `audio.mp3`.

Per ogni riga `status=valid`:

1. chiamare Whisper sul file segmento;
2. salvare output in `transcripts/segment-XXXX.txt`;
3. se Whisper fallisce, marcare il segmento come `transcription_failed` e proseguire sugli altri;
4. alla fine unire i testi in ordine in `trascrizione.txt`.

Formato consigliato di `trascrizione.txt`:

```text
[segment-0001 | 00:00:00 - 00:05:00]
...

[segment-0002 | 00:05:00 - 00:10:00]
...
```

Questo rende tracciabile quale parte della call ha prodotto ogni pezzo di testo.

## Regole anti-errore

La pipeline NON deve più:

- scegliere `audio.mp3` solo perché esiste;
- trascrivere un file non indicato nel manifest;
- considerare “OK” una trascrizione ripetitiva tipo “Sottotitoli creati…” senza segnalarla;
- sovrascrivere `trascrizione.txt` con contenuto sospetto senza warning;
- inviare sintesi se la trascrizione è assente, troppo corta o sospetta.

La pipeline DEVE:

- loggare la fonte audio effettiva in `META.md`;
- loggare numero segmenti generati e validi;
- indicare in `META.md` se la trascrizione è completa o parziale;
- mantenere i file audio originali per retry;
- permettere di rieseguire solo la fase post-call.

## Aggiornamento META.md

`META.md` deve includere una sezione tecnica simile:

```markdown
## Audio
- **Fonte:** virtual_out.monitor
- **Modalità:** segmenti MP3 da 300s
- **Cartella segmenti:** audio/segments/
- **Manifest:** audio/manifest.tsv
- **Segmenti generati:** 6
- **Segmenti validi:** 5
- **Trascrizione:** completa/parziale/fallita
```

## Flusso operativo aggiornato

### Fase 1 — Pre-join

1. creare cartella call;
2. creare `audio/segments/` e `transcripts/`;
3. verificare PulseAudio/source;
4. avviare `ffmpeg` in modalità segmentazione 300s;
5. salvare PID e log.

### Fase 2 — Join

6. entrare nella call;
7. instradare Chromium verso `virtual_out`;
8. verificare livello audio;
9. scrivere join in `META.md`.

### Fase 3 — In-call

10. monitorare partecipanti;
11. monitorare che nuovi segmenti vengano creati o che il segmento corrente cresca;
12. se audio fermo/silenzioso per troppo tempo, loggare warning ma non distruggere nulla.

### Fase 4 — Stop

13. fermare ffmpeg in modo graceful;
14. generare/aggiornare `manifest.tsv`;
15. validare tutti i segmenti;
16. aggiornare `META.md`.

### Fase 5 — Post-call

17. trascrivere tutti i segmenti validi;
18. unire in `trascrizione.txt`;
19. controllare qualità minima della trascrizione;
20. generare `SINTESI.md` solo se la trascrizione è utilizzabile;
21. inviare output ad Atti.

## Nota su `audio-call-only.mp3`

Nella run analizzata, `audio-call-only.mp3` era il file corretto mentre `audio.mp3` era contaminato/sbagliato.

Con la nuova procedura, `audio-call-only.mp3` non deve essere un caso speciale manuale: la sorgente corretta deve confluire direttamente nei segmenti `audio/segments/segment-XXXX.mp3`.

Se resta necessario produrre un file unico, va generato dopo la call concatenando i segmenti validi, non usato come input primario per la pipeline.
