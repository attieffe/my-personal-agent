# CLAUDE.md — Contesto workspace myOcSync

Questo workspace è gestito da **OpenClaw** ed è contemporaneamente un **vault Obsidian**.

## Leggi prima — file di avvio OpenClaw

Prima di operare, carica il contesto da questi file:

- [[AGENTS]] — regole operative, comportamento agent, gestione memoria, routing progetti, heartbeat
- [[IDENTITY]] — identità agent (IAcopo): nome, vibe, emoji, stile di risposta

## Regola fondamentale — link Obsidian

**Tutti i link a file `.md` devono usare la notazione wiki-link Obsidian:**

| Formato | Esempio | Uso |
|---------|---------|-----|
| ✅ Link semplice | `[[nomefile]]` | file con nome unico nel vault |
| ✅ Link con alias | `[[nomefile\|Testo visibile]]` | quando serve etichetta diversa |
| ✅ Link con path | `[[cartella/nomefile\|Testo]]` | per disambiguare file con stesso nome |
| ❌ Mai markdown std | `[testo](percorso.md)` | non funziona in Obsidian |

Questa regola vale per **qualsiasi file `.md`** creato o modificato nel workspace, indipendentemente dallo strumento usato (Claude, Copilot, OpenClaw).

## Lingua

Rispondi sempre in **italiano**. Termini tecnici e identificatori di codice restano in inglese.

## Struttura progetti

| Progetto | Path | Scopo |
|----------|------|-------|
| myJob | `projects/myJob/` | Lavoro: agenzie, clienti, task personali/professionali |
| myOCcall | `projects/myOCcall/` | Trascrizione e sintesi automatica di videocall |
| miotesoro-sheet-agent | `projects/miotesoro-sheet-agent/` | Gestione finanziaria su Google Sheets |

Registro completo: [[progetti]]

## Convenzioni operative

Riferimento completo: [[projects/myJob/CONVENTIONS]]

Punti chiave:
- Nomenclatura: `snake_case` per file, `YYYY-MM-DD` per date
- TODO routing per contesto → sezione 6 di CONVENTIONS
- Struttura agenzie FREELANCE → sezione 10 di CONVENTIONS
- Archiviazione task chiusi → sezione 7 di CONVENTIONS
- Stati TODO (`[ ]` / `[-]` / `[~]` / `[x]`) → sezione 8 di CONVENTIONS
- Censimento persone/ruoli → sezione 9 di CONVENTIONS

## Path corretti da ricordare

| Alias storico | Path reale |
|---------------|-----------|
| `ATTILIO_A_CASA/` | `projects/myJob/PERSONALE/` |
| Agenzie | `projects/myJob/FREELANCE/<AGENZIA>/` |
| Clienti diretti freelance | `projects/myJob/FREELANCE/DIRETTI/<cliente>/` |
