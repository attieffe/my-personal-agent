# EMAIL (myjob@ingeniosolution.it)

Qui gestiamo il flusso: triage richieste → assegnazione a ramo/progetto → aggiornamento file.

## Processo cron di lettura email

Questo è il processo che parte quando chiedo di far girare il task inbox di myjob:

- legge la posta IMAP in sola lettura
- identifica le nuove mail e le raggruppa per richiesta / thread
- distingue tra:
  - nuovo scope
  - continuazione di un task esistente
  - inoltro o notifica di attività già presa in carico
- aggiorna i file del progetto solo quando serve e solo dopo conferma per le azioni non banali
- non fa azioni distruttive in automatico
- restituisce l’esito qui nella chat Telegram da cui è stato avviato il task

Riferimento operativo: `INBOX_WORKFLOW.md`.

## Nota importante (sicurezza)
Non mettere credenziali IMAP/SMTP in chiaro in questi file.

## Prossimo step
Quando mi confermi che possiamo procedere, preparo la configurazione con:
- host
- porta
- SSL/TLS
- username
- metodo sicuro per password (es. app-password)
