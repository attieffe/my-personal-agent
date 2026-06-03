# TODO — Archiviazione Ottica Documenti

## Da fare

- [ ] Implementare `_system/vision_namer.py` — analisi documento via Claude vision API
- [ ] Implementare `_system/drive_uploader.py` — copia file su Drive via rclone
- [ ] Implementare `_system/archiver.py` — orchestratore principale (intake → analisi → proposta → conferma → archiviazione)
- [ ] Configurare ascolto topic Telegram (chat_id -1003877516285, topic_id 2069) per allegati in arrivo
- [ ] Aggiungere regole routing: BOLLETTE, BANCA, ASSICURAZIONI, FISCALE_PERSONALE
- [ ] Testare con un documento reale end-to-end

## Backlog

- [ ] OCR testo completo per ricerca full-text futura
- [ ] `_knowledge/MITTENTI.md` per autoapprendimento mittenti → categoria
- [ ] Report periodico "documenti archiviati questo mese"
