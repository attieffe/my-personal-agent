# Procedura: Cattura Audio — FONTE UNICA PulseAudio

> Questo file è la fonte di verità per tutto ciò che riguarda la configurazione PulseAudio,
> la cattura audio con ffmpeg e il routing post-join. Tutti gli altri file rimandano qui.

---

## Configurazione PulseAudio headless

### File di configurazione `~/.config/pulse/default.pa`

```bash
mkdir -p ~/.config/pulse
cat > ~/.config/pulse/default.pa << 'EOF'
.include /etc/pulse/default.pa
load-module module-null-sink sink_name=virtual_out sink_properties=device.description="VirtualOutput"
set-default-sink virtual_out
set-default-source virtual_out.monitor
EOF
```

> ⚠️ **CRITICO**: La prima riga `.include /etc/pulse/default.pa` è obbligatoria.
> Senza di essa, il modulo `module-native-protocol-unix` non viene caricato e il socket
> Unix non viene creato — la connessione PulseAudio fallirà con "connection refused".

### Avvio PulseAudio

Usare sempre `_system/scripts/start-audio.sh`. Non usare altri metodi.

```bash
bash _system/scripts/start-audio.sh
```

Il flag `--exit-idle-time=-1` è essenziale: senza di esso PulseAudio si spegne automaticamente
dopo pochi secondi quando non ci sono client connessi.

> ⚠️ **Non usare systemd socket activation** (`pulseaudio.socket`): va in conflitto con
> lo start manuale e causa race condition al primo tentativo di connessione.

### Verifica

```bash
pactl info                          # daemon attivo?
pactl list short sinks              # virtual_out presente?
pactl list short sources            # virtual_out.monitor presente?
```

---

## Test cattura audio

```bash
# Registra 5 secondi dal monitor — il file deve essere > 0 byte e contenere audio
ffmpeg -f pulse -i virtual_out.monitor -t 5 /tmp/test.mp3

# Verifica volume (distingue silenzio da audio reale)
ffmpeg -f pulse -i virtual_out.monitor -t 4 -filter:a volumedetect -f null /dev/null
# Silenzio:    max_volume: -91 dB
# Audio reale: max_volume: > -40 dB  (voce ~= -27 dB)
```

---

## Routing audio post-join (passo critico)

Dopo che il browser joina la call, l'audio di Chromium va sul sink di default, NON su `virtual_out`.
Bisogna spostarlo come step automatico nella pipeline.

```bash
# Trova i sink input di Chromium
pactl list sink-inputs short | grep -i chromium

# Sposta su virtual_out (sostituire <ID> con il numero trovato)
pactl move-sink-input <ID> virtual_out

# Verifica che l'audio arrivi
ffmpeg -f pulse -i virtual_out.monitor -t 4 -filter:a volumedetect -f null /dev/null
```

> Questo step va automatizzato in `call-orchestrate.sh` dopo la conferma del join.
> Vedi TODO in `_knowledge/ROADMAP.md`: "Routing audio post-join automatico".

---

## Segmentazione audio per Whisper

- I segmenti vengono registrati da ffmpeg in chunk da **300 secondi** (5 minuti)
- Formato: MP3
- Limite Whisper API: max **25 MB per chunk** — segmenti da 300s rientrano sempre nel limite
- Vedi `_system/PROCEDURA_AUDIO_TRASCRIZIONE.md` per il formato manifest.tsv e la validazione

```bash
# Avvia cattura segmentata (viene avviata da call-start.sh)
ffmpeg -f pulse -i virtual_out.monitor \
  -f segment -segment_time 300 -segment_format mp3 \
  "$CALL_DIR/audio/segments/segment-%04d.mp3"
```

---

## Troubleshooting

| Sintomo | Causa probabile | Fix |
|---|---|---|
| `Connection refused` a PulseAudio | Manca `.include /etc/pulse/default.pa` | Aggiungere prima riga al file config |
| PulseAudio si spegne da solo | Manca `--exit-idle-time=-1` | Usare `start-audio.sh` |
| `virtual_out.monitor` non esiste | PulseAudio avviato senza config corretta | Fermare daemon, correggere config, riavviare |
| ffmpeg non registra nulla | Chromium audio non su `virtual_out` | Eseguire routing manuale con `pactl move-sink-input` |
| Segmenti tutti `silent` | Audio non arriva al monitor source | Verificare routing (step sopra) |

Per casi più complessi, aggiornare `_knowledge/WORKAROUNDS.md`.
