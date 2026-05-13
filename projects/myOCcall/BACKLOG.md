# BACKLOG — myOCcall

Tutto ciò che vogliamo costruire, validare o migliorare nel sistema.
Aggiungere qui nuove feature, idee e task di setup man mano che emergono.

---

## Setup & validazione piattaforme

- [ ] Join automatico su **Google Meet** — verificare funzionamento, raccogliere istruzioni di join
- [ ] Join automatico su **Zoom** — test e istruzioni di join
- [ ] Join automatico su **Teams** — test e istruzioni di join
- [ ] Step 5 — Configurazione credenziali per piattaforma

## Feature & miglioramenti

- [ ] **Avvio automatico registrazione ffmpeg al join** — la cattura audio deve partire contestualmente al join nella call, non manualmente. Attualmente il null sink è attivo ma ffmpeg non viene avviato. Priorità alta.

---

## Completato

- [x] Analisi fattibilità stack Linux headless
- [x] Installazione PulseAudio + ffmpeg
- [x] Configurazione null sink `virtual_out`
- [x] Test cattura audio ffmpeg — OK (68kB MP3)
- [x] Script `scripts/start-audio.sh` (avvio idempotente)
- [x] Autostart in `~/.bashrc`
- [x] Step 3 — Playwright Chromium installato, audio browser → virtual_out → parec confermato (-6.2 dB)
