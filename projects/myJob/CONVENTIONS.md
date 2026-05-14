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
