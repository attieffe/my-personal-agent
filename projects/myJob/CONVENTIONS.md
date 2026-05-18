# CONVENTIONS.md — convenzioni operative

## 1) Nomination & layout
- Cartelle: `snake_case` quando possibile (es. `ballabio_cucine`), ma mantieni quelli già esistenti (es. `Ballabio_Cucine`).
- File: `snake_case`.
- Date: `YYYY-MM-DD`.
- Ogni “radice” (una directory cliente/progetto/area) contiene sempre `00_index.md`.

## 2) Numerazione sezioni
Usa prefissi numerici a due cifre per ordinare:
- `00_` → contesto e indice
- `01_` → raccolta/indagine
- `02_` → analisi/design
- `03_` → esecuzione/decisioni
- `04_` → deliverable
- `90_` → archivio

## 3) Documenti: come scriverli
- Ogni decisione importante va tracciata in un file dedicato o in `03_decisioni/*.md`.
- Se un documento cambia: aggiorna `meta:` con data e autore (anche solo “io”).

## 4) Tracciamento incontri
- Note incontro: una cartella per data o un file “log”.
- In ogni nota includi: *Obiettivo*, *Decisioni*, *Azioni (owner + scadenza)*.

## 5) Email
- Gli export email vanno in `EMAIL/00_inbox/` o `EMAIL/01_sent/`.
- I thread vanno indicizzati in `EMAIL/02_logs/email_threads.md` (per rintracciare cosa c’è senza aprire tutto).
## 6) Routing TODO personale di Attilio
Quando il sistema (es. myOCcall post-sintesi) deve aggiungere un TODO personale ad Attilio, usare questo routing:

| Contesto dell'attività | File di destinazione |
|------------------------|----------------------|
| Lavoro COLZANI (IT, gestione, operativo) | [[COLZANI/PERSONALI/README]] (sezione TODOLIST) |
| Sfera privata / casa / personale | [[PERSONALE/01_todo_riassuntivo]] |
| Clienti diretti / extra Colzani | [[PERSONALE/lavori_a_casa/42_clienti_diretti]] |
| Agenzie freelance (task operativi) | `FREELANCE/<AGENZIA>/README.md` (sezione TODO/Backlog) |
| Contesto non identificabile con certezza | [[DA_DEFINIRE]] nella root di myJob (creare se non esiste) |

> **Nota path**: la cartella `PERSONALE/` era storicamente chiamata `ATTILIO_A_CASA/` — usare sempre `PERSONALE/` nei link.

Regola pratica: se non sai con certezza a quale "mondo" appartiene un task, mettilo in [[DA_DEFINIRE]] per revisione manuale successiva.

## 7) Archiviazione task chiusi
- Ogni contesto/radice operativa deve avere un file `ARCHIVIATI.md`.
- Quando un TODO si chiude, va rimosso dal backlog aperto e spostato in `ARCHIVIATI.md` del contesto giusto.
- Nel record di archivio indicare sempre almeno:
  - cliente/progetto
  - titolo del task
  - `data_chiusura` in formato `YYYY-MM-DD`
  - stato finale (`chiuso`, `risolto`, `annullato`, ecc.)
  - note/contesto utile
- I file backlog devono contenere solo task ancora aperti.

## 8) Stati TODO — ogni task deve avere uno stato esplicito

Ogni task nei file TODO deve riportare **sempre** uno stato. Esistono due formati:

**Formato A — compatto** · usato in: `TODO.md`, `TODO_GENERALE.md`, `01_todo_riassuntivo.md`
→ riga unica: `- [stato] [TAG] Titolo — dettaglio · ref: [[link]]`

**Formato B — TEAM** · usato in: `TEAM/Fabio_TODO.md`, `TEAM/Alessandro_TODO.md`
→ riga compatta: `- [stato] [SCADENZA se presente] Titolo — eventuali link`
→ sub-bullet con date per log avanzamento: `  - GG/MM/YYYY → nota`
→ NO Owner (il file è già intestato alla persona); scadenza nel titolo solo se esiste

---

### Stati base (checkbox — validi in entrambi i formati)

| Checkbox | Significato |
|----------|-------------|
| `[ ]` | Aperto / da fare |
| `[-]` | In corso / assegnato / attivo |
| `[~]` | In attesa (risposta, evento, sblocco esterno) |
| `[x]` | Chiuso → spostare in ARCHIVIATI.md |

### Tag opzionali aggiuntivi (in coda al checkbox)

| Tag | Significato |
|-----|-------------|
| `[URGENTE]` | Priorità alta |
| `[DELEGATO]` | Assegnato e gestito da altri |
| `[DA-DISCUTERE]` | Da valutare/approvare prima di procedere |
| `[ANNULLATO]` | Non più rilevante — usare insieme a `[x]` |

Regola pratica: se aggiungi un task senza stato esplicito, assegna `[ ]` (aperto) come default.

## 9) Censimento persone e ruoli → GLOSSARIO

Ogni volta che emerge una persona con ruolo, titolo o afferenza a un'entità:
- Va censita nel file glossario/referenti del contesto corretto (vedi tabella sotto)
- Includere sempre: nome completo, ruolo, entità di afferenza, eventuali cross-link ad altri contesti

| Contesto persona | File di censimento |
|------------------|-------------------|
| Gruppo Colzani (SPORTIT, BRICOSPORT, COLZANI SRL, ecc.) | [[COLZANI/GLOSSARIO]] |
| GET ME DIGITAL | [[FREELANCE/GET_ME_DIGITAL/README]] (sezione Referenti) |
| SINAPPS | [[FREELANCE/SINAPPS/README]] (sezione Referenti) |
| NEWU SRL | [[FREELANCE/NEWU_SRL/README]] (sezione Referenti) |
| STUDIO VISUAL | [[FREELANCE/STUDIO_VISUAL/README]] (sezione Referenti) |
| Clienti diretti | `FREELANCE/DIRETTI/<cliente>/README.md` (sezione Referenti) |
| Personale / famiglia | [[PERSONALE/README]] |
| Trasversale a più contesti | Censire in **tutti** i contesti coinvolti con cross-link |

Regola pratica: "Neda Bazzana lavora per GMD + SPORTIT + BRICOSPORT" → la aggiungo in GLOSSARIO.md (sezioni SPORTIT + BRICOSPORT) **e** in GET_ME_DIGITAL/README.md.

---

## 10) Agenzie FREELANCE — struttura e censimento

Ogni agenzia con cui si collabora ha una cartella dedicata in `FREELANCE/<NOME_AGENZIA>/`.

### Agenzie registrate

| Agenzia | Cartella | Attiva dal |
|---------|----------|-----------|
| GET ME DIGITAL SRL | [[FREELANCE/GET_ME_DIGITAL/README\|FREELANCE/GET_ME_DIGITAL/]] | 2017 |
| SINAPPS (T PROJECT SRL) | [[FREELANCE/SINAPPS/README\|FREELANCE/SINAPPS/]] | ~2018 |
| NEWU SRL | [[FREELANCE/NEWU_SRL/README\|FREELANCE/NEWU_SRL/]] | 2023 |
| STUDIO VISUAL | [[FREELANCE/STUDIO_VISUAL/README\|FREELANCE/STUDIO_VISUAL/]] | — |

### Regola: censimento nuova agenzia

Quando si aggiunge una nuova agenzia:

1. **Crea la cartella** `FREELANCE/<NOME_AGENZIA>/`
2. **Crea `README.md`** con: ragione sociale, contesto/storia collaborazione, referenti, link struttura
3. **Crea `CHANGELOG.md`** con data di inizializzazione
4. **Crea `PROGETTI/README.md`** con convenzione naming (`PROJ-<Agenzia>-<slug>-<YYYYMMDD>`) e link al template `_TEMPLATE/PROGETTO_TEMPLATE.md`
5. **Aggiungi riga** alla tabella sopra con wiki-link all'area workspace
6. **Aggiorna [[PERSONALE/lavori_a_casa/41_clienti_agenzie]]** con la nuova sezione agenzia
7. **Censisci i referenti** secondo la tabella sezione 9

### Struttura minima di ogni cartella agenzia

```
FREELANCE/<AGENZIA>/
  README.md          ← anagrafica, referenti, TODO/backlog, link struttura
  CHANGELOG.md       ← log modifiche del ramo
  ARCHIVIATI.md      ← task chiusi (creare quando serve il primo)
  PROGETTI/
    README.md        ← convenzione naming + lista progetti attivi
    PROJ-<Agenzia>-<slug>-<YYYYMMDD>/
      README.md      ← scheda progetto (usa _TEMPLATE/PROGETTO_TEMPLATE.md)
```
