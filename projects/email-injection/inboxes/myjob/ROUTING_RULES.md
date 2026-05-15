# ROUTING RULES — Regole Apprese dal Feedback

> **IMPORTANTE**: Questo file appartiene al layer `_knowledge/` ed è aggiornato automaticamente dal sistema tramite `process_outcome.prompt.md` quando una proposta viene classificata come NON ADEGUATA.
> Non modificare manualmente salvo correzioni esplicite di Attilio.

---

## Come leggere questo file

Ogni regola descrive un pattern di errore già incontrato e come comportarsi in futuro.
Il sistema deve consultare questo file **prima** di fare qualsiasi proposta (Step A di `analyze_email.prompt.md`).

---

## Regole

*(nessuna regola ancora — cold start)*

---

## Casi di Test

> Esempi noti da usare per validare che le regole funzionino correttamente.
> Aggiornare quando si aggiunge una nuova regola.

### Caso GLS — 2026-05-15
- **Email**: UID 9, subject "GESTIONE RESA BANCALI - GLS ITALIA - ORIDNARE TESTINA STAMPA"
- **Errore commesso**: proposto `update_task` con confidence 0.93 su un TODO inesistente
- **Causa**: il modello ha inferito l'esistenza del TODO dalla storia del thread embedded nel corpo email, senza verificare nei file reali
- **Comportamento corretto**: `nuovo_task` in `COLZANI/TEAM/Fabio_TODO.md` con confidence_action ≤ 0.50
- **Regola da applicare**: thread history nel corpo email ≠ TODO esistente nel sistema
