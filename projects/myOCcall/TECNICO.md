# Documento Tecnico — myOCcall

Dettagli completi in `docs/architecture.md`, `docs/functions.md`, `docs/setup.md`.

## Stack

- **Audio capture:** PulseAudio null sink (`virtual_out`) + ffmpeg
- **Browser:** Chromium via OpenClaw browser tool (con `PULSE_SERVER` impostato)
- **Trascrizione:** OpenAI Whisper API (skill OpenClaw: `openai-whisper-api`)
- **Orchestrazione:** Ralf (OpenClaw) via skill dedicata (da creare)
- **Output:** riassunto strutturato inviato via Telegram

## Flusso tecnico

```
Link call + orario fine previsto
  → browser apre la call (OpenClaw browser tool)
  → audio grezzo instradato verso virtual_out (PulseAudio)
  → ffmpeg cattura da virtual_out.monitor → MP3/WAV
  → monitoraggio partecipanti (exit se tutti usciti, o timeout orario fine)
  → Whisper trascrive l'audio grezzo (NON la trascrizione della piattaforma)
  → speaker diarization: attribuzione interventi per parlante (via attivazione microfono)
  → Ralf produce riassunto strutturato (contesto, argomenti, decisioni, chi-dice-cosa)
  → invio a Atti via Telegram
```

## Regole di comportamento (requisiti funzionali)

- **Fonte audio:** sempre audio grezzo catturato localmente. Mai basarsi sulle trascrizioni live di Meet/Zoom/Teams (inaffidabili, perdono accenti e sovrapposizioni).
- **Speaker diarization:** identificare chi parla tramite attivazione microfono; attribuire ogni intervento al parlante corretto nella sintesi.
- **Output:** sintesi strutturata, NON trascrizione verbatim. Formato:
  - Contesto e inizio riunione
  - Argomenti trattati
  - Decisioni prese
  - Dettaglio per parlante (cosa ha detto, in sintesi)
- **Exit condition (doppia):**
  - Orario di fine previsto raggiunto → uscita automatica
  - Tutti i partecipanti hanno lasciato → uscita anticipata

## Note critiche

- `~/.config/pulse/default.pa` DEVE iniziare con `.include /etc/pulse/default.pa`
  (senza, il socket Unix non viene creato e nulla funziona)
- PulseAudio con `--exit-idle-time=-1` obbligatorio (altrimenti si spegne)
- Systemd socket activation interferisce: usare sempre `scripts/start-audio.sh`
- Whisper skill path: `~/.npm-global/lib/node_modules/openclaw/skills/openai-whisper-api/`

## Come verificare che PulseAudio sia attivo

```bash
pactl info
# Se fallisce → eseguire scripts/start-audio.sh
```
