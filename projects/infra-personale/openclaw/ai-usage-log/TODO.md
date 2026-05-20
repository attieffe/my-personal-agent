# AI Usage Log — TODO

## Fatto
- [x] Script ingest.py (parsa log JSONL → SQLite)
- [x] Cron ogni ora (alle :05) — jobId: 1b02b414-6abb-4a89-9153-38e73cd198a9
- [x] DB ~/.openclaw/usage.db operativo (122 record storici già importati)

## In corso / prossimo
- [ ] Migliorare parsing agent_id per sessioni claude-cli (ora "unknown")
- [ ] Aggiungere modello "sonnet" al pricing dict con nome completo
- [ ] Wrapper whisper_transcribe.sh con logging automatico → ~/.openclaw/whisper-usage.jsonl
- [ ] Dashboard Streamlit (grafici temporali, per modello, per agente, export Excel)
- [ ] Reverse proxy Caddy + HTTPS su subdomain da definire con Atti
- [ ] Login (basic auth Caddy)
- [ ] SKILL.md definitivo
- [ ] Aggiungere sezione "infra personale" a progetti.md
