# Inbox Config — [NOME_INBOX]

> Copia questa cartella in `inboxes/[nome]/` e compila tutti i campi contrassegnati con `[DA_COMPILARE]`.
> Poi aggiungi l'inbox al registro in `_system/INBOXES_REGISTRY.md`.

## Identificazione

```
name: [DA_COMPILARE — es. "colzani_personal", "clienti", "myjob"]
email: [DA_COMPILARE — es. "attilio@example.com"]
active: false
description: [DA_COMPILARE — una riga che descrive lo scopo della casella]
```

## Credenziali IMAP

```
credentials_key: [DA_COMPILARE — nome chiave nel file .env, es. IMAP_COLZANI]
credentials_file: ../../.imap_credentials.env
```

## Contesto Default

```
default_context: [DA_COMPILARE — es. COLZANI / PERSONALE / CLIENTI]
default_area: [DA_COMPILARE — area di destinazione per email non categorizzate]
default_fallback_area: EMAIL
lingua_principale: [DA_COMPILARE — italiano / english]
```

## Knowledge Base

```
triage_rules: inboxes/[NOME]/TRIAGE_RULES.md
routing_rules: inboxes/[NOME]/ROUTING_RULES.md
email_threads: inboxes/[NOME]/email_threads.md
interlocutors: _knowledge/INTERLOCUTORS.md        # condiviso — modifica solo se inbox isolata
```

## Cartelle Operative

```
inbox:          inboxes/[NOME]/00_inbox/
to_be_defined:  inboxes/[NOME]/01_to-be-defined/
archive:        inboxes/[NOME]/90_archive/
logs:           inboxes/[NOME]/02_logs/
index:          inboxes/[NOME]/01_to-be-defined/INDEX.md
```

## Destinazioni Task

```
# Dove vengono creati i task dopo la conferma di Attilio
area_default: [DA_COMPILARE — es. projects/myJob/COLZANI/]
# Aggiungi aree specifiche se necessario:
# area_[nome]: projects/[path]/
```

## Regole Speciali

```
# Mittenti con priorità assoluta (istruzioni nel corpo email):
priority_senders:
  - [DA_COMPILARE — es. attilio.fiumano@gruppocolzani.it]

# Domini che mappano automaticamente a un'area:
domain_mappings:
  - domain: [DA_COMPILARE — es. @gruppocolzani.it]
    area: [DA_COMPILARE — es. COLZANI]
```

## Note Operative

[DA_COMPILARE — note libere su come gestire questa inbox, eccezioni, pattern particolari]
