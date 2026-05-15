# Inbox Config — myjob@ingeniosolution.it

## Identificazione

```
name: myjob
email: myjob@ingeniosolution.it
active: true
description: Casella di lavoro principale — email di coordinamento IT, clienti, team Colzani
```

## Credenziali IMAP

```
credentials_key: IMAP_MYJOB
credentials_file: ../../.imap_credentials.env
```

## Contesto Default

```
default_context: COLZANI
default_area: COLZANI
default_fallback_area: EMAIL
lingua_principale: italiano
```

## Knowledge Base

```
triage_rules: inboxes/myjob/TRIAGE_RULES.md
routing_rules: inboxes/myjob/ROUTING_RULES.md
email_threads: inboxes/myjob/email_threads.md
interlocutors: _knowledge/INTERLOCUTORS.md        # condiviso tra tutte le inbox
```

## Cartelle Operative

```
inbox:          inboxes/myjob/00_inbox/
to_be_defined:  inboxes/myjob/01_to-be-defined/
archive:        inboxes/myjob/90_archive/
logs:           inboxes/myjob/02_logs/
index:          inboxes/myjob/01_to-be-defined/INDEX.md
```

## Destinazioni Task (dove finiscono i task creati)

```
area_colzani:   projects/myJob/COLZANI/
area_diretti:   projects/myJob/DIRETTI/
area_default:   projects/myJob/EMAIL/
```

## Note Operative

- Le istruzioni esplicite di Attilio Fiumanò (`attilio.fiumano@gruppocolzani.it`) hanno priorità assoluta
- Email con dominio `@gruppocolzani.it` → area COLZANI per default
- In caso di ambiguità → proponi `chiarimento` invece di agire
