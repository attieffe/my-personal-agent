# GitHub Copilot — Istruzioni workspace myOcSync

## Contesto del workspace

Questo workspace è un progetto **OpenClaw** e un vault **Obsidian**.

- Leggi `AGENTS.md` per capire le regole operative, la gestione memoria, il routing progetti e il comportamento atteso dall'agent AI.
- Leggi `IDENTITY.md` per capire l'identità dell'agent (AttiBot — assistente AI con mentalità da ingegnere informatico).
- Leggi `projects/myJob/CONVENTIONS.md` per le convenzioni operative specifiche del progetto di gestione lavoro.

## Lingua

Rispondi sempre in **italiano**. I termini tecnici e gli identificatori di codice restano in inglese.

## Regola fondamentale — link Obsidian

Tutti i link a file `.md` **devono** usare la notazione wiki-link Obsidian:

```
✅ Corretto:  [[nomefile]]
✅ Con alias: [[nomefile|Testo visibile]]
✅ Con path:  [[cartella/nomefile|Testo]]

❌ Mai:       [testo](percorso.md)   ← markdown standard non funziona in Obsidian
```

Questa regola si applica a **tutti i file `.md`** del workspace, senza eccezioni.

## Struttura progetti

Il workspace contiene questi progetti principali (sotto `projects/`):

- `myJob/` — gestione lavoro: agenzie, clienti freelance, task personali e professionali
- `myOCcall/` — sistema di trascrizione e sintesi automatica di videocall
- `miotesoro-sheet-agent/` — gestione finanziaria su Google Sheets

## Convenzioni operative (`projects/myJob/CONVENTIONS.md`)

- **Nominazione**: `snake_case` per file, `YYYY-MM-DD` per date
- **TODO routing** per contesto (sezione 6): ogni task va nel file giusto in base all'area
- **Agenzie**: cartelle sotto `projects/myJob/FREELANCE/<AGENZIA>/` — ogni agenzia ha `README.md`, `CHANGELOG.md`, `PROGETTI/README.md`
- **Archiviazione**: task chiusi → `ARCHIVIATI.md` del contesto corretto (sezione 7)
- **Stati TODO**: `[ ]` aperto / `[-]` in corso / `[~]` in attesa / `[x]` chiuso (sezione 8)
- **Censimento persone**: ogni persona con ruolo va censita nel glossario/referenti del contesto (sezione 9)

## Path critici da ricordare

| Alias vecchio | Path reale |
|---------------|-----------|
| `ATTILIO_A_CASA/` | `projects/myJob/PERSONALE/` |
| Agenzie freelance | `projects/myJob/FREELANCE/<AGENZIA>/` |
| Clienti diretti | `projects/myJob/FREELANCE/DIRETTI/<cliente>/` |
