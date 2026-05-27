# AI Usage Log — Documentazione Tecnica

## Obiettivo

Tracciare tutte le interazioni di OpenClaw con i modelli AI (Claude, Whisper, ecc.) in un database SQLite locale, con dashboard web per visualizzazione e analisi.

## Architettura

```
*.trajectory.jsonl sotto ~/.openclaw/agents/**/sessions/
    ↓ (ingest.py ogni ora via cron)
SQLite (~/.openclaw/usage.db)
    ↓
Streamlit dashboard (localhost:8501)
    ↓ (Caddy reverse proxy)
https://<subdomain> (internet, con login)
```

## Fonti dati

### Provider/sessioni OpenClaw
- Fonte primaria: `*.trajectory.jsonl` nelle sessioni agent
- Record chiave: `type = "model.completed"`
- Campi disponibili: `ts`, `sessionId`, `sessionKey`, `runId`, `workspaceDir`, `provider`, `modelId` / `modelApi`
- Usage dettagliato: `data.usage.input`, `data.usage.output`, `data.usage.cacheRead`, `data.usage.cacheWrite`, `data.usage.total`

### Provider embedded / OAuth (github-copilot, anthropic diretto)
- Ancora supportato dal parser legacy dei log text-based
- Riga chiave: `[context-diag] pre-prompt` (promptChars, systemChars, historyChars, model)
- Riga chiave: `embedded run done` (durationMs)

### Whisper (OpenAI Audio)
- Non passa per i log OpenClaw
- Tracciato da wrapper `whisper_transcribe.sh` → appende riga al log separato `~/.openclaw/whisper-usage.jsonl`

## Database

File: `~/.openclaw/usage.db`

### Tabella `ai_calls`

| Campo | Tipo | Note |
|---|---|---|
| `id` | INTEGER PK | autoincrement |
| `ts` | DATETIME | ora italiana (Europe/Rome) |
| `source_kind` | TEXT | trajectory / whisper / legacy-log |
| `source_file` | TEXT | file sorgente (per dedup) |
| `source_offset` | INTEGER | byte offset (ingest incrementale) |
| `agent_id` | TEXT | main, miotesoro, attibot-colzani… |
| `source_type` | TEXT | cron / direct / heartbeat |
| `channel` | TEXT | telegram / cron / direct |
| `sender_id` | TEXT | mittente chat se presente |
| `sender_username` | TEXT | username chat se presente |
| `sender_display` | TEXT | nome leggibile chat se presente |
| `cron_name` | TEXT | nome cron se presente |
| `provider` | TEXT | claude-cli, github-copilot, openai |
| `model` | TEXT | claude-sonnet-4.6, whisper-1… |
| `session_key` | TEXT | chiave sessione OpenClaw |
| `session_id` | TEXT | id sessione runtime |
| `run_id` | TEXT | id singolo run |
| `workspace_dir` | TEXT | cartella di lavoro |
| `model_api` | TEXT | api/model family usata internamente |
| `input_tokens` | INTEGER | token input del modello |
| `output_tokens` | INTEGER | token output del modello |
| `cache_read_tokens` | INTEGER | token letti da cache |
| `cache_write_tokens` | INTEGER | token scritti in cache |
| `total_tokens` | INTEGER | totale riportato dalla sessione |
| `prompt_chars` | INTEGER | chars prompt utente |
| `system_chars` | INTEGER | chars system prompt |
| `history_chars` | INTEGER | chars cronologia |
| `duration_ms` | INTEGER | durata turn in ms |
| `audio_seconds` | INTEGER | solo Whisper |
| `tokens_est` | INTEGER | fallback stimato se `total_tokens` manca |
| `cost_est_usd` | REAL | stima basata su prezzi modello |

### Tabella `ingest_state`

Tiene traccia dell'ultimo byte letto per ogni file di log (ingest incrementale).

## Prezzi modello (stima costi)

Aggiornare in `scripts/model_pricing.py` al cambio tariffe.

| Modello | Input $/1M tok | Output $/1M tok |
|---|---|---|
| claude-haiku-4-5 | 0.80 | 4.00 |
| claude-sonnet-4-6 | 3.00 | 15.00 |
| claude-opus-4-7 | 15.00 | 75.00 |
| whisper-1 | 0.006/min | — |

## File e path

| File | Path |
|---|---|
| DB SQLite | `~/.openclaw/usage.db` |
| Session JSONL OpenClaw | `~/.openclaw/agents/**/sessions/*.trajectory.jsonl` |
| Log OpenClaw legacy | `/tmp/openclaw/openclaw-YYYY-MM-DD.log` |
| Log Whisper extra | `~/.openclaw/whisper-usage.jsonl` |
| Script ingest | `~/.openclaw/plugin-skills/ai-usage-log/scripts/ingest.py` |
| Dashboard | `~/.openclaw/plugin-skills/ai-usage-log/scripts/dashboard.py` |

## Livello log richiesto

`logging.level: "debug"` in `~/.openclaw/openclaw.json` — già attivo.

## TODO

- [x] Script ingest.py (cron ogni ora)
- [ ] Wrapper whisper con logging
- [x] Dashboard Streamlit
- [ ] Reverse proxy Caddy + HTTPS
- [ ] Login (basic auth Caddy o Streamlit secrets)
