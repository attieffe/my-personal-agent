# Inbox Config — aos@ingeniosolution.it

## Identificazione

```
name: aos
email: aos@ingeniosolution.it
active: true
description: Casella Archiviazione Ottica Sostitutiva — riceve documenti da archiviare via email o inoltro
```

## Credenziali IMAP

```
credentials_key: IMAP_AOS
credentials_file: ../../.imap_credentials.env
```

## Contesto Default

```
default_context: ARCHIVIAZIONE_OTTICA
default_area: DOCUMENTI
default_fallback_area: ALTRO
lingua_principale: italiano
```

## Cartelle Operative

```
inbox:    inboxes/aos/00_inbox/
logs:     inboxes/aos/02_logs/
archive:  inboxes/aos/90_archive/
```

## Note Operative

- Ogni email può contenere documenti allegati da archiviare su Google Drive.
- Il mittente dell'email potrebbe essere Atti stesso che inoltra un documento ricevuto altrove.
- Il "mittente reale" del documento (chi ha spedito la comunicazione originale) va estratto
  dall'oggetto, dal corpo, o dagli header dell'email inoltrata — NON dal From: dell'inoltro.
- Per ogni allegato: eseguire analisi con archiver.py, proporre ad Atti, attendere conferma.
- Il cron gira ogni 10 minuti.
- Allegati non-documento (immagini inline, firme) vanno ignorati.
- Se un'email non ha allegati o allegati rilevanti, notificare solo se il corpo contiene
  un documento embedded (es. testo di fattura nel body).
