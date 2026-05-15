---
description: Gestisce la conferma/rettifica di una proposta, archivia l'email e aggiorna il feedback loop.
applyTo: "projects/email-injection/inboxes/*/01_to-be-defined/*.md"
---

# Prompt: Process Outcome — Conferma e Archiviazione

## Input atteso
- Nome inbox (es. `myjob`)
- File companion `.md` presente in `inboxes/[inbox]/01_to-be-defined/`
- Decisione di Attilio (conferma o rettifica dell'azione proposta)

---

## Fase 1 — Acquisisci la Decisione

Chiedi ad Attilio (se non già esplicito):

> "Confermo l'azione proposta" oppure descrive un'azione diversa?

Determina:
- **azione_effettiva**: cosa si fa concretamente (può coincidere con la proposta o essere diversa)

---

## Fase 2 — Esegui l'Azione

Esegui l'azione confermata:
- `nuovo_task` → aggiungi task nel file indicato (`target_file` del companion)
- `update_task` → aggiorna il task esistente con le informazioni nuove + aggiungi riferimento al `.eml` archiviato
- `archivia_nota` → nessuna modifica ai TODO, solo archiviazione
- `chiarimento` → non eseguire finché non hai risposta

In ogni task creato/aggiornato, aggiungi al termine:
```
· ref: `EMAIL/90_archive/[nome_eml].eml`
```

---

## Fase 3 — Classifica l'Outcome

Confronta la proposta originale con la decisione effettiva e determina:

### PROPOSTA ADEGUATA
- **SÌ**: l'azione proposta era quella giusta (anche se Attilio ha scelto diversamente per motivi suoi)
- **NO**: l'azione proposta era sbagliata (area errata, tipo azione errata, TODO inesistente, ecc.)

### DECISIONE CONFERMATA
- **SÌ**: Attilio ha confermato esattamente la proposta
- **NO**: Attilio ha scelto un'azione diversa

### Combinazioni e conseguenze

| Proposta Adeguata | Decisione Confermata | Significato | Azione |
|---|---|---|---|
| SÌ | SÌ | Tutto corretto | Solo archivia |
| SÌ | NO | Proposta buona, scelta diversa | Archivia + nota |
| NO | NO | Proposta sbagliata | Archivia + chiedi motivazione + aggiorna ROUTING_RULES |

> ⚠️ La combinazione NO + SÌ non è possibile logicamente.

---

## Fase 4 — Se PROPOSTA NON ADEGUATA

Chiedi ad Attilio:

> "Cosa era sbagliato nella proposta? (es. area errata, match TODO inesistente, tipo azione errata, altro)"

Usa la motivazione per aggiornare `inboxes/[inbox]/ROUTING_RULES.md` aggiungendo una nuova regola nella sezione appropriata. Formato regola:

```markdown
### Regola [N] — [titolo breve]
- **Trigger**: [condizione che ha generato l'errore]
- **Comportamento errato**: [cosa aveva proposto il sistema]
- **Comportamento corretto**: [cosa si doveva fare]
- **Aggiunta il**: [data]
- **Caso originale**: [soggetto/mittente dell'email che ha generato l'errore]
```

---

## Fase 5 — Archiviazione

1. Sposta il file `.eml` da `inboxes/[inbox]/01_to-be-defined/` a `inboxes/[inbox]/90_archive/`
2. Aggiorna il companion `.md` compilando la **Sezione: Outcome** (schema in `_system/companion_schema.md`)
3. Sposta il companion `.md` da `inboxes/[inbox]/01_to-be-defined/` a `inboxes/[inbox]/90_archive/`
4. Rimuovi la riga corrispondente da `inboxes/[inbox]/01_to-be-defined/INDEX.md`

---

## Fase 6 — Aggiorna email_threads.md (se nuovo thread)

Se l'email introduce un thread NON ancora presente in `inboxes/[inbox]/email_threads.md`, aggiungi:

```markdown
- **[AREA] UID [N]** — "[subject]"
  - **Da**: [mittente reale]
  - **Assegnazione**: [persona o area]
  - **File**: `90_archive/[nome_eml].eml`
```
