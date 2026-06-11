# Condominio Mazzini 3 — Rifacimento Facciate

**Indirizzo:** Via Pacini 77/79/81, Seregno  
**Lavoro:** Rifacimento colorazione facciate  
**Tapparelle:** Marrone Douglas (invariato — vincolo per tutte le proposte)

## Obiettivo

Simulazioni cromatiche per 24 proposte di colore facciata, da presentare in assemblea condominiale.  
Ogni proposta = 3 rendering Gemini (facciata · balconi · dettagli).

## Stato

- Proposte totali: **24** (famiglie A, B, C, D, E, F)
- Pipeline Gemini: attiva (cron orario, ID `208b5757`)
- Web page: https://attibot.ingeniosolution.it/reports/condominio/proposte_facciate.html

## File chiave

| File | Posizione |
|------|-----------|
| Coda rendering | `RENDERING_QUEUE.json` (questo progetto) |
| Script Gemini | `gemini_render.py` (questo progetto) |
| Script PIL (backup) | `condominio_color_render.py` (questo progetto) |
| Immagini output | `/home/openclaw/attibot/condominio/img/` |
| Foto originali | `/home/openclaw/attibot/condominio/img/originali/` |
| Pagina HTML | `/home/openclaw/attibot/condominio/proposte_facciate.html` |

## Come aggiungere nuovi rendering

Appendere a `RENDERING_QUEUE.json` → `queue[]` un nuovo item con `status: "pending"`.  
Il cron lo processerà automaticamente entro l'ora successiva.
