# myAgenda

Utility di schedulazione personale di Atti. Legge i calendari reali (file .ics) e le preferenze personali, e propone slot ottimali quando richiesto.

## Come invocare

Scrivi ad AttiBot:
- "Trovami uno slot per una call di 30 minuti con X questa settimana"
- "Ho bisogno di 2 ore di focus time entro venerdì — quando?"
- "Quando posso organizzare una riunione Colzani di un'ora?"
- "Controlla se giovedì pomeriggio sono libero"

L'agente legge i calendari e le preferenze e risponde con proposte concrete.

## Struttura

```
myAgenda/
├── README.md                    — questo file
├── CHANGELOG.md                 — versioni e modifiche
├── agents/
│   └── myagenda.agent.md        — agente principale (user-invocable)
├── calendars/
│   ├── README.md                — istruzioni aggiornamento calendari
│   └── *.ics                    — file calendario (da aggiungere)
└── preferences/
    ├── vincoli.md               — vincoli temporali fissi
    └── priorita.md              — priorità e contesti
```

## Aggiornamento calendari

I file `.ics` si aggiornano periodicamente (export da Google Calendar / Outlook).
Vedi `calendars/README.md` per istruzioni dettagliate.

## Stato

- [ ] Calendari da aggiungere (Atti li fornirà)
- [ ] Preferenze da completare (Atti le dettaglierà)
- [x] Struttura base creata
- [x] Agente configurato
