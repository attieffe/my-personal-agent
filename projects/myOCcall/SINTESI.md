# Sintesi — myOCcall

## Cos'è

Un sistema che permette a Ralf di entrare in una videochiamata (Google Meet, Zoom, Teams) come partecipante silenzioso, registrare l'audio, trascriverlo automaticamente e produrre un riassunto strutturato da inviare ad Atti via Telegram.

## Cosa fa

- Entra autonomamente in una call tramite browser
- Cattura l'audio grezzo della call (non la trascrizione della piattaforma)
- Identifica chi parla quando tramite speaker diarization (attivazione microfono)
- Trascrive l'audio con Whisper (OpenAI)
- Produce un riassunto strutturato (non verbatim) con: contesto, argomenti, decisioni, attribuiti al parlante
- Invia il riassunto su Telegram
- Esce dalla call quando scade l'orario di fine previsto, o quando tutti i partecipanti hanno lasciato

## Requisiti funzionali (specifiche di comportamento)

1. **Fonte audio:** deve processare l'audio grezzo della call, NON la trascrizione live della piattaforma (Meet, Zoom, Teams). La qualità della sintesi dipende dall'audio, non dai trascrittori integrati nelle piattaforme.

2. **Speaker diarization:** deve riconoscere chi sta parlando in base all'attivazione del microfono e attribuire ogni intervento al parlante corretto.

3. **Output — sintesi strutturata**, non trascrizione passo-passo:
   - Contesto/inizio della riunione
   - Argomenti trattati
   - Decisioni prese
   - Dettaglio per parlante (chi ha detto cosa, in sintesi)

4. **Exit condition (doppia):**
   - Orario di fine previsto raggiunto
   - Tutti i partecipanti hanno lasciato la call

## Come si usa (quando sarà completo)

1. Manda a Ralf il link della call
2. Ralf entra, ascolta e registra
3. Al termine, ricevi il riassunto su Telegram

## Stato attuale

Infrastruttura audio completata e testata. Il passo successivo è verificare che il browser instradi l'audio verso il sistema di cattura, poi integrare Whisper e costruire la pipeline completa.

## File di riferimento

- Piano completo con tutti gli step: `PLAN.md`
- Guida installazione e configurazione: `docs/setup.md`
- Come riprendere il progetto da zero: sezione finale di `PLAN.md`
