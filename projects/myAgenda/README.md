# myAgenda

Utility di schedulazione personale di Atti. Recupera i calendari live e le preferenze personali, e propone slot ottimali quando richiesto.

## Come invocare

Scrivi ad IAcopo:
- "Trovami uno slot per una call di 30 minuti con X questa settimana"
- "Ho bisogno di 2 ore di focus time entro venerdì — quando?"
- "Quando posso organizzare una riunione Colzani di un'ora?"
- "Controlla se giovedì pomeriggio sono libero"

## Struttura

```
myAgenda/
├── README.md                    — questo file
├── CHANGELOG.md                 — versioni e modifiche
├── agents/
│   └── myagenda.agent.md        — agente principale (user-invocable)
├── calendars/
│   ├── README.md                — fonti live e istruzioni
│   └── myagenda_oc.ics          — calendario proposte (unico file scrivibile)
└── preferences/
    ├── vincoli.md               — vincoli temporali fissi
    └── priorita.md              — priorità e contesti
```

## Calendari

I calendari vengono recuperati **live** via curl ogni volta — nessun file statico locale.
Fonti: Outlook Colzani, Google Calendar personale, Playtomic padel.
Vedi `calendars/README.md` per i link.

## Proposte slot

L'agente scrive le proposte direttamente su **Google Calendar myAgenda OC** via API (OAuth già autorizzato in `_credentials/google_token.json`). Nessun file locale.

## Stato

- [x] Calendari: fonti live configurate (no file statici)
- [x] myAgenda OC: calendario proposte creato
- [x] Agente configurato
- [ ] Preferenze da completare (Atti le dettaglierà)
