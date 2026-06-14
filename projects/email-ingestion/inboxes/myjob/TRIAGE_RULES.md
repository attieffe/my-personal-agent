# TRIAGE RULES — Regole di Categorizzazione Email

Regole per la categorizzazione automatica delle email in arrivo su `myjob@ingeniosolution.it`.

**Tipo**: Configurazione statica (modifiche manuali)

---

## Priorità di Analisi

L'analisi di un'email segue questa priorità (dal più importante al meno):

1. **Istruzioni esplicite di Attilio** (se mittente è `attilio.fiumano@gruppocolzani.it`)
2. **Mittente originale** (persona/entità che ha scritto l'email, anche se forwarded)
3. **Dominio mittente** (organizzazione di provenienza)
4. **Oggetto email** (pattern, keyword, riferimenti a thread esistenti)
5. **Contenuto corpo** (keyword, progetti, nomi, ticket reference)

---

## Regola 1: Email da Attilio Fiumanò

**Condizione**: `From: attilio.fiumano@gruppocolzani.it`

**Azioni**:
1. **Prima di tutto**: cercare istruzioni esplicite nel corpo email
   - "Segna nella mia TODO" → task per Attilio
   - "Mia todolist" → task per Attilio
   - "da discutere con [NOME]" → task con flag escalation
   - "(Assegna|Assegnato) a [NOME]" → task per quella persona specifica
   
2. **Se è un forward** (subject inizia con "I:" o "R:" o "Fwd:"):
   - Estrarre mittente originale dall'email inoltrata
   - **MA**: dare comunque priorità alle istruzioni di Attilio
   
3. **Area di pertinenza**:
   - Se istruzioni esplicite → seguire quelle
   - Altrimenti: analizzare contenuto/mittente originale per determinare area

**Output**:
- Flag `from_attilio: true`
- Campo `attilio_instructions: {action, target_person, escalation_to, notes}`
- Mittente originale se forwarded: `original_sender`

---

## Regola 2: Mapping Domini → Aree

### Domini Gruppo Colzani
**Dominio**: `@gruppocolzani.it`

**Area base**: `COLZANI`

**Raffinamento necessario**:
- Cross-reference con GLOSSARIO.md per identificare società specifica
- Analizzare oggetto/contenuto per keyword società (SPORTIT, COLZANI SRL, BRICOSPORT, ecc.)
- Verificare mittente in INTERLOCUTORS.md per contesto

**Sotto-aree possibili**:
- `COLZANI/TEAM` → comunicazioni team interno (Alessandro, Fabio)
- `COLZANI/CONSULENTI` → consulenti esterni (Marco Di Stefano AS400)
- `COLZANI/AS400` → topic AS400 specifico

### Domini Clienti Diretti
**Domini da catalogare**:
- (verranno aggiunti quando emergono pattern ricorrenti)

**Area**: `DIRETTI/[nome_cliente]`

**Processo**:
- Verificare se cliente già esiste in `projects/myJob/DIRETTI/`
- Se nuovo: proporre creazione cartella da `_TEMPLATE/CLIENTE_TEMPLATE.md`

### Domini Partner/Fornitori
**Esempi**:
- Lotrek → `COLZANI` (SPORTIT partner)
- Capgemini → `COLZANI` (fornitore software)

**Area**: Dipende dal contesto del cliente interno

---

## Regola 3: Pattern Oggetto Email

### Thread Esistenti
**Processo**:
1. Estrarre subject pulito (rimuovere "Re:", "I:", "Fwd:", numeri trailing)
2. Cercare in `email_threads.md` se oggetto già presente
3. Se match trovato → proporre **aggiornamento thread esistente** invece di nuovo task

### Ticket Reference
**Pattern**: `OP#` seguito da numero (es. "OP# 02698455")

**Azione**:
- Identificare come ticket Capgemini
- Cercare nei TODO se ticket già menzionato
- Se presente → proporre aggiornamento
- Se nuovo → creare task con reference al ticket

### Keyword Progetti
**Mapping keyword → progetti**:
- "GCAT" + ("ecommerce"|"Ecommerce") → COLZANI SRL, progetto GCAT Ecommerce
- "InPost" → SPORTIT SRL, integrazione InPost (task Alessandro)
- "Shopify" → SPORTIT SRL (verificare se task esistente)
- "AS400" → COLZANI/AS400, consulente Marco Di Stefano
- "fattura" + "elettronica" → SPORTIT (task Alessandro fatturazione elettronica)
- "dashboard" + "carichi" → COLZANI SRL, progetto con Marco Colzani

---

## Regola 4: Analisi Contenuto

### Nomi Persone
Se nel corpo email compare nome di persona catalogata in INTERLOCUTORS.md:
- Identificare relazione (assegnazione task, menzione, richiesta parere)
- Proporre categorizzazione basata su ruolo della persona

### Keyword Tecniche
**Tecnologie/Sistemi**:
- "AS400" → area AS400, consulente Marco Di Stefano
- "Shopify" → SPORTIT, team Alessandro/Fabio
- "feed", "Lotrek" → SPORTIT, Alessandro
- "NAV-Ls", "Dynamics NAV" → sistema gestionale, verificare contesto
- "API", "integrazione" → task tecnico, probabile Alessandro

**Processi Business**:
- "carico", "magazzino", "giacenza" → COLZANI SRL, dashboard carichi
- "ordini", "evadere" → e-commerce, SPORTIT
- "fattura", "fatturazione" → amministrativo, verificare società
- "canone", "licenza" → Capgemini o altri fornitori

---

## Regola 5: Categorizzazione Default

**Se nessun pattern match trovato**:

**Area**: `EMAIL/generale`

**Azione**:
- NON forzare categorizzazione errata
- Proporre ad Attilio di specificare:
  - Area corretta
  - Azione richiesta
  - Eventuale creazione nuova categoria

**Output**:
- Flag `needs_clarification: true`
- Campo `ambiguity_reason: "spiegazione del perché non si è riusciti a categorizzare"`

---

## Regola 6: Matching TODO Esistenti

**Prima di proporre nuovo task**:
1. Analizzare area identificata
2. Cercare nei file TODO dell'area (es. `COLZANI/TEAM/*.md`, `COLZANI/TEAM/README.md`)
3. Matching basato su:
   - Keyword progetto (es. "InPost", "GCAT", "Tyre24")
   - Ticket reference (es. "OP# 02698455")
   - Nome persona assegnata
   - Società/brand menzionato
4. **Confidence score**:
   - `> 70%` → proporre aggiornamento task esistente
   - `< 70%` → proporre sia nuovo task che possibili match, richiedere conferma

---

## Regola 7: Gestione Ambiguità

### Forward Multipli (catena >2 hop)
**Condizione**: Email è stata inoltrata più di 2 volte

**Azione**:
- Segnalare complessità
- Dare priorità a istruzioni di Attilio
- Estrarre mittente originale solo se rilevante per matching
- Richiedere conferma su quale mittente considerare primario

### Topic Drift (thread che cambia argomento)
**Condizione**: Subject uguale ma keyword contenuto molto diverse da email precedenti del thread

**Azione**:
- Flag `possible_topic_drift: true`
- Proporre ad Attilio:
  - Continuare thread esistente
  - Splittare in nuovo thread/task

### Società/Progetto Non Riconosciuto
**Condizione**: Menzionata società/brand/progetto non presente in GLOSSARIO.md

**Azione**:
- Flag `unknown_entity: true`
- Proporre aggiunta a GLOSSARIO.md con richiesta conferma + dettagli
- Non bloccare triage, procedere con best-effort categorizzazione

---

## Regola 8: Output Standardizzato

Ogni email analizzata deve produrre JSON con questa struttura:

```json
{
  "uid": "123",
  "from": "attilio.fiumano@gruppocolzani.it",
  "from_attilio": true,
  "original_sender": "partner@example.com",
  "subject": "I: GCAT Ecommerce",
  "subject_clean": "GCAT Ecommerce",
  "date": "2026-05-13T15:10:15Z",
  "attilio_instructions": {
    "action": "add_to_my_todo",
    "target_person": "Attilio",
    "notes": "da discutere con Stefano Colzani"
  },
  "area": "COLZANI",
  "society": "COLZANI SRL",
  "matched_todos": [
    {
      "file": "COLZANI/TEAM/README.md",
      "line": 42,
      "todo_text": "COLZANI SRL: integrazione GCAT Ecommerce [da fare]",
      "confidence": 0.95
    }
  ],
  "proposed_action": {
    "type": "update_existing_todo",
    "target_file": "COLZANI/TEAM/README.md",
    "details": "Aggiornare task esistente GCAT Ecommerce con nuove informazioni da email",
    "requires_escalation": true,
    "escalation_to": "Stefano Colzani"
  },
  "flags": {
    "needs_clarification": false,
    "possible_topic_drift": false,
    "unknown_entity": false,
    "forwarding_chain_long": false
  },
  "preview": "Breve preview contenuto...",
  "eml_file": "00_inbox/msg_3_20260513_151152.eml"
}
```

---

## Manutenzione

Queste regole sono **statiche** e vanno modificate manualmente quando:
- Si identificano nuovi pattern ricorrenti
- Si aggiungono nuovi clienti/partner con pattern specifici
- Si rilevano errori di categorizzazione sistematici

Per modifiche: editare questo file e aggiornare CHANGELOG.md

**Ultima modifica**: 2026-05-14 (inizializzazione)
