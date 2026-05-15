# INBOXES REGISTRY

Registro di tutte le caselle email monitorate dal sistema.
Aggiornare quando si aggiunge o disattiva una inbox.

---

## Inbox Attive

| Nome | Email | Contesto Default | Cartella | Attiva |
|------|-------|-----------------|----------|--------|
| myjob | myjob@ingeniosolution.it | COLZANI | `inboxes/myjob/` | ✅ |

---

## Come Aggiungere una Nuova Inbox

1. Copia la cartella `_system/inbox_template/` in `inboxes/[nome]/`
2. Compila tutti i campi `[DA_COMPILARE]` in `inbox.config.md`
3. Personalizza `TRIAGE_RULES.md` con le regole specifiche del contesto
4. Aggiungi le credenziali IMAP in `.imap_credentials.env` con la chiave indicata
5. Aggiungi una riga a questa tabella con `Attiva: ✅`
6. Se l'inbox richiede un contesto completamente diverso (es. cliente esterno, casella personale), valuta se creare un `INTERLOCUTORS.md` inbox-specifico invece di usare quello condiviso

---

## Inbox Inattive / Archiviate

*(nessuna)*
