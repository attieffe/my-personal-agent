# ROUTING.md — Regole di routing per TODO e operazioni myJob

> **ISTRUZIONI PER L'AI — LEGGERE PRIMA DI QUALSIASI OPERAZIONE SU TODO O FILE myJob**
>
> Questo file è la fonte di verità per il routing. Prima di aggiungere, modificare o spostare qualsiasi task/nota in myJob, consultare questo file e seguire le regole alla lettera. Se il contesto è ambiguo, CHIEDERE ad Atti prima di scrivere.

---

## REGOLA TODO PRIMARIA — TODO_GENERALE è obbligatorio

**SEMPRE**: Ogni task va inserito in `TODO_GENERALE.md` (fonte di verità unica)

**OPZIONALE**: Puoi duplicare/linkare in file specifici per organizzazione (`TODO_PERSONALE.md`, sezioni TODO/Backlog in `<AGENZIA>_INDEX.md`)

**Workflow corretto:**
1. Scrivi task in `TODO_GENERALE.md`
2. Se serve organizzazione dettagliata → duplica/linka in file specifico

---

## REGOLA ZERO — Prima di scrivere, dichiara

Prima di modificare qualsiasi file TODO, scrivi esplicitamente:
> "Inserisco in `<percorso/file>` — procedo?"

Solo se Atti conferma (o se il contesto è inequivocabile), procedere. In caso di dubbio minimo: FERMARSI e CHIEDERE.

---

## Mappa TODO per contesto

### Freelance e lavori da casa
- **TODO generali freelance / ingenio** → [[TODO_GENERALE]] (obbligatorio)
  - Copre: freelance (GMD, Sinapps, Newu, Studio Visual, diretti), Ingenio Solution
  - **Nota**: COLZANI è un workspace separato, non toccare qui
- **TODO cliente freelance specifico** (opzionale) → sezione `## TODO / Backlog` dentro `FREELANCE/<AGENZIA>/<AGENZIA>_INDEX.md`
  - Es: `FREELANCE/GET_ME_DIGITAL/GMD_INDEX.md` sezione TODO

Parole chiave: "gmd", "get me digital", "sinapps", "newu", "studio visual", "cliente diretto", "ingenio", "freelance"

### Personale / hobby / famiglia / casa
- **TODO personale Atti** (hobby, famiglia, casa, acquisti, padel, chitarra) → [[TODO_GENERALE]] (obbligatorio)
- **Organizzazione dettagliata** (opzionale) → [[PERSONALE/TODO_PERSONALE]]
- **TODO Attilio "nella mia lista"** → [[TODO_GENERALE]]

Parole chiave: "personale", "hobby", "padel", "famiglia", "casa", "acquisti", "chitarra", "mia todolist", "mia lista"

---

## Disambiguazione: "TODO" senza contesto

Se Atti dice solo "aggiungi ai TODO" senza specificare il contesto:

1. **SEMPRE** inserire in `TODO_GENERALE.md` (regola primaria)
2. Analizzare il contenuto del task: è chiaramente lavorativo? freelance? personale?
3. Se chiaro → routing automatico con dichiarazione preventiva (vedi REGOLA ZERO)
4. Se serve organizzazione specifica → chiedere: "Duplico anche in file specifico (TODO_PERSONALE / <AGENZIA>_INDEX)?"

**Mai indovinare in silenzio. Mai scrivere senza dichiarare il file target.**

---

## File da NON toccare per TODO normali

Questi file hanno nomi simili a TODO ma NON sono TODO operativi:

| File | Natura | Quando usarlo |
|------|--------|---------------|
| `_TEMPLATE/PROGETTO_TEMPLATE.md` | Template | Solo per creare nuovi progetti |
| `_TEMPLATE/CLIENTE_TEMPLATE.md` | Template | Solo per creare nuovi clienti |
| `_TEMPLATE/CLIENT_ROOT/` | Template struttura | Solo setup iniziale |
| `PERSONALE/README.md` | Indice navigazione | Non è una TODO list |

---

## Struttura myJob — orientamento rapido

```
projects/myJob/
├── ROUTING.md              ← QUESTO FILE (leggi sempre prima)
├── TODO_GENERALE.md        ← ⭐ TODO primario: TUTTI i task vanno qui
├── FREELANCE/
│   ├── GET_ME_DIGITAL/
│   │   └── GMD_INDEX.md           ← Sezione TODO/Backlog opzionale
│   ├── SINAPPS/
│   │   └── SINAPPS_INDEX.md       ← Sezione TODO/Backlog opzionale
│   ├── NEWU_SRL/
│   │   └── NEWU_INDEX.md          ← Sezione TODO/Backlog opzionale
│   ├── STUDIO_VISUAL/
│   │   └── STUDIO_VISUAL_INDEX.md ← Sezione TODO/Backlog opzionale
│   └── DIRETTI/
│       └── <cliente>/...
├── PERSONALE/
│   ├── TODO_PERSONALE.md   ← TODO personali (opzionale, organizzazione)
│   └── README.md           ← Indice navigazione (non è una TODO list)
├── INGENIO_SOLUTION/       ← Task Ingenio vanno in TODO_GENERALE.md
└── _TEMPLATE/              ← Solo template, MAI modificare per task reali
```

**Note:**
- `TODO_GENERALE.md` è l'unica fonte primaria obbligatoria
- File specifici (`TODO_PERSONALE`, `<AGENZIA>_INDEX`) sono opzionali per organizzazione
- COLZANI non esiste in questo workspace (workspace separato)

---

_Aggiornato: 2026-05-26_
