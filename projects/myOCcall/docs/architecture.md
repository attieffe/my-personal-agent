# Architettura

## Stack

| Componente | Tecnologia | Ruolo |
|---|---|---|
| Join call | OpenClaw browser tool | Apre il link della call nel browser headless |
| Audio virtuale | PulseAudio null sink | Dispositivo audio virtuale su server headless |
| Cattura audio | ffmpeg (PulseAudio monitor) | Registra l'audio della call in chunk |
| Trascrizione | OpenAI Whisper API | Converte audio → testo |
| Riassunto | Claude (IAcopo) | Elabora il testo e produce il riassunto |

## Flusso

```
Link call
   ↓
Browser tool (OpenClaw) → join call
   ↓
PulseAudio null sink ← audio della call
   ↓
ffmpeg monitor source → file audio (chunk)
   ↓
Whisper API → trascrizione testo
   ↓
Claude → riassunto strutturato
```

## Server

- **OS:** Linux 6.8.0-111-generic (x64)
- **User:** openclaw (sudo)
- **Hardware audio:** assente (VPS headless)
- **Audio software:** da installare

## Dipendenze da installare

```bash
sudo apt-get install -y pulseaudio pulseaudio-utils ffmpeg
```

## Configurazione PulseAudio headless

PulseAudio deve girare in modalità daemon con un null sink come dispositivo default:

```bash
pulseaudio --start --load="module-null-sink" --log-target=syslog
pactl load-module module-null-sink sink_name=virtual_out
pactl set-default-sink virtual_out
```

Il monitor source (`virtual_out.monitor`) è quello che ffmpeg cattura.
