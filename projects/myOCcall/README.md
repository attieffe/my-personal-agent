# myOCcall

Progetto per integrare OpenClaw con chiamate video (Teams, Meet, Zoom) al fine di produrre trascrizioni e riassunti automatici.

## Obiettivo

Consentire a IAcopo di entrare in una call come partecipante silenzioso, catturare l'audio via sistema virtuale, trascriverlo con Whisper e restituire un riassunto strutturato.

## Agenti

| Agente | File | Ruolo |
|--------|------|-------|
| **Orchestrator** | `agents/myoccall-orchestrator.agent.md` | Entry point — riceve richiesta da Atti e coordina le fasi |
| **Join** | `agents/myoccall-join.agent.md` | Fasi 1–4: audio setup, join browser, monitoring, exit |
| **Summarize** | `agents/myoccall-summarize.agent.md` | Fase 5: trascrizione, speaker attribution, SINTESI, Telegram |

**Come invocare:** scrivi ad Atti Bot "Entra in questa call Meet: \<url\>" — l'Orchestrator gestisce il resto.

## Struttura

```
myOCcall/
├── README.md                        — questo file
├── CHANGELOG.md                     — versioni e modifiche
├── agents/                          — agenti formali OpenClaw
│   ├── myoccall-orchestrator.agent.md  — entry point principale
│   ├── myoccall-join.agent.md          — fase join + monitoring
│   └── myoccall-summarize.agent.md     — fase post-call + sintesi
├── APPUNTI.md                       — note operative e workaround
├── TODO.md                          — task aperti e miglioramenti
├── data/                            — una cartella per ogni call registrata
│   └── YYYYMMDD HHMM platform - titolo/
│       ├── META.md                  — metadati call
│       ├── HUMAN.MD                 — note manuali di Atti (opzionale)
│       ├── PIPELINE.md              — checklist operativa della call (da template)
│       ├── trascrizione.txt         — output Whisper aggregato
│       ├── trascrizione_attribuita.md — trascrizione con attribuzione parlanti
│       ├── SINTESI.md               — riassunto strutturato finale
│       ├── audio/segments/          — segmenti MP3 da 300s
│       ├── audio/manifest.tsv       — indice + validazione segmenti
│       └── transcripts/             — trascrizioni per singolo segmento
├── docs/
│   ├── architecture.md              — stack tecnico e componenti
│   ├── functions.md                 — funzioni principali (sintetico)
│   ├── setup.md                     — guida installazione e configurazione
│   ├── AGENT_RUNBOOK.md             — guida operativa per l'agente
│   └── PLATFORM_ANALYSIS_ZOOM_TEAMS.md — analisi piattaforme
├── notes/
│   └── call-configs.md              — configurazioni specifiche per piattaforma
└── scripts/                         — script operativi
    ├── call-start.sh / call-stop.sh / call-orchestrate.sh
    ├── call-join-meet.js / call-join-teams.js
    ├── call-transcribe-segments.sh / call-post.sh
    └── ...
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
