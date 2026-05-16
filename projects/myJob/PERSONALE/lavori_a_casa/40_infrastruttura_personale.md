# Lavori a casa — infrastruttura personale

- [ ] Sistemare NAS + certificati per Synology Foto (non sta funzionando)
- [ ] Collegare OpenClaw a GitHub Copilot — basta lanciare il comando per connettere il gateway (2026-05-15)
- [ ] **Approfondire log OpenClaw** — capire come interagisce con i modelli (quali prompt invia, come vengono salvati i log) (2026-05-16)

---

## 📋 Ricerca: Log OpenClaw — come interagisce coi modelli

> Ricerca fatta il 2026-05-16. Fonti: docs.openclaw.ai + doc locale.

### Due superfici di log

OpenClaw logga in due posti:
1. **File JSON lines** → `/tmp/openclaw/openclaw-YYYY-MM-DD.log` (un file al giorno, ruota a 100 MB, max 5 archivi)
2. **Console output** → terminale / Debug UI (configurabile separatamente)

### Cosa viene loggato di default (livello `info`)

- All'avvio: il modello di default e le impostazioni, es. `agent model: claude-sonnet-4-6 (thinking=medium, fast=on)`
- Errori, call WebSocket lente (>= 50ms), parse errors
- Lifecycle events: tipo evento, provider, dimensioni/timing — ma **senza** il contenuto dei prompt o delle risposte

**I prompt inviati al modello NON vengono salvati nei log di default.** Questo è by design (privacy).

### Come vedere i prompt inviati al modello

Per catturare i dettagli delle chiamate ai modelli bisogna:

**Opzione 1 — Alzare il livello di log**
```json
// ~/.openclaw/openclaw.json
{
  "logging": {
    "level": "debug"   // oppure "trace" per il massimo dettaglio
  }
}
```
Con `trace` si includono timing diagnostici e dettagli sulle hot path.
Nota: `--verbose` alza solo la console, non il file log.

**Opzione 2 — OpenTelemetry export**
Le chiamate ai modelli diventano "children span" della request trace e possono essere esportate via OTLP (es. verso Jaeger, Grafana Tempo). Vedi `/gateway/opentelemetry`.

**Opzione 3 — MLflow Tracing (integrazione esterna)**
Con MLflow tracing ogni LLM span cattura il prompt completo inviato al modello, la risposta e i token counts. Utile per debuggare il ciclo ReAct (reason → act → observe).

### Comandi utili

```bash
# Tail live dei log (raccomandato)
openclaw logs --follow

# Output JSON strutturato
openclaw logs --follow --json

# Log canali specifici (es. Telegram)
openclaw channels logs --channel telegram

# Gateway verbose (solo console, non file)
openclaw gateway --verbose --ws-log compact
```

### Configurazione completa logging

```json
{
  "logging": {
    "level": "info",              // file log level (info/debug/trace)
    "file": "/tmp/openclaw/openclaw-YYYY-MM-DD.log",
    "consoleLevel": "info",       // console verbosity
    "consoleStyle": "pretty",     // pretty | compact | json
    "redactSensitive": "tools",   // maschera token sensibili (default: tools)
    "redactPatterns": ["sk-.*"]   // pattern aggiuntivi da redactare
  }
}
```

### TODO successivi (se si vuole approfondire)

- [ ] Testare con `logging.level: debug` e osservare cosa viene loggato in più
- [ ] Esplorare `/gateway/opentelemetry` per esportare le trace dei modelli
- [ ] Valutare MLflow tracing se serve vedere i prompt completi
