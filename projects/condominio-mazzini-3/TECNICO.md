# TECNICO — Condominio Mazzini 3

## Stack

- **Gemini API**: `google-genai` Python lib · modello `gemini-3.1-flash-image`
- **API Key**: in `/home/openclaw/attibot/condominio/.env` (GEMINI_API_KEY=...)
- **Fatturazione**: Google AI Studio — attivata 2026-06-10
- **Fallback modelli**: gemini-3.1-flash-image → gemini-3.1-flash-image-preview → gemini-3-pro-image

## Pipeline

```
RENDERING_QUEUE.json  →  gemini_render.py  →  img/{CODE}_foto{N}.jpg  →  proposte_facciate.html
```

Cron `208b5757` ogni ora → script → notifica Telegram → auto-disable quando queue vuota.

## Prompt Structure

Ogni proposta genera 3 immagini con prompt differenziato per focus:
- `foto1` → **facciata** (colore dominante su superfici murarie principali)
- `foto2` → **balconi** (colore secondario su fasce e soffitti balconi)
- `foto3` → **dettagli** (colore accessorio su contorni e bordi strutturali)

Tutti e 3 i prompt includono la palette completa (dominante + secondario + accessorio) e vincoli espliciti su: geometria, finestre, tapparelle Douglas, cielo, vegetazione, strada.

## Aggiornare il cron se cambia path script

```
cron update 208b5757 → payload.message con nuovo path
```

## Web server

- Nginx su `attibot.ingeniosolution.it`
- `/reports/*` → `/home/openclaw/attibot/reports/`
- `/home/openclaw/attibot/condominio/` è la stessa dir tramite hardlink
