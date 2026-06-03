# Archiviazione Ottica Documenti — Sintesi

Sistema AI per archiviare documenti fisici (scansioni/foto) ricevuti per posta ordinaria o in altro modo.

## Cosa fa

Riceve documenti da 3 canali:
1. **Topic Telegram** "Archiviazione documenti" — allegati inviati direttamente
2. **Upload manuale** — tramite AttiBot (`https://attibot.ingeniosolution.it/upload`)
3. **Cartella `input/`** — file copiati a mano nel progetto

Per ogni documento:
- Analizza il contenuto (vision AI) per capire di cosa si tratta
- Estrae la data dal documento (non dalla data di invio)
- Propone un nome parlante: `YYYYMMDD titolo documento.ext`
- Identifica la categoria e le destinazioni Drive
- **Chiede conferma ad Atti** prima di archiviare
- Copia il file su Drive (una o più destinazioni secondo le regole)
- Registra in `history.md`
- Non cancella mai il file originale

## Canale Telegram

- **Gruppo/topic:** Archiviazione documenti
- **chat_id:** -1003877516285
- **topic_id:** 2069

## Dove vanno i documenti

Destinazione primaria (sempre):
`Il mio Drive/Atti/Documenti/Archiviazione ottica/ANNO/YYYYMMDD titolo.ext`

Destinazioni aggiuntive per categoria → vedi `_knowledge/ROUTING_RULES.md`
