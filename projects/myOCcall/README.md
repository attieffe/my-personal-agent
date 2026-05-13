# myOCcall

Progetto per integrare OpenClaw con chiamate video (Teams, Meet, Zoom) al fine di produrre trascrizioni e riassunti automatici.

## Obiettivo

Consentire a AttiBot di entrare in una call come partecipante silenzioso, catturare l'audio via sistema virtuale, trascriverlo con Whisper e restituire un riassunto strutturato.

## Struttura

```
myOCcall/
├── README.md               — questo file
├── CHANGELOG.md            — versioni e modifiche
├── docs/
│   ├── architecture.md     — stack tecnico e componenti
│   ├── functions.md        — funzioni principali (sintetico)
│   └── setup.md            — guida installazione e configurazione
├── notes/
│   └── call-configs.md     — appunti su configurazioni specifiche per piattaforma
└── scripts/                — script di avvio/cattura (da sviluppare)
```

## Stato attuale

- [x] Infrastruttura audio completa (PulseAudio + ffmpeg)
- [x] Script pipeline implementati (start, stop, monitor, post-call)
- [x] Join automatico Google Meet implementato
- [x] Segmentazione audio 300s + trascrizione multi-segmento
- [x] Flow post-call: Whisper + SINTESI.md + Telegram
- [ ] Test end-to-end con call reale (in corso)
- [ ] Join automatico Zoom/Teams
- [ ] Speaker diarization

**Prossimi passi:** Test completo con chiamata reale, verifica invio Telegram, implementazione altre piattaforme.

**Documentazione:** Vedi [TODO.md](TODO.md) per task aperti e [PIPELINE_TEMPLATE.md](PIPELINE_TEMPLATE.md) per checklist operativa.
