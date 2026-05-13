# myMoney - Copilot Instructions (Core)

Queste istruzioni sono solo il nucleo operativo sempre valido.
I dettagli estesi sono nelle docs linkate sotto.

- Usare per tutto il progetto modello **CLAUDE SONNET 4.6** a meno di specifiche diverse

## Fonti canoniche
- Runbook registrazioni: `docs/REGISTRAZIONE-RUNBOOK.md`
- Storico modifiche: `docs/CHANGELOG.md`
- Regole operative e allineamento PERSONALE→CASA: `memory/repo/registrazione-regole-critiche.md`
- Mappature vendor/categorie: `memory/repo/vendor-mapping.md`

## Auto-aggiornamento (obbligatorio)
Ogni volta che Atti insegna una regola nuova, una correzione o un mapping confermato durante una sessione su questo progetto, aggiornarla immediatamente in `miotesoro.md` o nel file di riferimento corretto (`docs/`, `memory/repo/`). Non aspettare fine sessione.

## Ambito progetto
- Il progetto gestisce due fogli Google Sheets distinti:
  - PERSONALE: `1LiZNaKhL2UO3UDoSBOrTeaGHD30JQdIB7_BShisB0vQ`
  - CASA: `10O6jkcSvsUH8sVls-pJ2SWUymk71U3y_NtjmHktHKyg`
- Prima di qualsiasi lettura/scrittura, identificare sempre il foglio target.
- Se ambiguo, chiedere conferma esplicita all'utente.

## Guardrail obbligatori (registrazioni)
1. **Revisione pre-registrazione obbligatoria**
   - Prima di append su `Movimenti`, delegare la revisione all'agente dedicato in `agents/revisore-registrazioni.agent.md`.
   - Nessuna registrazione senza esito revisione `APPROVED`.

2. **Controllo duplicati obbligatorio**
   - Verificare collisioni su `id operazione` (colonna F).
   - Verificare anche chiave funzionale `Data + Importo + Nota`.

3. **Validazione conti sul foglio corretto**
   - CASA va validato solo contro `CASA -> Conti!A:A`.
   - PERSONALE va validato solo contro `PERSONALE -> Conti!A:A`.
   - Vietato correggere conti CASA usando riferimenti PERSONALE.

4. **Integrità partita doppia**
   - Stesso `id operazione` su tutte le righe della stessa operazione.
   - Somma algebrica importi per `id operazione` uguale a zero.

5. **Formato importi e encoding**
   - Importi in formato italiano (virgola decimale).
   - Charset UTF-8 obbligatorio.
   - `Spese|Prima necessità|...` deve mantenere `à` (U+00E0).
   - Per campi data/ora di creazione e modifica usare sempre il timezone italiano `Europe/Rome`, non UTC.

6. **Post-append obbligatorio**
   - Dopo append su `Movimenti!A:J`, copiare formule dalla riga precedente:
     - PERSONALE: colonne K-W (`startColumnIndex=10`, `endColumnIndex=23`)
     - CASA: colonne K-S (`startColumnIndex=10`, `endColumnIndex=19`)
   - Verificare formula e lookup coerenti sulle nuove righe.

## Regole di conferma utente
- Se un conto non e' certo, proporre tabella con `Data | Importo | Descrizione | Conto proposto | Motivazione`.
- Registrare solo dopo conferma utente sui casi dubbi.

## Accesso API Google Sheets
- Usare API REST v4 con token OAuth2 dal percorso fisso: `.env` (relativo alla cartella `miotesoro/`)
- Non cercare token in variabili d'ambiente o percorsi home.
- Se 401: eseguire refresh token (vedi runbook sezione 5) e riprovare.

## Allineamento PERSONALE → CASA
Procedura completa in `memory/repo/registrazione-regole-critiche.md` (sezione "Allineamento PERSONALE → CASA").

Regole chiave:
- Solo righe con **Stato = Eseguito**
- Verifica per **id operazione** (colonna F)
- Conto patrimoniale di chiusura: solo `Versamento diretto` → `Portafoglio|Ptf|Webank`; tutti gli altri → voce dedotta dalla nota secondo piano dei conti CASA, di solito sono SPESE confronta con  + `memory/repo/vendor-mapping.md`
- **Chiedere sempre conferma prima di scrivere**
- Usare modello **OPUS 4.7**

## Manutenzione periodica doc (obbligatoria)
- Ogni blocco importante di registrazioni o import:
  1. Aggiornare `docs/CHANGELOG.md`.
  2. Aggiornare `memory/repo/vendor-mapping.md` solo con mapping confermati.
  3. Rimuovere regole duplicate/spostate in docs specialistiche.
  4. Verificare che `miotesoro.md` resti sintetico e senza dettagli ridondanti.
