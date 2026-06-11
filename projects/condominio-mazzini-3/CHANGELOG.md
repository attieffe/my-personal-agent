# CHANGELOG

## 2026-06-10
- Progetto creato in `projects/condominio-mazzini-3/`
- Pipeline Gemini completa: RENDERING_QUEUE.json + gemini_render.py + cron orario
- B1 primo rendering Gemini completato (billing attivato)
- Reset queue: tutte le 24 proposte in pending per rigenerazione con Gemini
- Pagina HTML responsive con 24 proposte, slider + lightbox

## 2026-06-11
- B5 completato con `render_and_publish.py`
- Pagina pubblicata aggiornata su `proposte_facciate.html`
- Swap immagine di base: foto4.jpg originale (124KB, duplicato) → nuova immagine WhatsApp (1.1MB)
- Reset proposte: eliminati `proposte_facciate.html` e `TODO_RENDERING.json` per rigenerazione con nuova foto
