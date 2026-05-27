# cron_fix_plan

Scopo: tenere traccia di cosa ho già provato sui cron che vanno in timeout, e dei prossimi test sensati da fare prima di dire che “non funziona”.

## Già provato

- `cron status`: scheduler attivo.
- `cron list`: i job esistono e sono schedulati correttamente.
- Run manuale di un job TODO reale:
  - job `30b5a7cc-18f4-465a-9098-83a17d9c14e5`
  - esito: `cron: job execution timed out`
  - durata circa 20s.
- Run manuale di un job meteo reale:
  - job `51c138f7-1f73-4ff7-a73d-e0585c52ad67`
  - comportamento anomalo: `already-running` dopo force run.
- Test minimale creato apposta:
  - job `4d1f19e4-6103-48a5-a1f9-5fc6c726082e`
  - prompt: `Rispondi solo con OK.`
  - `timeoutSeconds: 15`
  - esito: timeout comunque (~15s).
- Il job di test è stato poi rimosso.
- Test `systemEvent` minimale:
  - job `7f9e8cb5-c1a9-4cf9-a0db-29fad82ccf96`
  - creato e forzato in run
  - al momento del check non aveva ancora prodotto una run conclusa
  - poi rimosso per pulizia.
- Test `agentTurn` minimale con timeout alto:
  - job `bd2b6179-94ab-472a-b270-a2abf9b0dd14`
  - prompt: `Rispondi solo con OK.`
  - `timeoutSeconds: 90`, `lightContext: true`, nessun tool
  - al momento del check non aveva ancora prodotto una run conclusa
  - poi rimosso per pulizia.

## Cosa sembra emergere

- Il problema non è il trigger cron.
- Il problema sembra stare nell’esecuzione dei job `agentTurn` in sessione isolata, anche con prompt banale.
- I job più pesanti/estesi (TODO, meteo) non sono il solo caso: il timeout avviene anche sul minimo.
- Anche il test `Bash` minimale (`echo CRON_OK`) è finito in timeout.
- Quindi queste prove sono già sufficienti per evitare di rifarle identiche in loop.

## Prossimi test utili

1. **systemEvent minimale**
   - job one-shot con payload `systemEvent`
   - testo tipo `TEST CRON SYSTEMEVENT OK`
   - serve a capire se il cron core completa senza passare da agentTurn.

2. **agentTurn senza tools e con timeout più alto**
   - prompt di una riga
   - `timeoutSeconds` 30/60
   - delivery `none`
   - serve a vedere se è un problema di timeout troppo basso o proprio di bootstrap della sessione isolata.

3. **agentTurn con modello esplicito diverso**
   - provare `gpt-mini` o `cc-sonnet`
   - per escludere un problema specifico di modello.

4. **job con delivery none + sessionTarget current/main**
   - solo se serve confrontare isolato vs corrente.

## Ultimo aggiornamento / heartbeat

- Durante il controllo in heartbeat, è emerso il testo del test `systemEvent`:
  - `TEST CRON SYSTEMEVENT OK`
- Questo conferma che il payload `systemEvent` può arrivare in sessione come promemoria/evento di sistema.
- Però, nel momento dei check, la run non risultava ancora chiusa nelle `cron runs`, quindi resta da capire se:
  - la chiusura è solo ritardata,
  - oppure il reporting di fine run non viene aggiornato correttamente.

## Restart gateway / esito post-restart

- Restart gateway eseguito: il servizio risulta di nuovo attivo con PID aggiornato.
- Dopo il restart ho rifatto un test minimale:
  - job `998b650a-ff12-4c1f-9bff-aec408418317`
  - payload: `echo CRON_OK` via `Bash`
  - esito: ancora `cron: job execution timed out`
- Dal log si vede anche la cleanup del run timed-out:
  - `cron: cleaned up timed-out agent run`
  - `cron: disabling one-shot job after error`
- Quindi il restart del gateway **non ha risolto** il problema.

## Server reboot / test dopo reboot

- Dopo il reboot del server, il gateway risulta di nuovo attivo e raggiungibile.
- Ho rilanciato lo stesso test minimale post-reboot:
  - job `479f9973-808a-4477-9fa2-9ff6f18c39a9`
  - `agentTurn` con `Bash` che esegue `echo CRON_OK`
  - esito: ancora `cron: job execution timed out`
- Il log mostra che il run è partito davvero:
  - `agent harness selected`
  - `embedded run start`
  - `session state ... run_started`
- Quindi anche dopo reboot il problema resta nel path di esecuzione del cron/agent run.

## Nota operativa

Quando rifaccio un test, devo sempre:
- creare un job usa-e-getta
- eseguirlo manualmente
- leggere `cron runs`
- salvare l’esito qui dentro
- cancellare il job di prova se non serve più
