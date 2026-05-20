# AI Usage Log — Documentazione Tecnica

## Obiettivo

Tracciare tutte le interazioni di OpenClaw con i modelli AI (Claude, Whisper, ecc.) in un database SQLite locale, con dashboard web per visualizzazione e analisi.

## Architettura

```
Log JSONL OpenClaw
    ↓ (ingest.py ogni ora via cron)
SQLite (~/.openclaw/usage.db)
    ↓
Streamlit dashboard (localhost:8501)
    ↓ (Caddy reverse proxy)
https://<subdomain> (internet, con login)
```

## Fonti dati

### Provider claude-cli
- Log livello: **INFO**
- Righe chiave: `cli exec` (promptChars, model, trigger) + `claude live session turn` (durationMs)

### Provider embedded / OAuth (github-copilot, anthropic diretto)
- Log livello: **DEBUG** (necessario)
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
| `log_file` | TEXT | file sorgente (per dedup) |
| `log_offset` | INTEGER | byte offset (ingest incrementale) |
| `agent_id` | TEXT | main, miotesoro, attibot-colzani… |
| `source_type` | TEXT | cron / direct / heartbeat |
| `source_name` | TEXT | nome cron o canale (telegram) |
| `provider` | TEXT | claude-cli, github-copilot, openai |
| `model` | TEXT | claude-haiku-4-5, whisper-1… |
| `prompt_chars` | INTEGER | chars prompt utente |
| `system_chars` | INTEGER | chars system prompt |
| `history_chars` | INTEGER | chars cronologia |
| `duration_ms` | INTEGER | durata turn in ms |
| `audio_seconds` | INTEGER | solo Whisper |
| `tokens_est` | INTEGER | (prompt+system+history)/4 |
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
| Log OpenClaw | `/tmp/openclaw/openclaw-YYYY-MM-DD.log` |
| Log Whisper extra | `~/.openclaw/whisper-usage.jsonl` |
| Script ingest | `~/.openclaw/plugin-skills/ai-usage-log/scripts/ingest.py` |
| Dashboard | `~/.openclaw/plugin-skills/ai-usage-log/scripts/dashboard.py` |

## Livello log richiesto

`logging.level: "debug"` in `~/.openclaw/openclaw.json` — già attivo.

## TODO

- [ ] Script ingest.py (cron ogni ora)
- [ ] Wrapper whisper con logging
- [ ] Dashboard Streamlit
- [ ] Reverse proxy Caddy + HTTPS
- [ ] Login (basic auth Caddy o Streamlit secrets)
