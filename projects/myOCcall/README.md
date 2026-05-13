# myOCcall

Progetto per integrare OpenClaw con chiamate video (Teams, Meet, Zoom) al fine di produrre trascrizioni e riassunti automatici.

## Obiettivo

Consentire a Ralf di entrare in una call come partecipante silenzioso, catturare l'audio via sistema virtuale, trascriverlo con Whisper e restituire un riassunto strutturato.

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

- [x] Analisi fattibilità
- [x] Verifica infrastruttura audio (assente, da installare)
- [x] Installazione PulseAudio + ffmpeg
- [x] Configurazione null sink (`virtual_out` + `virtual_out.monitor`)
- [x] Test cattura audio con ffmpeg — OK
- [x] Script avvio `scripts/start-audio.sh` + autostart in `.bashrc`
- [ ] Verifica routing audio browser → virtual sink
- [ ] Integrazione Whisper
- [ ] Pipeline completa end-to-end
