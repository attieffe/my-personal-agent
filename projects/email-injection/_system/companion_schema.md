# Companion Schema — Email Analysis Record

Schema fisso per il file `.md` companion di ogni `.eml` in `01_to-be-defined/` e `90_archive/`.
Ogni campo è obbligatorio salvo indicazione contraria.

---

## Sezione: Identificazione

```
uid: <stringa, es. "9">
received_at: <ISO 8601, es. "2026-05-15T07:34:00Z">
eml_path: <percorso relativo al .eml, es. "01_to-be-defined/msg_9_20260515_073446.eml">
mittente_reale: <nome e email del mittente effettivo — se forward, il mittente originale, NON Attilio>
mittente_forwarder: <se applicabile, es. "Attilio Fiumanò <attilio.fiumano@gruppocolzani.it>">
subject: <soggetto email pulito>
istruzioni_attilio: <testo esplicito di Attilio se presente, altrimenti "nessuna">
```

---

## Sezione: Log di Ricerca

> Questa sezione documenta COSA è stato cercato e COSA è stato trovato.
> Non si inferisce — si riporta solo ciò che esiste nei file.
> La storia del thread nel corpo email NON vale come prova di TODO esistente.

```
routing_rules:
  cercato: SI
  trovato: <descrizione o "nessuna corrispondenza">

email_threads:
  cercato: SI
  trovato: <descrizione o "nessuna corrispondenza">

todo_files_consultati:
  - <percorso file 1>: <trovato: SI/NO — dettaglio>
  - <percorso file 2>: <trovato: SI/NO — dettaglio>

interlocutor:
  trovato: SI/NO
  dettaglio: <nome, ruolo, note da INTERLOCUTORS.md>
```

---

## Sezione: Proposta

```
area: <es. "COLZANI">
sotto_area: <es. "TEAM > Fabio" — opzionale>
tipo_azione: <"nuovo_task" | "update_task" | "archivia_nota" | "chiarimento">
target_file: <percorso file da creare/aggiornare>
testo_azione: |
  <descrizione testuale dell'azione proposta>
confidence_routing: <0.0–1.0 — quanto sono sicuro di area/persona/progetto>
confidence_action: <0.0–1.0 — quanto sono sicuro di nuovo_task vs update — MAX 0.50 se nessun TODO trovato nei file>
note_confidenza: <spiegazione breve dei valori scelti>
```

---

## Sezione: Outcome

> Compilata da process_outcome.prompt.md dopo la conferma di Attilio.

```
processed_at: <ISO 8601>
proposta_adeguata: <SI | NO>
decisione_confermata: <SI | NO>
azione_effettiva: |
  <descrizione di cosa è stato effettivamente fatto>
motivazione_scarto: <se proposta_adeguata = NO — testo libero spiegazione>
regola_aggiornata: <SI | NO — se ROUTING_RULES.md è stato aggiornato>
```
