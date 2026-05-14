---
name: Revisione Governance Periodica
description: "Verifica coerenza tra copilot instructions, runbook, changelog e memory repo; riduce duplicazioni e mantiene la repository pulita."
agent: "agent"
tools: [read, search, edit]
argument-hint: "Ambito della revisione (es. registrazioni aprile, import Revolut CASA, ecc.)"
---

Esegui una revisione periodica della governance del repository per l'ambito indicato.

## Obiettivo
- Trovare incoerenze tra istruzioni, docs e memory.
- Ridurre overload e duplicazioni.
- Lasciare una struttura chiara: core + runbook + memoria operativa.

## Fonti da usare
- `miotesoro.md`
- `docs/REGISTRAZIONE-RUNBOOK.md`
- `docs/CHANGELOG.md`
- `memory/repo/vendor-mapping.md`
- `agents/revisore-registrazioni.agent.md`

## Regole di revisione
1. Conserva in `miotesoro.md` solo guardrail always-on.
2. Sposta i dettagli operativi nel runbook.
3. Mantieni in memory solo regole confermate e mapping consolidati.
4. Se modifichi procedure, aggiorna `docs/CHANGELOG.md`.
5. Verifica che la revisione pre-registrazione con agente dedicato resti obbligatoria.

## Output richiesto
Restituisci sempre:
1. Elenco incongruenze trovate (severita': alta/media/bassa)
2. Patch proposte/applicate
3. Checklist finale di allineamento
4. Rischi residui