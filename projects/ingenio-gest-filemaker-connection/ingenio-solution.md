# Ingenio Solution

> **Nota identità**: `Attilio Fiumanò` == Ralf (l'utente). `attilio.fiumano@ingeniosolution.it` è la sua mailbox aziendale, `ralf00@gmail.com` è quella personale. Quando i workflow parlano di "inviare ad Attilio" significa "inviare alla mailbox aziendale dell'utente", così Ralf trova l'email pronta da inoltrare al cliente preservando "Attilio Fiumanò" come mittente.

## Identità azienda

- **Ragione sociale**: Ingenio Solution S.a.s. di Fiumanò Attilio
- **P.IVA / Cod. Fis.**: 08971020964
- **Sede**: via Pacini 77 — 20831 Seregno (MB)
- **Telefono**: +39 0362 1636590
- **Email**: info@ingeniosolution.it
- **Banca d'appoggio**: Banco BPM
- **IBAN**: IT93O0503433842000000003795
- **BIC/SWIFT**: BPMIITMMXXX
- **ABI / CAB**: 05034 / 33842

L'azienda è di proprietà di Ralf. Vende hardware/servizi (postazioni PC, accessori, sviluppo) e gestisce il ciclo attivo con un ERP custom FileMaker (DADEGEST).

---

## ERP — FileMaker DADEGEST

Documentazione completa: [knowledge/tools/filemaker.md](../../tools/filemaker.md).

Riassunto rapido:
- Host: `https://localhost/fmi/data/v2` (FM Server 19.3, certificato self-signed → bypass TLS)
- Master file: `DADEGEST` — contiene i layout
- File dati: `anagrafiche` (Clienti, Fornitori, Prodotti, **Iva**, **Pagamenti Preventivo**, ecc.), `Preventivi`, `fatture`, `DDT`, `righe vendita`, `Parametri` (anagrafica azienda + logo + banca), `Fatture acq`
- Credenziali: `.env` (FM_USER, FM_PASSWORD)

---

## Strumenti disponibili

### Generatore PDF preventivo
**Path**: [templates/preventivo/](../../../templates/preventivo/) · **Doc**: [README](../../../templates/preventivo/README.md) · **Piano**: [docs/plans/preventivo-pdf-template.md](../../../docs/plans/preventivo-pdf-template.md)

CLI: `npm run preventivo -- [opzioni]`

| Comando | Cosa fa |
|---|---|
| `--nr <N> [--anno <YYYY>]` | Trova per numero (anno corrente di default, fallback anno precedente) |
| `--cliente "Rossi" --ultimo` | Ultimo preventivo di un cliente |
| `--cliente "Rossi" --argomento "PC"` | Ultimo preventivo del cliente con `<testo>` nelle note |
| `--record-id <ID>` | recordId interno FileMaker |
| `--iva-inclusa` | Riga mostra "Totale (IVA incl.)" invece di Imponibile |
| `--html-only` | Solo HTML, no PDF |
| `--keep-html` | Conserva HTML accanto al PDF (per debug visivo) |

Output di default: `output/preventivi/<anno>/PRE-<nr>-<anno>-<slug-cliente>.pdf`.
PDF generato con Edge headless (`--print-to-pdf`), zero dipendenze npm.

Rispetta i flag testata FM: `STAMPA TOTALE`, `STAMPA FIRMA PER ACCETTAZIONE`, `Stampa SENZA QTA`, `Stampa SENZA PARZIALI`, `STAMPA SALTO PAGINA CON REQIUSITI`.

---

## Convenzioni operative

- Per "il preventivo", "il cliente", "la fattura" senza altri contesti → riferimenti all'ERP DADEGEST
- Per "noi" o "la mia società" → Ingenio Solution
- Tutti i preventivi che genero in PDF vanno loggati in [logs/YYYY-MM.md](../../../logs/)
- Mai modificare il record FM dal generatore PDF — è solo lettura

---

## Workflow "preventivo Ingenio + email" (modalità operativa)

Quando Ralf chiede "preventivo X di Ingenio" (o equivalenti), il flusso completo è:

1. **Generare PDF**: `npm run preventivo -- --nr X` (o resolver appropriato). Verificare a video.
2. **Recuperare email cliente**: dal record `V_PRE_000` per il preventivo: campo `Clienti::Email 1` (relazione). Se vuoto: `Clienti::Email 2`. Se entrambi vuoti: marcare placeholder e segnalare a Ralf.
3. **Determinare oggetto email**: campo `V_PRE_000.oggetto email` (se popolato). Se vuoto: improvviso un oggetto coerente con la nota documento (es. "Preventivo per fornitura PC") e lo segnalo come generato da me.
4. **Comporre testo email**:
   - **Destinatario**: `attilio.fiumano@ingeniosolution.it` — è la mailbox aziendale di Ralf stesso (Attilio Fiumanò == Ralf). L'email arriva a lui, che poi la inoltra al cliente da quella stessa mailbox
   - **Oggetto email Gmail**: stesso del punto 3
   - **Allegato**: il PDF generato in `output/preventivi/<anno>/`
   - **Prima riga del corpo**: l'email reale del cliente (per copia rapida da parte di Ralf), formato `→ Email cliente: nome@dominio.it`. Se assente: `→ Email cliente: [non presente in anagrafica — inserire manualmente]`
   - **Resto del corpo**: tono **caloroso/colloquiale** italiano (non eccessivamente formale). Stile esempio:

     ```
     → Email cliente: rocco.condello@example.it

     Buongiorno [Nome o Spett.le RagioneSociale],

     in allegato trova il preventivo richiesto per [oggetto sintetico].
     Per qualsiasi necessità o chiarimento ci scriva pure.

     A presto,
     Attilio
     Ingenio Solution
     ```

   - Il testo è scritto **come se fosse spedito al cliente**, non ad Attilio — Ralf poi lo inoltrerà.
5. **Invio default = send diretto** (non bozza). Modalità:
   - Mostrare a Ralf in chat l'anteprima dell'email (oggetto + corpo + nome allegato + destinatario)
   - Inviare via MCP Gmail subito dopo, **a meno che Ralf interrompa o chieda esplicitamente "fai bozza"**
   - Se Ralf dice "fai bozza" o "mostrami prima" → usare `mcp__claude_ai_Gmail__create_draft` invece di send
   - Coerente con regola 2 (CLAUDE.md): l'anteprima in chat è la "descrizione dell'azione", l'assenza di interruzione è la "conferma equivalente"
6. **Log**: aggiungere riga in `logs/YYYY-MM.md` con data + "Email preventivo Nr X inviata ad attilio.fiumano (cliente Y, oggetto: ...)".

### Convenzione FM consigliata per `oggetto email`

Quando si crea un nuovo preventivo in FM, popolare il campo `Preventivo::oggetto email` con un titolo sintetico (es. "Preventivo per fornitura PC", "Preventivo manutenzione annuale"). Sarà usato sia dallo script FM "Invia preventivo via email" sia da questo workflow.

---

*Aggiornato: 2026-05-04*
