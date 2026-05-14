# Appunti — myOCcall

Note operative, workaround e configurazioni specifiche per piattaforma.

- Quando Atti dice “registrazione CALL”, si intende sempre il progetto **myOCcall**.

---

## PulseAudio — workaround critici

- Il file `~/.config/pulse/default.pa` deve iniziare con `.include /etc/pulse/default.pa`
  Senza questa riga il modulo `native-protocol-unix` non viene caricato e il socket non esiste.
- Non usare mai systemd socket activation per PulseAudio: va in conflitto con lo start manuale.
- Usare sempre `scripts/start-audio.sh` per avviare PulseAudio.

## Test cattura audio

```bash
ffmpeg -f pulse -i virtual_out.monitor -t 5 /tmp/test.mp3
# Verifica: il file deve essere > 0 byte e contenere audio
```

## Configurazioni piattaforme call

Vedi `notes/call-configs.md` per selettori CSS/XPath e workaround specifici per Meet, Zoom, Teams.

---

## Come joinare Google Meet — metodo che funziona (testato 2026-05-13)

### Problema incontrato
I test con Playwright headless diretto (fresh browser, nessun account Google) fallivano immediatamente con "You can't join this video call", anche con l'host presente e il meeting impostato su "chiunque con il link".
- Causa: Google Workspace blocca i join anonimi a livello di dominio, non di singolo meeting.
- Anche `launchPersistentContext` con il profilo OpenClaw falliva perché Chromium era già in esecuzione e il profilo risultava bloccato.

### Soluzione che funziona
Usare il **browser tool di OpenClaw** tramite subagent (NON Playwright diretto).

Il browser tool di OpenClaw usa una istanza Chromium gestita dal gateway con la sessione Google dell'utente già attiva (`/home/openclaw/.openclaw/browser/openclaw/user-data/`). Con questa sessione, Meet accetta il join senza bisogno di autenticazione aggiuntiva.

### Flusso operativo corretto
1. Lanciare un subagent con label `myOCcall` e task di join (vedi `scripts/call-orchestrate.sh`)
2. Il subagent usa il `browser` tool: `action="open"`, `url=<meet_url>`, `label="meet"`
3. Meet mostra la schermata pre-join → il subagent: disattiva mic/cam, imposta nome "Attilio F.", clicca "Chiedi di partecipare"
4. L'host vede la richiesta e ammette il bot dalla sala d'attesa
5. Una volta dentro: NON attivare i sottotitoli — la pipeline usa solo registrazione audio → Whisper

### Routing audio (passo critico — da automatizzare)
Dopo che il browser joina la call, l'audio Chromium va sul sink di default, NON su `virtual_out`.
Bisogna spostarlo manualmente (o automaticamente nella pipeline):
```bash
# Trova i sink input di Chromium
pactl list sink-inputs short | grep -i chromium
# Sposta su virtual_out
pactl move-sink-input <ID> virtual_out
```
Questo va aggiunto come step automatico in `call-orchestrate.sh` dopo la conferma del join.
Verifica che l'audio arrivi: `ffmpeg -f pulse -i virtual_out.monitor -t 4 -filter:a volumedetect -f null /dev/null`
- Silenzio: `max_volume: -91 dB`
- Audio reale: `max_volume: > -40 dB` (voce = circa -27 dB)

## Chunking audio per Whisper

Se la call è lunga, dividere il file audio in chunk da max 25MB prima di inviare a Whisper.

## Cronistoria call

- Per ogni call, cercare di salvare o ricostruire: join browser, start/end segmenti, ingressi/uscite, bot/esterni e nomi rilevati.
- Se i metadati mancano, usare i timestamp audio disponibili e segnare la lacuna per approfondimento in sessione dedicata (MEET e TEAMS).

---

## Speaker attribution — decisione tecnica v1

Decisione: per attribuire “chi ha detto cosa” non puntiamo prima alla diarization pura da voce, ma a una **timeline active speaker** ricavata dal DOM di Meet/Teams e poi sovrapposta ai timestamp della trascrizione.

Pipeline prevista:

1. Durante la call, un monitor osserva il DOM e salva gli eventi active speaker in `speaker-events.jsonl`.
2. Ogni evento deve contenere almeno: `wall_ts`, `call_sec`, `speaker_name`, `event`, `source`, `confidence`.
3. I chunk audio restano la fonte primaria: `audio/manifest.tsv` conserva `start_sec` e `duration_sec` per ogni segmento.
4. Whisper deve produrre anche timestamp per frase/segmento, quindi va affiancato al `.txt` un output JSON per chunk.
5. Post-call: si genera una timeline normalizzata `transcript-events.jsonl` con `call_start_sec`, `call_end_sec`, `text`, `segment_file`.
6. Overlay: ogni frase viene assegnata al parlante con massimo overlap temporale nella timeline DOM.
7. Output finale: `trascrizione_attribuita.md`, poi uso nella sezione “Dettaglio per parlante” di `SINTESI.md`.

Nota: chiamarla “speaker attribution via active speaker timeline” è più preciso di “speaker diarization”, perché non identifica il parlante solo dalla voce ma sfrutta i segnali della piattaforma.
