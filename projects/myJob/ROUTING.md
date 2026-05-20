# ROUTING.md — Regole di routing per TODO e operazioni myJob

> **ISTRUZIONI PER L'AI — LEGGERE PRIMA DI QUALSIASI OPERAZIONE SU TODO O FILE myJob**
>
> Questo file è la fonte di verità per il routing. Prima di aggiungere, modificare o spostare qualsiasi task/nota in myJob, consultare questo file e seguire le regole alla lettera. Se il contesto è ambiguo, CHIEDERE ad Atti prima di scrivere.

---

## REGOLA ZERO — Prima di scrivere, dichiara

Prima di modificare qualsiasi file TODO, scrivi esplicitamente:
> "Inserisco in `<percorso/file>` — procedo?"

Solo se Atti conferma (o se il contesto è inequivocabile), procedere. In caso di dubbio minimo: FERMARSI e CHIEDERE.

---

## Mappa TODO per contesto

### Freelance e lavori da casa
- **TODO generali freelance / ingenio / personale** → `projects/myJob/TODO_GENERALE.md`
  - Copre: freelance (GMD, Sinapps, Newu, diretti), Ingenio Solution, tutto tranne Colzani
- **TODO cliente freelance specifico** → `projects/myJob/FREELANCE/<AGENZIA_O_DIRETTI>/<CLIENTE>/README.md` sezione TODO/Backlog

Parole chiave: "gmd", "get me digital", "sinapps", "newu", "cliente diretto", "ingenio", "freelance"

### Personale / hobby / famiglia / casa
- **TODO personale Atti** (hobby, famiglia, casa, acquisti, padel, chitarra) → `projects/myJob/PERSONALE/01_todo_riassuntivo.md`
- **TODO Attilio "nella mia lista"** (quando Atti dice "metti nella mia todolist") → `projects/myJob/PERSONALE/01_todo_riassuntivo.md`

Parole chiave: "personale", "hobby", "padel", "famiglia", "casa", "acquisti", "chitarra", "mia todolist", "mia lista"

---

## Disambiguazione: "TODO" senza contesto

Se Atti dice solo "aggiungi ai TODO" senza specificare il contesto:

1. Analizzare il contenuto del task: è chiaramente lavorativo? freelance? personale?
2. Se chiaro → routing automatico con dichiarazione preventiva (vedi REGOLA ZERO)
3. Se ambiguo → CHIEDERE: "In quale area va questo task? Colzani / Freelance / Personale?"

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
| `COLZANI/TACCUINI/` | Note/log | Note, non task |

---

## Struttura myJob — orientamento rapido

```
projects/myJob/
├── ROUTING.md              ← QUESTO FILE (leggi sempre prima)
├── TODO_GENERALE.md        ← TODO Atti: freelance + ingenio + personale (NON Colzani)
├── FREELANCE/
│   ├── GET_ME_DIGITAL/README.md
│   ├── SINAPPS/README.md
│   ├── NEWU_SRL/README.md
│   └── DIRETTI/<cliente>/README.md
├── PERSONALE/
│   ├── 01_todo_riassuntivo.md  ← TODO personali Atti (hobby, famiglia, casa)
│   └── README.md               ← Indice navigazione (non è una TODO list)
└── _TEMPLATE/              ← Solo template, MAI modificare per task reali
```

---

_Aggiornato: 2026-05-16_
