---
description: Analizza un'email in ingresso e produce il companion .md con proposta di azione e aggiorna l'INDEX.
applyTo: "projects/email-ingestion/inboxes/*/00_inbox/*.eml"
---

# Prompt: Analisi Email in Ingresso

## Input atteso
- Nome inbox (corrisponde a una cartella in `inboxes/`) — es. `myjob`
- Testo dell'email (già scaricata in `inboxes/[inbox]/00_inbox/`)
- UID e nome file `.eml`

## Fase -1 — Carica Configurazione Inbox

Prima di tutto, leggi:
1. `inboxes/[inbox]/inbox.config.md` → contesto default, aree, knowledge base da usare
2. `inboxes/[inbox]/TRIAGE_RULES.md` → regole di categorizzazione specifiche
3. Tutti i percorsi sono relativi a questa inbox da questo momento in poi

## Fase 0 — Pulizia

Prima di qualsiasi analisi:
1. Rimuovi la firma dell'email (tutto ciò che segue pattern tipo "Ing.", "Tel.", "Le informazioni contenute", disclaimer legali)
2. Se è un forward, separa il corpo del messaggio di Attilio dal thread embedded sottostante
3. Il thread embedded serve SOLO per contesto storico — NON costituisce prova che esista un TODO nel sistema

> ⚠️ REGOLA CRITICA: la presenza di un soggetto/thread nel corpo dell'email NON significa che quel thread sia tracciato nei nostri file. Devi VERIFICARE nei file reali.

---

## Fase 1 — Identificazione Mittente

1. Chi ha scritto l'email? (non chi ha inoltrato)
2. L'email arriva da `attilio.fiumano@gruppocolzani.it`?
   - SÌ → cerca istruzioni esplicite nel corpo: "Segna nella mia TODO", "Mia todolist", "Assegna a [NOME]", "Da mettere task", ecc.
   - Le istruzioni esplicite di Attilio hanno **priorità assoluta** su qualsiasi altra analisi
3. Consulta `_knowledge/INTERLOCUTORS.md` per il mittente reale
   - Trovato → annota ruolo, area, pattern tipici
   - Non trovato → annota "sconosciuto" e abbassa confidence_routing

---

## Fase 2 — Ricerca in Knowledge (OBBLIGATORIA, nell'ordine)

Esegui ogni step e **documenta nel log** cosa hai trovato o non trovato.

### Step A — ROUTING_RULES.md
- Leggi `inboxes/[inbox]/ROUTING_RULES.md`
- Esiste una regola che corrisponde a questo mittente/soggetto/dominio?
- Log: `routing_rules: cercato: SI, trovato: [risultato]`

### Step B — email_threads.md
- Leggi `inboxes/[inbox]/email_threads.md`
- Il soggetto o il thread-topic corrisponde a un thread già censito?
- Log: `email_threads: cercato: SI, trovato: [risultato]`

### Step C — File TODO dell'area pertinente
Dopo aver determinato l'area (da `inbox.config.md` + `TRIAGE_RULES.md`), cerca nei file TODO **fisici**:

Per area COLZANI, consulta in quest'ordine:
- `projects/myJob/COLZANI/TODO.md`
- `projects/myJob/COLZANI/TEAM/Fabio_TODO.md`
- `projects/myJob/COLZANI/TEAM/Alessandro_TODO.md`
- `projects/myJob/COLZANI/TEAM/README.md`
- `projects/myJob/COLZANI/CONSULENTI/README.md`

Per altre aree: adatta di conseguenza consultando TRIAGE_RULES.md.

Per ogni file: indica se trovato match e quale riga/task.
Log: `todo_files_consultati: [lista con SI/NO per ciascun file]`

> ⚠️ Se nessun TODO trovato nei file → `confidence_action` NON può superare 0.50

---

## Fase 3 — Determinazione Area e Azione

Basandoti su ciò che hai trovato (non su assunzioni):

1. **Area**: COLZANI / DIRETTI / GET_ME_DIGITAL / SINAPPS / EMAIL
2. **Tipo azione**:
   - `nuovo_task` — nessun TODO esistente trovato nei file
   - `update_task` — TODO trovato fisicamente nei file (indica file + riga)
   - `archivia_nota` — solo informativa, nessuna azione richiesta
   - `chiarimento` — ambigua, serve input di Attilio prima di procedere

---

## Fase 4 — Calcolo Confidence (SEPARATA)

### confidence_routing (0.0–1.0)
Quanto sono sicuro di aver identificato area/persona/progetto corretti?

| Condizione | Impatto |
|---|---|
| Istruzione esplicita di Attilio | +0.40 |
| Mittente trovato in INTERLOCUTORS.md | +0.20 |
| Dominio noto (es. @gruppocolzani.it) | +0.15 |
| Keyword progetto univoca (Shopify, GCAT, InPost…) | +0.15 |
| Mittente sconosciuto | -0.30 |
| Email ambigua o più aree plausibili | -0.20 |

### confidence_action (0.0–1.0)
Quanto sono sicuro del tipo di azione (nuovo vs update)?

| Condizione | Impatto |
|---|---|
| TODO trovato fisicamente nei file con match forte | +0.40 |
| Thread trovato in email_threads.md | +0.20 |
| Regola trovata in ROUTING_RULES.md | +0.20 |
| Nessun TODO trovato nei file | CAP A 0.50 (massimo assoluto) |
| Thread embedded nel corpo email (NON nei nostri file) | 0 (non conta) |

---

## Fase 5 — Output: Companion .md

Crea il file `inboxes/[inbox]/01_to-be-defined/[nome_eml_senza_estensione].md` compilando lo schema da `_system/companion_schema.md`.

Poi componi il messaggio per Attilio seguendo questo formato (da `_system/FLOW.md`, sezione "Formato Recap"):

```
📧 Email da [Mittente Nome] ([Contesto])
- Oggetto: [subject]
- Area/Società: [es. COLZANI - SPORTIT SRL]
- Cosa dice: [2-3 righe]
- Azione proposta ([routing X%] / [azione Y%]): [dettaglio con file/riga se update]
- 📎 [Leggi email originale] → [percorso .eml]
```

---

## Fase 6 — Aggiorna INDEX

Aggiungi una riga in `inboxes/[inbox]/01_to-be-defined/INDEX.md`:

```
| [data] | [uid] | [mittente_reale] | [subject] | [[nome_companion.md]] |
```
