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
| Lavoro COLZANI (IT, gestione, operativo) | `COLZANI/PERSONALI/README.md` (sezione TODOLIST) |
| Sfera privata / casa / personale | `ATTILIO_A_CASA/01_todo_riassuntivo.md` |
| Clienti diretti / extra Colzani | `ATTILIO_A_CASA/lavori_a_casa/42_clienti_diretti.md` |
| Contesto non identificabile con certezza | Appendere a `DA_DEFINIRE.md` nella root di myJob (creare se non esiste) |

Regola pratica: se non sai con certezza a quale "mondo" appartiene un task, mettilo in `DA_DEFINIRE.md` per revisione manuale successiva.

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

Ogni task nei file TODO deve riportare **sempre** uno stato. Stati ammessi:

| Stato | Markdown | Significato |
|-------|----------|-------------|
| Aperto | `[ ]` | Da fare, nessun blocco |
| Urgente | `[ ]` + tag `[URGENTE]` | Da fare con priorità alta |
| In corso | `[-]` o tag `[IN_CORSO]` | Avviato, non concluso |
| In attesa | `[~]` o tag `[ATTESA]` | Bloccato su risposta/evento esterno |
| Chiuso | `[x]` | Completato — poi spostare in ARCHIVIATI.md |
| Annullato | `[x]` + tag `[ANNULLATO]` | Non più rilevante |

Regola pratica: se aggiungi un task senza stato esplicito, il sistema deve richiedere chiarimento o assegnare `[ ]` (aperto) come default.

## 9) Censimento persone e ruoli → GLOSSARIO

Ogni volta che emerge una persona con ruolo, titolo o afferenza a un'entità:
- Va censita nel file glossario/referenti del contesto corretto (vedi tabella sotto)
- Includere sempre: nome completo, ruolo, entità di afferenza, eventuali cross-link ad altri contesti

| Contesto persona | File di censimento |
|------------------|-------------------|
| Gruppo Colzani (SPORTIT, BRICOSPORT, COLZANI SRL, ecc.) | `COLZANI/GLOSSARIO.md` |
| GET ME DIGITAL | `FREELANCE/GET_ME_DIGITAL/README.md` (sezione Referenti) |
| SINAPPS | `FREELANCE/SINAPPS/README.md` (sezione Referenti) |
| Clienti diretti | `FREELANCE/DIRETTI/<cliente>/README.md` |
| Personale / famiglia | `PERSONALE/README.md` |
| Trasversale a più contesti | Censire in **tutti** i contesti coinvolti con cross-link |

Regola pratica: "Neda Bazzana lavora per GMD + SPORTIT + BRICOSPORT" → la aggiungo in GLOSSARIO.md (sezioni SPORTIT + BRICOSPORT) **e** in GET_ME_DIGITAL/README.md.
