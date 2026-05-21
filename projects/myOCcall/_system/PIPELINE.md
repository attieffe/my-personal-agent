# PIPELINE — myOCcall

> **Reference documentation** — Questo file descrive il flow completo del sistema. Per la **checklist operativa** da seguire in ogni singola call, vedi [PIPELINE_TEMPLATE.md](PIPELINE_TEMPLATE.md) (da copiare nella cartella della call).

Definizione operativa di cosa fa il sistema durante e dopo una call attiva.

> **Regole operative:**
> - Il join e tutta la pipeline vengono eseguiti dalla **sessione dedicata myOCcall**, non dalla sessione principale (IAcopo).
> - **Modello da usare per l'implementazione:** `claude-opus-4-7` (Opus 4.7)
> - La **webcam è sempre spenta/nascosta** — nessun output video visibile agli altri partecipanti.
> - Il nome visualizzato nella call è sempre **"Attilio F."**
> - Tutti gli orari usano il **timezone Europe/Rome (ora italiana)**.

---

## Struttura dati per call

Ogni call produce una cartella dedicata in `data/`:

```
projects/myOCcall/data/
  YYYYMMDD HHMM <platform> - <titolo>/   ← es. "20260513 1224 meet - rinnovo shippypro"
    META.md                    ← metadati call (aggiornato in tempo reale)
    HUMAN.md                   ← note manuali di Atti (opzionale, fuse nella sintesi)
    audio/segments/*.mp3       ← segmenti audio ffmpeg da 300s
    audio/manifest.tsv         ← indice + validazione segmenti audio
    transcripts/*.txt          ← trascrizioni per segmento
    trascrizione.txt           ← output Whisper aggregato (fase post-call)
    SINTESI.md                 ← riassunto strutturato finale (fase post-call)
```

> **HUMAN.md** — file opzionale che Atti può creare e aggiornare durante o dopo la call con appunti, contesto, nomi dei partecipanti, decisioni osservate, cose da non dimenticare. Se presente, viene fuso nella SINTESI.md come sezione dedicata e usato per arricchire/correggere il riassunto automatico.

> Procedura audio/trascrizione autorevole: vedere `PROCEDURA_AUDIO_TRASCRIZIONE.md`.
> La pipeline non deve più dipendere da un singolo `audio.mp3` come input primario di Whisper.

### Formato META.md

```markdown
# Call — <platform> — <data ora italiana>

## Info call
- **Piattaforma:** Meet / Zoom / Teams
- **URL:** https://...
- **Bot join:** YYYY-MM-DD HH:MM (Europe/Rome)
- **Bot leave:** YYYY-MM-DD HH:MM (Europe/Rome)
- **Durata:** HH:MM

## File di lavoro
- **Audio:** segmenti MP3 da 300s
- **Trascrizione:** trascrizione.txt ([ ] da generare)
- **Sintesi:** SINTESI.md ([ ] da generare)

## Partecipanti
| Nome | Entrata | Uscita |
|------|---------|--------|
| Attilio F. (bot) | HH:MM | HH:MM |
| ... | HH:MM | HH:MM |

## Note
_(anomalie, problemi tecnici, osservazioni)_
```

---

## Fase 1 — Pre-join

1. Determinare piattaforma e URL della call
2. Creare cartella `data/YYYYMMDD HHMM <platform>/` (ora italiana)
3. Creare `META.md` con piattaforma, URL, stato "in corso"
4. Avviare **ffmpeg** in background → output segmentato in `audio/segments/segment-XXXX.mp3` ogni 300s
5. Verificare che ffmpeg stia scrivendo (segmento corrente creato/cresce dopo 3s)

## Fase 2 — Join

6. Aprire URL con Playwright, webcam spenta, nome "Attilio F."
7. Scrivere **orario di join** (Europe/Rome) in `META.md`

## Fase 3 — In-call (monitoring loop)

8. Polling ogni 60-90s sul badge "People":
   - Loggare entrate/uscite partecipanti in `META.md` con orario
   - Se partecipanti = 1 (solo bot) per > 2 minuti → attivare exit
9. Controllare periodicamente che ffmpeg stia ancora scrivendo

## Fase 4 — Exit

10. Fermare ffmpeg (graceful stop, non kill — garantisce file integro)
11. Scrivere **orario di leave** e durata in `META.md`
12. Uscire dalla call (click "Leave call")
13. Generare `audio/manifest.tsv` e verificare che esista almeno un segmento valido

## Fase 5 — Post-call (flow separato, indipendente)

> Questa fase può girare subito dopo o in differita. Richiede solo che `audio/manifest.tsv` e `META.md` esistano.

14. Avviare **Whisper** su tutti i segmenti validi nel manifest → salvare output per segmento in `transcripts/`
15. Aggregare tutte le trascrizioni ordinate in `trascrizione.txt`
16. Aggiornare `META.md`: trascrizione completa/parziale/fallita
17. Generare **SINTESI.md** dalla trascrizione solo se supera i controlli minimi. La sintesi deve includere obbligatoriamente:
    - **Info call:** piattaforma, URL, orari join/leave, durata
    - **Partecipanti:** nomi espliciti di chi ha partecipato (ricavati da trascrizione, DOM, META.md o HUMAN.MD). Se un nome non è verificabile con certezza, indicarlo come "citato" vs "presente confermato". Non scrivere solo "bot registratore" se ci sono partecipanti reali.
    - **Contesto e inizio riunione**
    - **Argomenti trattati**
    - **Considerazioni e pareri emersi:** opinioni, preoccupazioni, valutazioni espresse dai partecipanti durante la discussione (distinte dalle decisioni formali)
    - **Decisioni prese:** solo quelle effettivamente deliberate, da confrontare e integrare con `HUMAN.MD` se presente
    - **Se esiste `HUMAN.md`:** leggere il file prima di scrivere la sintesi; fondere le note come sezione "Note di Attilio" e usarle per arricchire/correggere il contenuto automatico (le note di HUMAN.MD prevalgono sull'interpretazione automatica in caso di discrepanza)
    - **Estratto trascrizione** (frasi utili; escludere boilerplate e parti incomprensibili)
    > **Regola HUMAN.MD:** Se Atti ti fornisce note riferite a questa riunione (durante o dopo la call), chiedile di archiviarle in `HUMAN.MD` nella cartella della call prima che tu generi la SINTESI. Questo garantisce che vengano fuse correttamente.
18. Aggiornare `META.md`: sintesi ✓
19. Deducere un titolo breve dalla sintesi e rinominare la cartella call in `YYYYMMDD HHMM <platform> - <titolo>/`
19b. **Conferma IT post-SINTESI:** Prima di inviare via Telegram, presentare ad Atti:
    - Elenco delle **azioni in carico all'area IT** emerse dalla sintesi (es. sviluppi, integrazioni, strumenti da costruire)
    - Proposta di assegnazione o revisione per ciascuna azione
    - Aggiungere a TODO personale di Atti la voce "Revisiona SINTESI [titolo call]", instradando nel file corretto:
      - Call COLZANI → `projects/myJob/COLZANI/PERSONALI/README.md` (sezione TODOLIST)
      - Call sfera privata/casa → `projects/myJob/ATTILIO_A_CASA/01_todo_riassuntivo.md`
      - Contesto non identificabile → appendere a `projects/myJob/DA_DEFINIRE.md` (creare se non esiste)
20. Inviare `SINTESI.md` ad Atti via Telegram

---

## Stato dei task di implementazione

### Fase 1-4 (in-call)
- [x] Script avvio ffmpeg automatico al join (output in cartella call)
- [x] Creazione automatica cartella call + META.md
- [x] Logging join/leave in META.md (orario Europe/Rome)
- [x] Monitoring partecipanti + log entrate/uscite
- [x] Exit condition: partecipanti = 1 per > 2 min
- [x] Stop graceful ffmpeg + verifica integrità audio

### Fase 5 (post-call)
- [x] Flow post-call: Whisper su manifest segmenti → trascrizione.txt
- [x] Generazione SINTESI.md da trascrizione
- [x] Invio SINTESI.md via Telegram

### Infrastruttura
- [ ] Speaker diarization (chi parla quando)
- [ ] Skill OpenClaw `call-summarizer` con output strutturato
