# CHANGELOG

## 2026-05-13

### Aggiornamento vendor mapping e timezone operativo
- Aggiornato `memory/repo/vendor-mapping.md` e copia `docs/vendor-mapping.md` con mapping confermati da Atti: Acqua & Sapone, Osteria Del Gelato, Alperia, OVS, Corsico Hfb, Pepco Cantù, Shopsi Srl, Max Factory, D115 Carugo.
- Aggiunta regola operativa: campi data/ora creazione e modifica sempre in timezone `Europe/Rome`, non UTC.
- Aggiornate sul foglio CASA le contropartite rimaste vuote in `Movimenti`: righe 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53, 55, 57, 59, 61, 63, 65, 67, 69, 71, 75, 77. Conti validati su `CASA -> Conti!A:A`; data modifica impostata in timezone italiano. Riga 73 (Tri Malnatt) lasciata vuota perché non confermata.

## 2026-05-12

### Registrazione Entrate|Chiara|Anticipo spese — 26/04 → 12/05/2026 (CASA)
- **16 righe inserite** in Movimenti (righe 2-17), 8 operazioni in partita doppia:
  - 26/04: -€20 giostre → `Spese|Svago|Parchi giochi` (id `efqa2x`)
  - 05/05: -€340 asilo entrambi figli maggio → `Spese|Istruzione|Asilo` (id `zx7wi5`)
  - 05/05: -€340 centro estivo entrambi figli → `Spese|Istruzione|Centro Estivo` (id `vidxdr`)
  - 05/05: -€44 centro estivo (20+2)x2 bambini → `Spese|Istruzione|Centro Estivo` (id `n87qay`)
  - 05/05: -€60 gita Alessandro → `Spese|Istruzione|Gita` (id `b4roi0`)
  - 12/05: -€7 regali scuola → `Spese|Svago|Regali` (id `bn1k6m`)
  - 12/05: -€10 parrucchiere Alessandro (Taiziano) → `Spese|Cura persona|Parrucchiere` (id `xito4c`)
  - 12/05: -€5 salvadanaio bimbi regali → `Spese|Svago|Regali` (id `l1cxve`)
- 5 voci già presenti saltate (duplicate da mar-apr 2026)
- Formule K-S copiate via CopyPasteRequest batchUpdate
- Righe inserite in cima (prepend) — CASA è ordinata newest-first

## 2026-05-07

### Registrazione movimenti Contanti e PTF Amazon — 17/04 → 05/05/2026 (PERSONALE)
- **24 righe inserite** in Movimenti (righe 182-205), 12 operazioni in partita doppia:
  - 17/04: +350 Silvia Migliaccio → `Entrate|Attività|Privati vari` / `Portafoglio|PTF|Contanti` (id `209c47`)
  - 17/04: -50 calzolaio → `Spese|Cura persona|Abbigliamento` / `Portafoglio|PTF|Contanti` (id `72d5bc`)
  - 21/04: +350 Davide Rizzi → `Entrate|Attività|Rizzi` / `Portafoglio|PTF|Contanti` (id `d0818b`)
  - 24/04: -125 dati a Chiara (foto pantaloni) → `Spese|Casa condivise|Contanti Conto Casa` / `Portafoglio|PTF|Contanti` (id `9e3959`)
  - 25/04: -10 giostre → `Spese|Casa condivise|Conto Casa` / `Portafoglio|PTF|Contanti` (id `3c0015`)
  - 27/04: -5 ascensore S. Valeria → `Spese|Casa condivise|Conto Casa` / `Portafoglio|PTF|Contanti` (id `7f5eee`)
  - 01/05: -15 ingresso fiera erba → `Spese|Casa condivise|Conto Casa` / `Portafoglio|PTF|Contanti` (id `5949d0`)
  - 05/05: +150 Condello → `Entrate|Attività|Condello` / `Portafoglio|PTF|Contanti` (id `ec3a64`)
  - 05/05: +30 d4v3 VT → `Entrate|Vt|Vt` / `Portafoglio|PTF|Contanti` (id `5e5f15`)
  - 05/05: +120 g1g1 VT → `Entrate|Vt|Vt` / `Portafoglio|PTF|Contanti` (id `757f86`)
  - 28/04: +30 4nt0 VT → `Entrate|Vt|Vt` / `Portafoglio|Ptf|Amazon` (id `c9c5f1`)
  - 28/04: +30 c0rr4 VT → `Entrate|Vt|Vt` / `Portafoglio|Ptf|Amazon` (id `31e16f`)
- Formule K-W copiate via CopyPasteRequest batchUpdate
- **Saldo Contanti risultante**: 185 + 795 = **980€**
- **PTF Amazon**: +60€ (30+30)

## 2026-05-04

### Modifica rate previste — Condominio Straordinario facciate (PERSONALE)
- **Eliminate** rate Previsto giugno (id `3l0ex9`, 01/06/2026, € 1.000,00) e luglio (id `3l0exd`, 01/07/2026, € 1.000,00)
- **Inserite** 3 nuove rate da `Portafoglio|Ptf|Revolut` (righe 129-134):
  - R8: 01/07/2026 | € 740,03 | id `3l0exh`
  - R9: 01/08/2026 | € 790,00 | id `3l0exl`
  - R10: 01/09/2026 | € 790,00 | id `3l0exp`
- Formule K-W copiate via CopyPasteRequest batchUpdate
- Rata maggio (id `3l0ex5`, € 1.000,00) lasciata invariata

### Registrazione singola — vendita racchetta Metalbone a Paolo
- **1 operazione registrata** in Movimenti (righe 144-145, id `5rwkw4`):
  - Previsto | 10/05/2026 | `Entrate|Vendita|Usato` | -150 | vendita racchetta metalbone a Paolo
  - Previsto | 10/05/2026 | `Portafoglio|Ptf|Paypal` | +150 | vendita racchetta metalbone a Paolo
- Formule K-W copiate via CopyPasteRequest batchUpdate
- **Aggiornato CLAUDE.md e copilot-instructions.md**: aggiunta regola di sincronizzazione obbligatoria tra i due file

## 2026-04-18

### Governance istruzioni: ottimizzazione, coerenza e riduzione overload
- **Snellito `.github/copilot-instructions.md`** in versione core:
  - rimosso contenuto enciclopedico duplicato
  - mantenuti solo guardrail obbligatori, riferimenti canonici e manutenzione periodica
  - resa esplicita la regola: nessuna registrazione senza revisione pre-registrazione `APPROVED`
- **Creato runbook operativo**: `docs/REGISTRAZIONE-RUNBOOK.md`
  - raccolto il flusso completo di registrazione
  - checklist obbligatoria pre-append
  - sezione post-append e quality gate periodico per mantenere pulita la repository
- **Creato custom agent dedicato**: `.github/agents/revisore-registrazioni.agent.md`
  - ruolo ristretto a revisione tecnica pre-registrazione
  - output standardizzato `APPROVED|REJECTED` con check granulari
  - impostato in sola lettura (`tools: [read, search]`) per evitare scritture involontarie
- **Creato prompt operativo periodico**: `.github/prompts/revisione-governance-periodica.prompt.md`
  - rende ripetibile la manutenzione di coerenza
  - impone output strutturato (incongruenze, patch, checklist, rischi residui)

### Direzione architetturale documentazione
- Separazione netta:
  - `copilot-instructions.md` = regole always-on e guardrail critici
  - `docs/REGISTRAZIONE-RUNBOOK.md` = procedura dettagliata
  - `/memories/repo/*` = memoria operativa e mapping confermati
- Obiettivo: ridurre conflitti tra fonti e migliorare manutenzione periodica.

## 2026-04-17

### Ristrutturazione doc: supporto doppio foglio PERSONALE + CASA
- **Aggiunto foglio CASA** (`10O6jkcSvsUH8sVls-pJ2SWUymk71U3y_NtjmHktHKyg`) alla documentazione
- **Ristrutturato copilot-instructions.md**:
  - Panoramica progetto ora specifica entrambi i fogli
  - Sezione "Fogli target" con ID e URL per PERSONALE e CASA
  - Struttura fogli separata per PERSONALE e CASA
  - Schema Movimenti con tabella comparativa colonne formula (PERSONALE K-W vs CASA K-S)
  - Parametri CopyPaste differenziati (endColumnIndex 23 vs 19)
  - Piano dei conti separato con schema PERSONALE e CASA
  - Documentato il piano conti completo CASA (174 righe, incluse righe per-bambino Alessandro/Alice)
  - API lettura/scrittura aggiornati con commenti per scegliere spreadsheetId
- **Differenze CASA vs PERSONALE**:
  - CASA Movimenti: solo col K-S (mancano T Tipo conto, U Conto P, V Conto E, W Altro conto)
  - CASA Conti: col F = "conversione" (mapping al PERSONALE) invece di "Tipo conto" (P/E)
  - CASA Conti: righe per-bambino con id vuoto e nome in col C
  - CASA Utility: data corrente in B16 (PERSONALE: B17), metà mese in B17
- **Aggiornata memoria repo**: rimosso `mymoney-schema.md` obsoleto (referenziava foglio test), creato `mymoney-project.md` con note operative aggiornate

## 2026-04-15

### Import Ingenio Revolut (13 operazioni mar-apr 2026)
- **Cambio foglio target**: da test (`1CgZJyrB6aGCs-...`) a PRODUZIONE (`1LiZNaKhL2UO3UDoSBOrTeaGHD30JQdIB7_BShisB0vQ`)
  - Aggiornato spreadsheetId in copilot-instructions.md
- **Nuove istruzioni workflow** aggiunte in copilot-instructions.md:
  - Decodifica conti mancanti da storico + mapping vendor
  - Aggiornamento memoria vendor mapping
  - Richiesta conferma all'utente per conti dubbi
- **Nuovo conto creato**: `Spese|Auto|Batteria` (Variabile, E) in Conti riga 218
- **Colzani Previsto→Eseguito**: aggiornate 3 righe (id `2026.58272379`) da Previsto a Eseguito con data 09/04/2026 (righe 171, 178, 179)
- **Fix Amazon Prime gennaio**: riga 4560 corretta da `Spese|Prima necessità|Spesa` a `Spese|Svago|Amazon Prime`
- **26 righe registrate** in Movimenti (righe 4820-4845):
  - 13 operazioni (14 dall'utente, esclusa Colzani già come Previsto)
  - Periodo: 13/03/2026 - 10/04/2026
  - Vendor: Boom Di Veggian Sarae (×3), Pv1241 (×2), Muscatello, Coldi Oil, Amazon Music, Balza Multiservice, Biemme Motorit, Amazon Prime, Commissione Revolut, Pepe 68
  - Conti: Pasto, Benzina(×4), Bonifico Conto Casa, Conto Casa(×2), Batteria, Tagliando, Amazon Prime, Canone conto
- **Fix encoding UTF-8**: risolto problema con carattere `à` in "Prima necessità" (PowerShell non inviava correttamente senza UTF-8 file)
- **Vendor mapping creato**: file `/memories/repo/vendor-mapping.md` per Ingenio Revolut

## 2026-04-14

### Bulk import Revolut transactions
- **Nuovi conti creati** (Conti righe 214-217):
  - `Spese|Mediche|Visita medico agonistica` (Variabile, E)
  - `Spese|Sport|Padel tornei` (Variabile, E)
  - `Spese|Sport|Padel attrezzatura` (Variabile, E)
  - `Spese|Sport|Padel lezioni` (Variabile, E)
- **78 righe registrate** in Movimenti (righe 4822-4899)
  - Periodo: 17/03/2026 - 14/04/2026
  - 39 operazioni in partita doppia (tutte bilanciate a zero)
  - Vendor: Playtomic, Cob Centro Medico, Mody's Ssd, Sp Sportit, Condominio Mazzini, Pizzeria Kebap, Maximo Padel Cup, Google One, L'Art du Pain, VINCI Autoroutes, Carrefour, Attilio Fiumanò, Service.pay4ve, Cafe Velo
  - Include 3 rimborsi Playtomic (056, 048, 027)
  - Include 6 giroconti P-P (Revolut→Isybank, Revolut→Prestito Personale)
- **Formule K-W copiate** via CopyPasteRequest batchUpdate
- **Documentazione aggiornata**: tabella mappature Vendor→Conto Revolut aggiunta a copilot-instructions.md

### Sessione precedente (stesso giorno)
- Registrata entrata 120€ Vt (righe 4820-4821, id=zifoou)
- Scoperto e documentato metodo CopyPasteRequest per copia formule K-W dopo append
- Aggiornata checklist in copilot-instructions.md con procedura formula copy
