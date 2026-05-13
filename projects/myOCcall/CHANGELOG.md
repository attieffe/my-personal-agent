# Changelog

## [Unreleased]

### In corso
- Installazione Chromium (richiede sudo) per completare Step 3
- Integrazione Whisper API

---

## [0.3.0] — 2026-05-13

### Verificato
- Pipeline audio end-to-end confermata: tono 440 Hz generato con ffmpeg → sink `virtual_out` → catturato da ffmpeg su `virtual_out.monitor` a -25 dB (audio reale)
- Confermato anche con `parec --device=virtual_out.monitor` (-22 dB)
- Identificato blocco Step 3: Chromium non installato → OpenClaw browser non funziona
- Richiesta azione: `sudo snap install chromium`

---

## [0.2.0] — 2026-05-13

### Aggiunto
- Installato `pulseaudio`, `pulseaudio-utils`, `ffmpeg`
- Configurato `~/.config/pulse/default.pa` con null sink (`virtual_out`) e `module-always-sink`
- **Nota tecnica:** `default.pa` deve includere `/etc/pulse/default.pa` per caricare `module-native-protocol-unix`, altrimenti il socket non viene creato
- Test cattura 5 secondi con `ffmpeg -f pulse -i virtual_out.monitor` — OK (68kB MP3)
- Creato `scripts/start-audio.sh` per avvio idempotente
- Configurato autostart in `~/.bashrc`

---

## [0.1.0] — 2026-05-13

### Aggiunto
- Analisi fattibilità tecnica su Linux headless
- Verifica infrastruttura: nessun hardware audio presente, nessun sistema audio installato
- Identificato stack: PulseAudio null sink + ffmpeg + Whisper API + OpenClaw browser tool
- Creata struttura cartella `myOCcall`
