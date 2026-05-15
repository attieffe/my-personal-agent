# Regole Critiche Registrazione

Regole operative consolidate — non duplicare nel runbook, qui restano solo le critiche.

## Struttura fogli — ATTENZIONE ordine righe

- **CASA**: le righe più recenti sono in CIMA (righe con numero basso). NON cercare le ultime registrazioni in fondo al foglio — ordinare per data movimento per trovare le più recenti.
- **PERSONALE**: le righe vengono appese in fondo (ordine crescente per riga).
- Errore commesso il 12/05/2026: cercando le ultime righe per numero, si leggevano dati del 2024 anziché del 2026 presenti nelle prime righe di CASA.

## Regole anti-errore (da incidenti passati)

- **Verifica `updatedRange`**: dopo ogni append su Movimenti, leggere la response e verificare che `updatedRange` corrisponda alle righe attese. Il 15/04/2026 l'op001 è stata duplicata perché non si è verificato l'output.
- **No cross-foglio**: i conti CASA si validano SOLO contro `CASA → Conti!A:A`. Mai usare riferimenti PERSONALE per validare un'operazione CASA.
- **Refresh token prima di batch lunghi**: se si prevede una sessione lunga, eseguire refresh preventivo per evitare 401 a metà lavoro.
- **Encoding UTF-8 obbligatorio**: `Prima necessità` deve contenere `à` (U+00E0), non `Ã ` o altri artefatti. Verificare prima di ogni append.

## Conti creati in sessioni precedenti (non nel piano conti iniziale)

| Data | Conto | Foglio | Riga |
|------|-------|--------|------|
| 2026-04-14 | `Spese\|Mediche\|Visita medico agonistica` | PERSONALE | 214 |
| 2026-04-14 | `Spese\|Sport\|Padel tornei` | PERSONALE | 215 |
| 2026-04-14 | `Spese\|Sport\|Padel attrezzatura` | PERSONALE | 216 |
| 2026-04-14 | `Spese\|Sport\|Padel lezioni` | PERSONALE | 217 |
| 2026-04-15 | `Spese\|Auto\|Batteria` | PERSONALE | 218 |

## Allineamento PERSONALE → CASA (spese condivise)

### Regola generale
Ogni voce PERSONALE sui conti `Spese|Casa condivise|xxx` deve avere un corrispettivo nel foglio CASA.
La corrispondenza si verifica tramite **id operazione** (stesso ID su entrambi i fogli).

### Mapping conti

| PERSONALE (Spese) | CASA (Entrate, segno opposto) |
|-------------------|-------------------------------|
| `Spese\|Casa condivise\|Bonifico Conto Casa` | `Entrate\|Attilio\|Versamento diretto` |
| `Spese\|Casa condivise\|Contanti Conto Casa` | `Entrate\|Attilio\|Anticipo spese contanti` |
| `Spese\|Casa condivise\|Prelievi Conto Casa` | `Entrate\|Attilio\|Prelievo` |
| `Spese\|Casa condivise\|Conto Casa` | `Entrate\|Attilio\|Anticipo spese` |

### Struttura partita doppia in CASA

Per ogni voce PERSONALE `Spese|Casa condivise|X` con importo +N:
1. Riga 1 — `Entrate|Attilio|Y` | importo **-N** (segno opposto) | stessa nota | stesso id
2. Riga 2 — conto patrimoniale CASA | importo **+N** (stesso segno) | stessa nota | stesso id

**Regole conto di chiusura (riga 2):**
- `Versamento diretto` (bonifico) → `Portafoglio|Ptf|Webank`
- `Anticipo spese contanti` → `Entrate|Chiara|Prelievo` (Chiara ha usato contanti di Attilio)
- Importo negativo su `Versamento diretto` (es. rimborso/storno) → `Entrate|Chiara|Prelievo`
- `Anticipo spese` / `Prelievo` → voce **Spese** CASA dedotta da nota + `memory/repo/vendor-mapping.md` + piano conti CASA
- Interessi/spese bancarie → `Spese|Banche|Spese bancarie` (o interessi se esplicito)
- Ambiguo → segnalare e chiedere conferma Atti

### Scope temporale allineamento
**Default: ultimi 2 mesi** (aprile/maggio anno corrente). Voci più vecchie → sessione dedicata, non mescolare.

### Procedura "allinea spese condivise"

Quando Atti chiede di allineare le spese da PERSONALE a CASA:
1. Leggere voci PERSONALE su `Spese|Casa condivise|*` — **solo Stato = Eseguito**, **solo ultimi 2 mesi** (salvo indicazione diversa)
2. Leggere tutti gli ID già presenti in CASA su `Entrate|Attilio|*`
3. Trovare le voci PERSONALE il cui ID **non** esiste in CASA
4. Per ciascuna, dedurre il conto di chiusura secondo le regole sopra
5. **Presentare tabella riepilogativa ad Atti e attendere conferma esplicita** prima di scrivere qualsiasi riga
6. Solo dopo conferma: registrare con regole standard (revisore → insertDimension in cima → formule K-S)
7. **Usare il modello OPUS 4.7** per questa operazione
8. **Post-allineamento obbligatorio**: dopo aver scritto, cercare nel foglio CASA le righe recenti (per data creazione) su `Portafoglio|Ptf|Webank` che non hanno contropartita (ID non abbinato a nessun'altra riga). Proporre la contropartita con le regole standard; se ambigua, chiedere ad Atti.

### Errore del 12/05/2026 (da non ripetere)
- Inserite righe senza attendere conferma utente
- Usato `Portafoglio|Ptf|Webank` come chiusura per tutti i casi invece di decodificare le spese
- Incluse righe con Stato ≠ Eseguito

## Operazioni "Previsto" note (da aggiornare a Eseguito)

- Colzani/GRUPPO COLZANI SRL: spesso ha già righe Previsto — aggiornare stato + data, non reinserire.
