# Documento Tecnico — miotesoro (myMoney)

## Stack

- **Modello AI:** Claude Sonnet 4.6
- **Dati:** Google Sheets v4 API (REST + OAuth2)
- **Token auth:** file `.env` nella cartella `miotesoro-sheet-agent/` (percorso relativo)
- **Fogli target:**
  - PERSONALE: `1LiZNaKhL2UO3UDoSBOrTeaGHD30JQdIB7_BShisB0vQ`
  - CASA: `10O6jkcSvsUH8sVls-pJ2SWUymk71U3y_NtjmHktHKyg`

## Architettura

```
miotesoro-sheet-agent.md              ← istruzioni core dell'agente (sempre caricato)
agents/
  revisore-registrazioni.agent.md  ← agente validazione pre-append
docs/
  CHANGELOG.md            ← storico dettagliato modifiche
  REGISTRAZIONE-RUNBOOK.md ← procedura completa di registrazione
  vendor-mapping.md        ← mappatura vendor → categoria
memory/repo/
  registrazione-regole-critiche.md ← regole di allineamento PERSONALE↔CASA
  vendor-mapping.md        ← copia operativa del mapping
```

## Varianti architetturali

- `mio-tesoro-file` → full privacy, file-based
- `mio-tesoro-paas` → full service
- `mio-tesoro-cloud` → cloud personale ibrido, con base dati ancora da scegliere
- `mio-tesoro-sheet` → Google Sheet come base unica, senza webapp HTML

## Flusso registrazione

1. Ricezione dati da Atti
2. Agente revisore verifica (duplicati, integrità partita doppia, conti validi)
3. Solo con esito `APPROVED` → append su `Movimenti!A:J`
4. Post-append: copia formule colonne K-W (PERSONALE) o K-S (CASA)

## Guardrail critici

- Importi in formato italiano (virgola decimale)
- Charset UTF-8, `à` = U+00E0
- Timezone Europe/Rome per tutti i timestamp
- `id operazione` univoco, somma algebrica = 0 per partita doppia
- Fogli CASA e PERSONALE non si mischiano mai
