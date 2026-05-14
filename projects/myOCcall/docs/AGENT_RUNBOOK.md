# AGENT RUNBOOK — myOCcall

Guida operativa per l'agente che gestisce le registrazioni delle chiamate.

---

## Panoramica

Come agente myOCcall, il tuo compito è:
1. Ricevere richiesta di join call (piattaforma + URL)
2. Seguire la PIPELINE operativa step-by-step
3. Registrare audio, trascrivere con Whisper, generare sintesi
4. Inviare risultato finale ad Atti via Telegram

---

## Quando Ti Viene Chiesto di Registrare una Call

### Input Atteso

- **Piattaforma:** `meet` | `zoom` | `teams`
- **URL:** Link completo della call
- **Opzionale:** Orario fine previsto (per exit automatico)

**Esempio:**
```
"Entra in questa call Meet: https://meet.google.com/abc-defg-hij"
```

### Output Atteso

- Cartella call creata in `data/YYYYMMDD HHMM platform/`
- File `PIPELINE.md` (checklist) nella cartella call
- Audio registrato in segmenti da 300s
- Cronistoria call ricostruibile (join browser, segmenti, partecipanti)
- Trascrizione completa in `trascrizione.txt`
- Sintesi strutturata in `SINTESI.md`
- Invio sintesi ad Atti via Telegram

---

## Procedura Step-by-Step

### Step 1 — Preparazione

1. **Verificare prerequisiti:**
   - PulseAudio attivo: `pactl info`
   - Se non attivo: `bash scripts/start-audio.sh`
   - Source `virtual_out.monitor` esiste: `pactl list short sources | grep virtual_out`

2. **Creare cartella call:**
   ```bash
   CALL_DIR=$(bash scripts/call-start.sh <platform> <url>)
   ```
   Output: path assoluto alla cartella call (es. `/home/user/.openclaw/workspace/projects/myOCcall/data/20260514 1430 meet`)

3. **Copiare template PIPELINE:**
   ```bash
   cp PIPELINE_TEMPLATE.md "$CALL_DIR/PIPELINE.md"
   # Aggiorna header con data/ora/piattaforma effettivi
   sed -i "s/\[DATA ORA PIATTAFORMA\]/$(basename "$CALL_DIR")/" "$CALL_DIR/PIPELINE.md"
   ```

### Step 2 — Esecuzione Call

**Opzione A — Orchestratore automatico (consigliato):**
```bash
bash scripts/call-orchestrate.sh <platform> <url>
```
Esegue automaticamente tutte le fasi (join → monitoring → exit → post-call).

**Opzione B — Manuale (debug/controllo fine):**
```bash
# Fase 1: già fatto (call-start.sh)
# Fase 2: join browser
node scripts/call-join-meet.js "$CALL_DIR" <url>

# Fase 3: monitoring (blocca fino a exit condition)
bash scripts/call-monitor.sh "$CALL_DIR"

# Fase 4: exit
bash scripts/call-stop.sh "$CALL_DIR"

# Fase 5: post-call
bash scripts/call-post.sh "$CALL_DIR"
```

### Step 3 — Monitoraggio Durante Call

Ogni 60s, aggiorna la `PIPELINE.md` della call:
- Spunta `[x]` task completati
- Aggiungi note operative se necessario
- Se rilevi anomalie → logga in sezione "Note Operative"

**Esempio anomalia:**
```markdown
## Note Operative
- `[14:32]` PulseAudio source non trovato → riavviato con start-audio.sh
- `[14:45]` Browser crash → riavviato, audio non perso (ffmpeg continuava)
```

### Step 4 — Post-Call

Al termine della call, verifica:
- [ ] `audio/manifest.tsv` generato
- [ ] Almeno 1 segmento `status=valid`
- [ ] `trascrizione.txt` creato (>10 parole, non ripetitivo, con timestamp utili)
- [ ] **Se Atti ha fornito note sulla call → archiviate in `HUMAN.MD` prima di generare la SINTESI**
- [ ] `SINTESI.md` generata con contenuto valido e struttura completa:
  - Nomi partecipanti espliciti (presenti confermati vs citati)
  - Argomenti trattati + considerazioni e pareri emersi
  - Decisioni prese (integrate con HUMAN.MD se presente)
  - Sezione "Note di Attilio" se HUMAN.MD presente
- [ ] Azioni IT estratte dalla SINTESI e presentate ad Atti per conferma/assegnazione
- [ ] TODO personale di Atti aggiornato ("Revisiona SINTESI [titolo]") nel file corretto (COLZANI/PERSONALI, ATTILIO_A_CASA, o DA_DEFINIRE)
- [ ] Partecipanti e cronistoria ricostruiti per quanto possibile
- [ ] Invio Telegram riuscito (o `sintesi-pending-send.txt` creato)

**Messaggio di conferma ad Atti:**
```
✅ Call registrata e trascritta
📁 Cartella: data/YYYYMMDD HHMM platform
⏱️ Durata: HH:MM
📊 Segmenti audio: X validi / Y totali
📝 Trascrizione: XXX parole
```

---

## Gestione Errori Comuni

### PulseAudio Non Attivo

**Sintomo:** `pactl info` fallisce

**Fix:**
```bash
bash scripts/start-audio.sh
pactl info  # verifica funzionante
```

### ffmpeg Non Scrive Segmenti

**Sintomo:** `audio/segments/` vuota dopo 60s

**Diagnosi:**
```bash
ps aux | grep ffmpeg           # processo attivo?
tail -f audio/recording.log    # errori?
pactl list sink-inputs         # browser collegato?
```

**Fix:**
1. Verificare che browser sia instradato a `virtual_out`
2. Se no: `pactl move-sink-input <ID> virtual_out`
3. Verificare livello audio: `ffmpeg -f pulse -i virtual_out.monitor -t 3 -filter:a volumedetect -f null - 2>&1 | grep max_volume`

### Whisper API Fallisce

**Sintomo:** `call-transcribe-segments.sh` esce con errore

**Diagnosi:**
```bash
# Verifica chiave API
echo $OPENAI_API_KEY

# Test connessione
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

**Fix:**
1. Verificare `.env` contiene `OPENAI_API_KEY=sk-...`
2. Verificare quota API OpenAI non esaurita
3. Retry manuale: `bash scripts/call-transcribe-segments.sh "$CALL_DIR"`

### Trascrizione Ripetitiva o Vuota

**Sintomo:** `call-post.sh` esce con "too_short" o "repetitive"

**Diagnosi:**
```bash
wc -w trascrizione.txt          # conta parole
head -20 trascrizione.txt       # ispeziona contenuto
```

**Fix:**
1. Verificare che i segmenti audio contengano effettivamente parlato (non silenzio)
2. Controllare `audio/manifest.tsv` — tutti i segmenti validi?
3. Se audio OK ma trascrizione sbagliata → possibile errore Whisper, segnalare ad Atti

### Metadati mancanti o incompleti

**Sintomo:** non si riesce a ricostruire join browser, ingressi/uscite o start/end segmenti.

**Comportamento atteso:** procedere comunque con trascrizione audio e poi sintetizzare usando i timestamp disponibili.

**Fix futuro:** approfondire in una sessione apposita per MEET e TEAMS come salvare metadati o log strutturati da convertire in cronistoria MD.

### Browser Crash Durante Call

**Sintomo:** Processo `call-join-meet.js` terminato inaspettatamente

**Comportamento atteso:** ffmpeg continua a registrare → audio NON perso

**Fix:**
1. Riavviare browser manualmente (se call ancora in corso)
2. Logging in `META.md` / `PIPELINE.md` con timestamp crash
3. Completare normalmente post-call

---

## Troubleshooting Rapido

| Problema | Comando Diagnosi | Fix |
|----------|------------------|-----|
| PulseAudio morto | `pactl info` | `bash scripts/start-audio.sh` |
| ffmpeg non scrive | `ls -lh audio/segments/` + `tail audio/recording.log` | Verifica sink routing |
| Audio silenzioso | `ffmpeg -f pulse -i virtual_out.monitor -t 3 -filter:a volumedetect -f null -` | `pactl move-sink-input <ID> virtual_out` |
| Whisper timeout | `curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models` | Verifica API key, quota |
| Sintesi non inviata | `ls sintesi-pending-send.txt` | Retry: `openclaw sessions send main "$(cat SINTESI.md)"` |

---

## Riferimenti Rapidi

- **Procedura audio:** [PROCEDURA_AUDIO_TRASCRIZIONE.md](../PROCEDURA_AUDIO_TRASCRIZIONE.md)
- **Flow completo:** [PIPELINE.md](../PIPELINE.md)
- **Template checklist:** [PIPELINE_TEMPLATE.md](../PIPELINE_TEMPLATE.md)
- **TODO progetto:** [TODO.md](../TODO.md)

---

## Regole Operative

1. **Mai sovrascrivere audio senza conferma** — i segmenti MP3 sono fonte primaria
2. **Mai inviare sintesi se trascrizione fallita** — meglio notificare errore
3. **Sempre loggare anomalie in PIPELINE.md** — aiuta il debug futuro
4. **Timezone sempre Europe/Rome** — orari in META.md e log
5. **Nome bot sempre "Attilio F."** — visibile agli altri partecipanti
6. **Webcam sempre spenta** — nessun video trasmesso

---

## Checklist Finale Prima di Chiudere

- [ ] `PIPELINE.md` nella cartella call completamente spuntata
- [ ] `META.md` aggiornato con tutti i timestamp
- [ ] `SINTESI.md` generata con struttura completa (partecipanti, argomenti, considerazioni, decisioni, note Atti)
- [ ] Azioni IT presentate ad Atti e TODO personale aggiornato
- [ ] Sintesi inviata ad Atti (o pending salvato)
- [ ] Nessun processo ffmpeg/browser ancora attivo (`ps aux | grep -E 'ffmpeg|chromium'`)
- [ ] Messaggio di conferma inviato ad Atti
