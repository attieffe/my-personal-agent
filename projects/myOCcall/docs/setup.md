# Guida Setup

## Prerequisiti

- Server Linux con sudo
- OpenClaw installato e funzionante
- Chiave API OpenAI (per Whisper)

## Step 1 — Installazione pacchetti

```bash
sudo apt-get install -y pulseaudio pulseaudio-utils ffmpeg
```

## Step 2 — Configurazione PulseAudio headless

Crea il file di configurazione:

```bash
mkdir -p ~/.config/pulse
cat > ~/.config/pulse/default.pa << 'EOF'
load-module module-null-sink sink_name=virtual_out sink_properties=device.description="VirtualOutput"
set-default-sink virtual_out
set-default-source virtual_out.monitor
EOF
```

Avvia PulseAudio:

```bash
pulseaudio --start
```

Verifica:

```bash
pactl list short sinks
pactl list short sources
```

## Step 3 — Test cattura audio

```bash
# Registra 10 secondi dal monitor
ffmpeg -f pulse -i virtual_out.monitor -t 10 test.mp3
```

## Step 4 — Configurazione browser per audio

Il browser headless deve usare PulseAudio come dispositivo audio. Verificare che la variabile `PULSE_SERVER` sia impostata correttamente nell'ambiente OpenClaw.

## Step 5 — Whisper API key

Configurare la chiave OpenAI in OpenClaw (vedi `notes/call-configs.md`).

## Stato installazione

- [x] Pacchetti installati
- [x] PulseAudio configurato e avviato
- [x] Test cattura audio superato
- [ ] Browser routing audio verificato
- [ ] Whisper API configurata

## Note tecniche

- Il `~/.config/pulse/default.pa` **deve** iniziare con `.include /etc/pulse/default.pa` — senza, PulseAudio non carica `module-native-protocol-unix` e il socket non viene creato (connessione rifiutata)
- PulseAudio va avviato con `--exit-idle-time=-1`, altrimenti si spegne dopo pochi secondi senza client connessi
- Il systemd socket activation (`pulseaudio.socket`) interferisce: usa lo script `scripts/start-audio.sh` invece
