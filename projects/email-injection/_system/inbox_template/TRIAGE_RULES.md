# TRIAGE RULES — [NOME_INBOX]

> File inbox-specifico. Contiene le regole di categorizzazione email per questa casella.
> Compilare con le regole specifiche del contesto di questa inbox.

---

## Priorità di Analisi

1. **Istruzioni esplicite del mittente prioritario** (vedi `inbox.config.md` → `priority_senders`)
2. **Mittente originale** (persona/entità che ha scritto, anche se forwarded)
3. **Dominio mittente** (vedi `domain_mappings` in `inbox.config.md`)
4. **Oggetto email** (pattern, keyword, riferimenti a thread in `email_threads.md`)
5. **Contenuto corpo** (keyword, progetti, nomi, ticket reference)

---

## Regola 1: Email dal Mittente Prioritario

**Condizione**: `From` corrisponde a un `priority_sender` in `inbox.config.md`

**Azioni**:
1. Cercare istruzioni esplicite nel corpo:
   - [DA_COMPILARE — pattern di istruzione tipici per questo mittente]
2. Se è un forward: estrarre mittente originale MA dare precedenza alle istruzioni del prioritario
3. Area di pertinenza: seguire istruzioni esplicite, altrimenti analizzare contenuto

---

## Regola 2: Mapping Domini

[DA_COMPILARE — lista domini e aree corrispondenti]

Esempio:
- `@example.com` → area EXAMPLE

---

## Regola 3: Keyword Progetto

[DA_COMPILARE — keyword specifiche per questa inbox e area/progetto corrispondente]

---

## Aree di Pertinenza

[DA_COMPILARE — lista aree con descrizione]

---

## Pattern Ticket / Riferimenti

[DA_COMPILARE — pattern ticket specifici per questa inbox, es. "OP#", "TICKET-", ecc.]
