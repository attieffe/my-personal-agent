# FileMaker Server — DADEGEST

## Connessione

- **Host**: `FM_HOST` (da .env) | **Porta**: `FM_PORT` (da .env) (HTTPS self-signed, FM 19.3.2.203)
- **Credenziali**: vedere `.env` → `FM_USER` / `FM_PASSWORD`
- **API base URL**: `https://FM_HOST:FM_PORT/fmi/data/v2`
- **SSL**: certificato self-signed → `NODE_TLS_REJECT_UNAUTHORIZED=0` in `filemaker.mjs` (già gestito)

> **⚠️ Raggiungibilità**: il server FM deve essere accessibile da questa macchina sulla porta FM_PORT.
> La porta deve essere aperta/forwardata nel router se si accede da fuori rete locale.
> Gli snippet PowerShell sotto sono documentazione storica (provenivano da Windows); su Linux usare `npm run preventivo` o curl equivalente.

---

## Architettura multi-file

DADEGEST è il file **master** (layouts, script, logica). I dati vivono in **file esterni** separati, tutti accessibili con le stesse credenziali:

| Database FM | Contenuto | Layout | Accessibile |
|---|---|---|---|
| **DADEGEST** | Master applicazione | Tutti i layout UI | ✅ |
| **anagrafiche** | Clienti, Fornitori, Articoli, **Iva**, **Pagamenti Preventivo**, Destinazione Merce, Listini, Nazioni/Province/Regioni, UM, Famiglia/MacroFamiglia, Centri costo, Agenti | 21 | ✅ |
| **fatture** | Fatture vendita | 11 | ✅ |
| **DDT** | Documenti di trasporto | 11 | ✅ |
| **Preventivi** | Preventivi | 11 | ✅ |
| **righe vendita** | Righe di tutti i documenti | 2 | ✅ |
| **Fatture acq** | Fatture acquisto | 21 | ✅ |
| **GENERALEParametri** | Parametri globali | 4 | ✅ |
| **Parametri** | Anagrafica azienda + utenti + struttura articolo | 4 | ✅ |
| **SyncPrj** | MirrorSync (replica) | — | ❌ (credenziali diverse) |

---

## Struttura dati — Layout principali

### Anagrafiche

#### M_CLI_000 — Clienti (50 record)
**Tabella**: `Clienti` nel file `anagrafiche`

| Gruppo | Campi chiave |
|---|---|
| Identificativo | Codice, Ragione Sociale, P.IVA, C.F. |
| Indirizzo | Indirizzo, Cap, Città, Provincia, CodNazione, Nazione |
| Contatti | Telefono 1-3, Email 1-2, Fax 1-2, Cellulare 1-3 (tutti con Note) |
| Commerciale | Listino Vendita, Cod Pagamento, Descrizione Pagamento, Cod Esenzione IVA |
| Fatturazione elettronica | fattura elettronica codicedestinatario, pec trasmissione fattura |
| Agente | Codice Agente, Agente |
| KPI anno corrente | Valore imponibile: preventivi, ordinato, consegnato, fatturato, resi |

**Portali collegati**: Destinazione Merce Clienti, Preventivo_Clienti, Ordini_Cliente, ddt_clienti, Reso da Cliente, fatture_clienti

---

#### M_FOR_000 — Fornitori
**Tabella**: `Fornitori` nel file `anagrafiche`

Struttura simile a Clienti. Campi extra: Pagamento automatico attivato, Centro di costo, cod NAZIONE sede legale.

---

#### M_ART_000 — Prodotti/Articoli (26 record)
**Tabella**: `Prodotti` nel file `anagrafiche`

| Gruppo | Campi chiave |
|---|---|
| Codifica | Tipologia Articolo, Precodice, Codice Articolo, Codice EAN 12 |
| Classificazione | Macrofamiglia, IDMacrofamiglia, Famiglia, IDFamiglia |
| Descrizione | Descrizione, TXT 1-3, NUM 1 |
| Dimensioni | Lunghezza, Larghezza, Altezza, Peso Netto, Peso Lordo, Pz per imballo |
| Prezzi | Costo, Costo Netto, Sc 1-3, Codice IVA, Unità di Misura |
| Giacenze | Inventario Iniziale, Qta Consegnata, In Ordine, Resa, Caricata, Prodotta, Scaricata, Rettificata, Giacenza, Giacenza Futura |
| Valore | VALORE GIACENZA AL COSTO |
| Posizione | Posizione Magazzino |

**Portali**: Listino Acquisto, Listino Vendita, Distinta Base

---

#### Iva — Codici IVA (16 record)
**Layout**: `Iva` nel file `anagrafiche`

| Campo | Tipo | Esempio |
|---|---|---|
| `Codice` | string | `22`, `22R`, `NI8`, `ESC15`, `ES10C1` |
| `Descrizione` | string | `Iva 22%`, `Non Imponibile Art. 8/A - D.P.R. 633/72` |
| `Aliquota` | number | `22`, `0` |
| `Flag NI` | string | `x` se non imponibile / esente / escluso, vuoto altrimenti |
| `IDDADE` | string | `DADE` (chiave tecnica) |

Codici principali in uso: `4`, `10`, `21`, `22`, `22R` (reverse charge) + serie `NI*`, `ESC*`, `ES10C1`. Usato per il **riepilogo IVA in fondo ai documenti**: raggruppare le righe per `CodiceIva` e mostrare `Codice → Descrizione → Imponibile → IVA`.

---

#### Pagamenti Preventivo — Codici pagamento (13 record)
**Layout**: `Pagamenti Preventivo` nel file `anagrafiche`

| Campo | Tipo | Note |
|---|---|---|
| `Codice` | string | `001`...`013` |
| `Descrizione` | string | es. `Bonifico 60 gg fm`, `Anticipo 30% saldo a Consegna`, `Bonifico Bancario Vista` |
| `Tipo Pagamento` | string | `BONIFICO`, `RID`, `RI.BA. 60gg`, `RIMESSA DIRETTA` |
| `Decorrenza` | string | `Fine Mese`, `Data Documento`, `Anticipato`, `Data Fattura` |
| `Rata GG 1(1..5)`, `PERC IMPONIBILE 1(1..5)`, `PERC IVA 1(1..5)`, `nr rate` | misti | scadenze dettagliate (non servono in preventivo, usate in fattura) |

**Per il preventivo basta `Descrizione`**: V_PRE_000 contiene già `Cod Pagamento` + `Descrizione Pagamento` denormalizzati nella testata, quindi **non serve fare il join** lato API per generare il PDF preventivo. Le scadenze articolate non vanno esposte in preventivo (richiesta utente: solo condizione generica).

---

### Anagrafica azienda — file `Parametri`

**Layout API-friendly**: `Parametri` nel file `Parametri` (1 record singleton). Contiene l'identità dell'azienda licenziataria + dati bancari + container immagini.

#### Campi rilevanti per la stampa documenti

| Campo | Esempio | Note |
|---|---|---|
| `Ragione Sociale` | `Ingenio Solution S.a.s. di Fiumanò Attilio` | Header documenti |
| `P.iva` | `08971020964` | Header |
| `C.f.` | `08971020964` | Header |
| `Indirizo` | `via Pacini 77` | ⚠️ typo nel campo (manca una "z") |
| `Cap` / `Città` / `Prov` | `20831` / `Seregno` / `MB` | Header |
| `Logo max 9.5x2.5` | URL container | ⚠️ è un campo container — vedi sezione "Container fields" |
| `Intestazione banca` | `Ingenio Solution S.a.s. di Fiumanò Attilio` | Footer / coordinate bancarie |
| `Nome Banca d'appoggio` | `Banco BPM` | Footer |
| `IBAN banca d'appoggio` | `IT93O0503433842000000003795` | Footer |
| `BIC SWIFT` | `BPMIITMMXXX` | Footer (eventuale) |
| `ABI` / `CAB` | `05034` / `33842` | Coordinate bancarie italiane |
| `pie pagina` | `Ingenio Solution S.a.s. ... - tel. +39 0362 1636590 e-mail. info@ingeniosolution.it` | Footer pre-formattato. ⚠️ contiene un punto di concatenazione senza spazio prima di `tel.`: normalizzare con replace `tel.` → `\ntel.` o spazio |

**Container "payoff 1-6"**: 6 immagini secondarie (non utilizzate per il PDF preventivo).

#### Campi NON rilevanti per il PDF preventivo (presenti ma da ignorare)

`@Contenitore1`, `de_acq 1-20`, `de_art 1-20`, `de_cli 1-20`, `de_for 1-20`, `de_varie 1-20`, `de_ven 1-20` (label custom dell'applicazione), `codice licenza`, `data installazione licenza`, `Validità licenza`, `Codice fiscale trasmittente`, `xml id trasmittente`, `Progressivo`, `Tipo Struttura`, `Licenza intestata a`, `P.iva licenziatario`, `DATA OGGI`.

---

### Container fields — download

I campi container in FileMaker (es. `Logo max 9.5x2.5`, `payoff 1-6`) restituiscono via Data API un URL del tipo:

```text
https://localhost/Streaming/Additional_1/<HASH>.png?RCType=EmbeddedRCFileProcessor
```

**Per scaricarlo**:
1. La sessione FM deve essere ancora attiva (token bearer valido)
2. Chiamare l'URL in HTTPS GET con header `Authorization: Bearer <token>` (bypass SSL self-signed come per gli altri endpoint Data API)
3. Il body della response è il binario raw dell'immagine (Content-Type es. `image/png`)
4. Per inlineare in HTML/PDF: convertire in base64 e usare `data:<mime>;base64,<b64>` come `src` di `<img>`

⚠️ **Logout dopo il download**: scaricare il container *prima* del logout della sessione, altrimenti il token non è più valido e l'URL ritorna 401.

---

### Ciclo Attivo (Vendite)

#### V_PRE_000 — Preventivi (245 record)
**Tabella**: `Preventivo` nel file `Preventivi`

| Gruppo | Campi chiave |
|---|---|
| Documento | Nr, Anno, Data, Data Validità, Stato, Tabella |
| Cliente | Cod Cliente, Ragione Sociale + anagrafica completa (relazione Clienti) |
| Totali | Totale Imponibile, Totale IVA, Totale |
| Destinazione merce | Cod, Ragione Sociale, Indirizzo, Cap, Città, Provincia, Tel 1-2 |
| Trasporto | Aspetto dei beni, Peso Netto/Lordo, Consegna |
| Opzioni stampa | SALTO PAGINA, STAMPA TOTALE, FIRMA PER ACCETTAZIONE, SENZA QTA, SENZA PARZIALI |
| Email | oggetto email |
| Controllo costi | (via portale) totale costo, totale guadagno |

**Portale**: Righe Vendita Preventivo

---

#### V_ORD_000 — Ordini (0 record)
**Tabella**: `Ordini`

---

#### V_DDT_000 — DDT (26 record)
**Tabella**: `ddt` nel file `DDT`

| Gruppo | Campi chiave |
|---|---|
| Documento | Nr, Anno, Data, Stato, Tabella |
| Cliente | Cod Cliente, Ragione Sociale + anagrafica |
| Destinazione merce | completa |
| Trasporto | Vettore, Trasporto mezzo, CAUSALE, Aspetto beni, Peso Netto/Lordo |
| Totali | Totale Imponibile, IVA, Totale |

**Portali**: Righe Vendita ddt, Ordini, Righe Ordini da evadere

---

#### V_FAT_000 — Fatture Vendita (459 record)
**Tabella**: `fatture` nel file `fatture`

| Gruppo | Campi chiave |
|---|---|
| Documento | Nr, Anno, Data, Stato, Tabella, NR REGISTRO |
| Cliente | Cod Cliente + anagrafica + contatti (relazione Clienti 4) |
| Totali | Totale Imponibile, IVA, Totale |
| Pagamento | tipo pagamento, Cod Pagamento, Descrizione Pagamento |
| Scadenzario | fino a 5 scadenze: Data, Importo, Pagato, Da pagare — Totale Da pagare, Totale Scaduto |
| Scadenze forzate | Scadenza forzata (1-5) |
| Destinazione merce | completa |
| Trasporto | Aspetto beni, Peso Netto/Lordo, Consegna |
| Fattura elettronica | xml content, xml header, xml dati riepilogo, xml causale, CAUSALE CONTABILE |
| Bollo | Bollo |
| Collegamento | id_testa Precedente, id_testa Precedenti, percorso file |

**Portali**: Righe Vendita Fatture, ddt, Righe DDT o reso da evadere, Reso da Cliente da evadere

---

#### Righe_Vendita (1862 record) — tabella trasversale
**Tabella**: `Righe_Vendita` nel file `righe vendita`

| Gruppo | Campi chiave |
|---|---|
| Chiavi | IDTESTA, IDRIGA, ID_ARTICOLO |
| Articolo | TIPOLOGIA_ARTICOLO, CODICE_ARTICOLO, DESCRIZIONE, UM |
| Fiscale | CodiceIva, Aliquota Iva, segno Fiscale |
| Prezzo | Prezzo, Sc_1, Sc_2, Sc_3, Prezzo_Netto, CodListino |
| Sconti finali | Sc f 1, Sc f 2, Sc f 3, Prezzo f |
| Quantità | QTA, QTA_evasa, QTA_da_evadere |
| Importi | imponibile, Iva, Totale riga |
| Magazzino | segno magazzino |
| Stato | Stato Nr, Stato Txt |
| Evasione | IdRigaPrecedente, id_testa_evadente |
| KPI | Qta/Valore: Ordinata, Consegnata, In ordine, Fatturata, Resa (cliente) |
| Metadati | Data, anno |

---

### Ciclo Passivo (Acquisti)

#### A_FAT_000 — Fatture Acquisto (1 record, template)
**Tabella**: `Fatture Acq` nel file `Fatture acq`

Struttura simile a V_FAT_000 ma lato fornitore. Campi extra: Nr Documento Fornitore, Data Documento Fornitore.
**Portali**: Righe Acquisto fa, Carichi Acquisto, Righe Acquisto da evadere fa, reso a fornitore

---

#### Registro Acquisti — Archivio contabile fatture passive (pseudo-contabile)
**Database**: `Fatture acq` | **Layout**: `registro acquisti` (50+ record)

**Descrizione**: È l'archivio dove confluiscono TUTTE le fatture di acquisto registrate. È il vero registro contabile per la contabilità IVA — non il file importato da fatture elettroniche, ma il consolidamento in registro.

| Campo | Significato | Note |
|---|---|---|
| `Nr Reg.` | Numero progressivo registrazione | Univoco per registro |
| `Data` | Data fattura / documento | Data del documento fornitore |
| `Data reg.` | Data registrazione | Quando è stata registrata |
| `Fornitore` | Ragione sociale fornitore | Da anagrafica fornitori |
| `Nr documento` | Numero fattura fornitore | Identificativo esterno |
| `Categoria` | Categoria di spesa | Es. "Servizi", "Manutenzione Auto", "Formazione" |
| `Partita IVA` | P.IVA fornitore | Spesso vuoto se non estero |
| `IVA` | Aliquota IVA % | `22`, `10`, `0` |
| `Imponibile import` | Imponibile lordo | Base imponibile |
| `Valore iva` | Importo IVA | IVA calcolata |
| `Totale` | Importo totale | Imponibile + IVA |
| `% DED` | Deducibilità IVA % | `100%` ordinaria, `40%` esente, `20%` mista |
| `% IVA DETR` | Percentuale detraibilità | Correlato a deducibilità |
| `mostra iva esente` | Flag esente | `1` se esente/reverse charge, `0` ordinaria |
| `Natura` | Natura contabile | Spesso vuoto nel registro (vedi DatiRiepilogo per Natura=N4/N1/N2) |
| `nome file xml` | Riferimento file XML | Se importato da fatturazione elettronica |
| `id liquidazione` | Link a liquidazione IVA | Es. "2026.2.0" (anno.trimestre.0) |

**Filtro Reverse Charge / EXTRA UE**:
- `IVA = 0` + `mostra iva esente = 1` → Record esente o reverse charge
- Per dettagli sulla natura esatta (N4=reverse charge, N1=EXTRA UE, ecc.), consultare:
  - **Fatture acq** / layout **DatiRiepilogo** (contenuto XML importato)
  - Campo `Natura` nella fatturazione elettronica (N4=reverse charge, N1=EXTRA UE, ecc.)

**Collegamento a fatturazione elettronica**:
- Campo `nome file xml` linka al layout `DatiRiepilogo` nel database `Fatture acq`
- Nel `DatiRiepilogo`, il campo `Natura` specifica il regime IVA (N4, N1, N2, ecc.)
- Il registro acquisti è la **visione contabile semplificata**, il DatiRiepilogo è il **dettaglio per riga XML**

---

#### DatiRiepilogo — Riepilogo IVA per documento (importato da e-fattura)
**Database**: `Fatture acq` | **Layout**: `DatiRiepilogo`

Contiene il riepilogo IVA estratto dai file XML di fatturazione elettronica.

| Campo | Significato | Esempio |
|---|---|---|
| `Fattura` | Nome file XML fattura | `IT0526289001419059_8PMU4.xml` |
| `AliquotaIVA` | Aliquota % | `22.00`, `10.00`, `0.00` |
| `Natura` | Codice natura regime IVA | `N4` (reverse charge), `N1` (EXTRA UE), `N2` (esente), vuoto (ordinaria) |
| `ImponibileImporto` | Importo imponibile | €15.49, €30.00 |
| `Imposta` | Importo IVA | €0.00 (per reverse charge) |
| `EsigibilitaIVA` | Esigibilità | `I` (Immediata) |

**Natura IVA Codici**:
- Nessuno / vuoto = **Ordinaria** (aliquota 22%, 10%, ecc.)
- **N1** = EXTRA UE (fornitore fuori UE, reverse charge dell'acquirente)
- **N2** = Esente
- **N4** = Reverse charge interno (acquisto da fornitore italiano)

---

## Flusso documenti (Ciclo Attivo)

```
Preventivo → Ordine → DDT → Fattura
   (V_PRE)    (V_ORD)  (V_DDT)  (V_FAT)
      ↓           ↓        ↓        ↓
              Righe_Vendita (tabella unica trasversale)
```

Le righe di tutti i documenti condividono la stessa tabella `Righe_Vendita`. Il collegamento avviene tramite `IDTESTA` + evasione tramite `IdRigaPrecedente` / `id_testa_evadente`.

---

## Script disponibili

| Script | File | Layout | Parametro | Effetto |
|---|---|---|---|---|
| `Invia preventivo via email` | DADEGEST | V_PRE_000 | `AUTO` | Genera PDF preventivo e lo invia via email al cliente |

### Come eseguire uno script

```powershell
# Agganciare lo script a una GET sul record (non modifica dati)
$scriptName = [Uri]::EscapeDataString('Invia preventivo via email')
$url = "https://localhost/fmi/data/v2/databases/DADEGEST/layouts/V_PRE_000/records/{recordId}?script=$scriptName&script.param=AUTO"
$r = Invoke-WebRequest -Uri $url -Method GET -Headers $h -UseBasicParsing
$json = $r.Content | ConvertFrom-Json
# Verificare: $json.response.scriptError -eq 0 = successo
```

**Note script:**
- Non esiste un endpoint standalone "run script" — lo script va agganciato a un'operazione CRUD (GET, POST, PATCH, DELETE)
- `script.param` passa il parametro come stringa
- `scriptError: 0` = eseguito correttamente
- I nomi script sono case-sensitive e vanno URL-encoded

---

## Modifica record — PATCH

Endpoint generico:
```
PATCH /fmi/data/v2/databases/{db}/layouts/{layout}/records/{recordId}
Body: {"fieldData": {"Campo": "valore"}}
```

### Preventivo V_PRE_000 — campi modificabili via PATCH

| Campo | Scrivibile | Note |
|---|---|---|
| `Cod Pagamento` | ✅ | Impostare solo questo — FM auto-popola `Descrizione Pagamento` via lookup |
| `Descrizione Pagamento` | ❌ | Campo lookup/calcolato → errore FM 201 se si tenta PATCH diretto |
| `Note Documento` | ✅ | Testo plain (nessun HTML — il template lo escapa) |

**Errore FM 201** = "Field cannot be modified" → il campo è calcolato o lookup, non editabile direttamente via API.

### Codici pagamento preventivo (tabella `anagrafiche` / layout `Pagamenti Preventivo`)

| Codice | Descrizione | Tipo |
|---|---|---|
| `001` | Bonifico 60 gg fm | BONIFICO |
| `002` | Bonifico 60/90 gg fm | BONIFICO |
| `003` | Bonifico IVA 30 gg - saldo 60/90 gg fm | BONIFICO |
| `004` | Bonifico Bancario Vista | BONIFICO |
| `005` | Ricevuta Bancaria 60gg | RI.BA. 60gg |
| `006` | RID 30gg | RID |
| `007` | Rimessa Diretta Vista | RIMESSA DIRETTA |
| `008` | Bonifico 30 gg fm | BONIFICO |
| `009` | Bonifico bancario anticipato | BONIFICO |
| `010` | Anticipo 30% saldo a Consegna | Bonifico |
| `011` | Bonifico bancario data consegna fine mese | BONIFICO |
| `012` | Bonifico 30 gg df fm | BONIFICO |
| `013` | Bonifico 60 gg data fatt. | BONIFICO |

---

## Creazione Fatture Vendita e Righe — Procedura API

### Flusso Completo

1. **POST testata** → `V_FAT_000` → genera `IDTESTA`
2. **POST riga** → `R_FAT_0001` (Righe_Vendita) → referenzia `IDTESTA` dalla testata

---

### 1. Creazione Testata Fattura (V_FAT_000)

#### Campi obbligatori:
```json
{
  "fieldData": {
    "Nr": 5678,
    "Anno": 2026,
    "Data": "06/12/2026",
    "CodCliente": "C00024",
    "Causale": "Fattura di Vendita",
    "TIPO DOCUMENTO": "FATTURA"
  }
}
```

#### Note:
- **Nr + Anno** = Univoci per documento
- **CodCliente** = Codice da M_CLI_000
- **Causale** = Testo fisso per fatture ordinarie; per autofatture reverse charge: "Autofattura Reverse Charge"
- **TIPO DOCUMENTO** = Campo fisso "FATTURA"
- **Totali** (Totale Imponibile, IVA, Totale) = **Calcolati automaticamente** dalle righe

#### Risposta:
```json
{
  "response": {
    "data": [{
      "recordId": "12345",
      "fieldData": { "Nr": 5678, "IDTESTA": "FA12345", ... }
    }]
  }
}
```
**Salva `recordId` e/o `IDTESTA`** per collegare le righe.

---

### 2. Creazione Riga Fattura (R_FAT_0001 / Righe_Vendita)

#### Struttura di una riga:
```json
{
  "fieldData": {
    "IDTESTA": "FA10338",
    "TIPOLOGIA_ARTICOLO": "SERVIZI",
    "CODICE_ARTICOLO": "SRV001",
    "DESCRIZIONE": "Autofattura rif. acquisto merci Art 17 C6 Let C rif fattura NR2025/123 del 01/10/2025 di HOLDEN INTERNATIONAL LTD",
    "UM": "Nr",
    "QTA": 1,
    "Prezzo f": 895.00,
    "Codice Iva f": "22R"
  }
}
```

#### Campi scrivibili (solo questi):
| Campo | Tipo | Scrivibile | Note |
|-------|------|-----------|-------|
| **IDTESTA** | FK | ✅ | Riferimento testata (obbligatorio) |
| **TIPOLOGIA_ARTICOLO** | Lookup | ✅ | Leggi valori da layout "Tipologia Articoli"; esempi: SERVIZI, MATERIALI, DEV, ecc. |
| **CODICE_ARTICOLO** | Text | ✅ | Codice libero (es. "SRV001", "D.002") — può esistere in M_ART_000 oppure no |
| **DESCRIZIONE** | Text | ✅ | Testo descrizione riga (per righe generiche/servizi) |
| **UM** | Text | ✅ | Unità di misura: `Nr` (numero) o `h` (ore) |
| **QTA** | Number | ✅ | Quantità |
| **Prezzo f** | Number | ✅ | Prezzo finale (il valore vero con sconti applicati) |
| **Codice Iva f** | Lookup | ✅ | Codice IVA: `22`, `22R`, `10`, `NI8`, `ESC15`, ecc. |

#### Campi CALCOLATI (NON scrivibili):
| Campo | Calcolato da |
|-------|--------------|
| `IDRIGA` | Auto-numerato |
| `Prezzo_Netto` | Calcolato internamente |
| `imponibile` | QTA × Prezzo f |
| `Aliquota Iva` | Lookup da `Codice Iva f` |
| `Iva` | imponibile × Aliquota Iva / 100 |
| `Totale riga` | imponibile + Iva |
| `Data` | Auto (da IDTESTA) |
| `anno` | Auto (da IDTESTA) |

#### Logica UM (Unità di Misura):
- **UM = "Nr"** (numero): Usa `Prezzo f` direttamente
- **UM = "h"** (ore): 
  - `Prezzo f` = tariffa oraria
  - Se non hai tariffa predefinita, **cerca in fatture precedenti** per lo stesso cliente/fornitore per inferire la tariffa standard
  - Esempio: Se cliente X ha fatture precedenti con UM=h a €50/h, usa quella tariffa

---

### 3. Numero Fattura Sequenziale

Per fatture **ORDINARIE** (non reverse charge):
- Leggi l'**ultimo Nr** per l'anno corrente da V_FAT_000
- Proponi **Nr = ultimo + 1**
- Format: `Nr: 5678, Anno: 2026` → prossima: `Nr: 5679, Anno: 2026`

**Query per ottenere ultimo Nr dell'anno:**
```json
{
  "query": [
    {"Anno": "2026"},
    {"Nr": ">0"}
  ],
  "_sort": [{"fieldName": "Nr", "sortOrder": "descend"}],
  "_limit": 1
}
```

---

### 4. Autofattura Reverse Charge EXTRA UE

**Caso**: Ho acquistato da fornitore EXTRA UE (es. HOLDEN INTERNATIONAL LTD) con reverse charge.

**Procedura Autofattura**:
1. **Creare testata** V_FAT_000 con:
   - `Causale`: "Autofattura Reverse Charge"
   - `Nr`: da logica reverse charge (es. `EU-{Nr registro acquisti}-{Anno}` oppure `REV-{Nr}-{Anno}`)
   - `CodCliente`: C00024 (me stesso, Ingenio Solution)
   - `Data`: stessa data acquisto

2. **Creare riga** R_FAT_0001 con:
   - `DESCRIZIONE`: "Autofattura rif. acquisto merci Art 17 C6 Let C rif fattura {NRFATTACQ} del {DATA} di {FORNITOREORIGINALE}"
   - `Prezzo f`: importo lordo riga acquisto
   - `Codice Iva f`: `22R` (reverse charge)
   - `QTA`: 1, `UM`: "Nr"

3. **Flag nel testata**: 
   - `Ignora in IVA`: 1 (per non trasmettere al registro IVA formale, ma l'IVA esiste contabilmente)
   - L'IVA calcolata sulla riga si annulla con quella dell'acquisto

**Differenza da reverse charge ITALIANO (N4)**:
- **N4 (Italia)**: Causale "Rev", Natura N4
- **N6.6 (EXTRA UE)**: Causale "Rev" (stesso), Natura N6.6, Flag `Ignora in IVA=1` su autofattura

---

### Operazioni API utili

```powershell
# Cerca clienti per ragione sociale
$body = '{"query":[{"Ragione Sociale":"*Mario*"}]}'
Invoke-WebRequest -Uri "https://localhost/fmi/data/v2/databases/DADEGEST/layouts/M_CLI_000/_find" -Method POST -Headers $h -Body $body -UseBasicParsing

# Ultimi 10 preventivi
Invoke-WebRequest -Uri "https://localhost/fmi/data/v2/databases/DADEGEST/layouts/V_PRE_000/records?_limit=10&_sort=[{%22fieldName%22:%22Nr%22,%22sortOrder%22:%22descend%22}]" -Method GET -Headers $h -UseBasicParsing

# Fatture non pagate (Totale Da pagare > 0)
$body = '{"query":[{"Totale Da pagare":">0"}]}'
Invoke-WebRequest -Uri "https://localhost/fmi/data/v2/databases/DADEGEST/layouts/V_FAT_000/_find" -Method POST -Headers $h -Body $body -UseBasicParsing
```

---

## Campi stampa testata V_PRE_000

| Campo | Valori | Effetto |
|---|---|---|
| `STAMPA TOTALE` | `SI` / vuoto | Mostra totale in fondo alla stampa |
| `STAMPA FIRMA PER ACCETTAZIONE` | `SI` / vuoto | Aggiunge riga firma cliente |
| `Stampa SENZA QTA` | valore / vuoto | Nasconde colonna quantità |
| `Stampa SENZA PARZIALI` | valore / vuoto | Nasconde importi parziali riga |
| `STAMPA SALTO PAGINA CON REQIUSITI` | valore / vuoto | Salto pagina prima delle note/requisiti |

Formato IVA inclusa → usare layout `Stampa Preventivo IVA INCL` (non è un campo testata).

---

## Note Documento — pattern per tipo preventivo

Il campo `Note Documento` nella testata del preventivo è la presentazione descrittiva dell'offerta. Varia per tipo.

### Hardware (PC, Monitor, accessori)

**Struttura standard:**
```
Fornitura [numero + descrizione componenti con specifiche]:
- [componente 1 con spec tecniche]
- [componente 2 con spec tecniche]

Tempo di consegna stimata: 14 giorni da conferma
I prezzi sono soggetti a cambi dinamici da parte dei fornitori, pertanto l'offerta potrebbe non essere più applicabile al momento dell'accettazione, in tal caso verranno proposte alternative o i nuovi prezzi in vigore.
Condizioni pagamento: 30% anticipo
70% alla consegna
```

**Varianti condizioni pagamento osservate:**
- `30% anticipo / 70% alla consegna` — ordini > ~400€ o con anticipo richiesto
- `100% alla consegna` — ordini semplici/piccoli
- `30% anticipo / 70% data fattura fine mese dopo consegna` — clienti con pagamento differito

**Template per altri tipi:** da definire quando si presentano (sviluppo web, assistenza, ecc.)

---

## Flusso completo: modifica + rigenera preventivo

1. Identificare recordId con `resolvePreventivo` o `npm run preventivo -- --nr X` (vedi stderr)
2. PATCH i campi modificabili su FM (es. solo `Cod Pagamento`)
3. Rigenerare da sorgente: `npm run preventivo -- --nr X --keep-html`
4. Applicare grassetti in post-processing sull'HTML (regex su `<div class="note">`), perché `template.mjs` usa `escapeHtml()` sulla nota FM → impossibile iniettare `<strong>` dal testo FM
5. Rigenerare PDF da HTML modificato con Edge headless (script `_gen-pdf-from-html.mjs` o equivalente)

---

## Reverse Charge EXTRA UE — Procedura Amministrativa

### Definizioni

- **Natura N6.6**: Servizi internazionali verso committente EXTRA UE (regime reverse charge)
- **Causale "Rev"**: Marcatura per fatture reverse charge (cercare `Causale = "Rev"`)
- **Autofattura**: Fattura di vendita intestata a se stessi (cliente = Ingenio Solution C00024) per registrazione contabile

### Caso di Studio: HOLDEN INTERNATIONAL LTD (09/30/2025)

#### Ciclo Passivo (Acquisto da fornitore EXTRA UE)

**Registro Acquisti** (layout: `Registro acquisti` in database `DADEGEST`):

```
Data: 09/30/2025
Fornitore: HOLDEN INTERNATIONAL LTD
Cod. Fornitore: F00279
Nr Documento: EU-1
Categoria: Formazione
Natura: N6.6
Imponibile: €895,00
IVA applicata: 22% (€196,90)
Totale: €1.091,90
```

**Caratteristiche:**
- Fornitore EXTRA UE (UK) → soggetto a reverse charge
- Natura N6.6 → servizio internazionale
- IVA: registrata al 22% in fase di acquisto, ma sarà neutralizzata a bilancio (non detraibile)
- Imponibile: il valore del servizio ricevuto

#### Ciclo Attivo (Autofattura di vendita)

**Fatture Vendite** (layout: `V_FAT_000` in database `DADEGEST`):

```
Nr Documento: EU-1
Data: 09/30/2025 (stessa del documento origine)
Cliente: C00024 INGENIO SOLUTION S.a.s. (autofattura a se stessi)
Causale: Rev (reverse charge)
Natura: N6.6
Imponibile: €895,00
IVA: 22% (€196,90) — con flag Ignora in IVA = 1
Totale: €1.091,90
```

**Caratteristiche:**
- Autofattura: cliente = fornitore (se stessi)
- IVA: calcolata al 22% (€196,90) esattamente come l'acquisto
- **Ignora in IVA = 1** → non trasmettere al registro IVA/SDI, MA l'IVA va considerata contabilmente perché si annulla con quella dell'acquisto
- Imponibile: identico a quello dell'acquisto
- Natura: N6.6 per tracciabilità
- **Effetto netto**: l'IVA dell'acquisto (non detraibile) si annulla con l'IVA dell'autofattura (non registrata formalmente), risultato = costo netto €895

#### Differenze tra Acquisto e Vendita

| Aspetto | Acquisto (Passivo) | Vendita (Attivo) |
|--------|-------------------|-----------------|
| **Documento** | Fattura HOLDEN EU-1 (fornitore) | Autofattura EU-1 (a se stessi) |
| **Cliente/Fornitore** | HOLDEN INTERNATIONAL LTD | INGENIO SOLUTION C00024 |
| **Data** | 09/30/2025 | 09/30/2025 |
| **Natura IVA** | N6.6 | N6.6 |
| **Imponibile** | €895,00 | €895,00 |
| **IVA** | 22% (€196,90) — non detraibile | 22% (€196,90) — con flag Ignora in IVA |
| **Totale** | €1.091,90 | €1.091,90 |
| **Flag speciale** | (nessuno) | **Ignora in IVA = 1** (non trasmettere SDI) |
| **Causale** | (vuota o generica) | "Rev" (reverse charge) |
| **Trasmissione SDI** | Ricezione da fornitore | Autofattura: trasmessa con flag di annullamento IVA |

#### Flusso Contabile

1. **Acquisto**: €895 imponibile + €196,90 IVA (non detraibile) = €1.091,90
   - Addebito Conto 611xx (acquisto servizi) per €1.091,90
   - IVA a credito: €0,00 (non detraibile in reverse charge EXTRA UE)
   
2. **Autofattura EU-1**: €895 imponibile + €196,90 IVA = €1.091,90
   - Credito Conto 611xx (storno compensativo) per €1.091,90
   - Causale "Rev" + Ignora in IVA = 1 → l'IVA non va registrata nel registro IVA formale
   - Contabilmente: l'IVA di €196,90 si annulla con quella dell'acquisto

3. **Risultato finale**: 
   - Costo netto al bilancio: €895,00 (l'IVA non detraibile si compensa)
   - Registro IVA: solo l'IVA dell'acquisto, **senza l'autofattura** (per effetto del flag Ignora in IVA)

#### Campi chiave in Query

Per cercare reverse charge EXTRA UE in `Registro acquisti`:

```sql
SELECT * FROM "Registro acquisti"
WHERE Natura = "N6.6"
  AND Data > "01/01/2025"
  AND Totale > 800
ORDER BY Data DESC
```

O in M_FOR_000 (anagrafica fornitori):
- Cercare fornitori con `Nazione ≠ ITALIA`
- Verificare `CodNazione` per identificare EXTRA UE (non-UE27 / non-EEA)

---

## Procedura Registrazione Reverse Charge — Passo passo

### 1️⃣ ACQUISTO (Ciclo Passivo - Registro Acquisti)

**Campi da compilare:**

| Campo | Valore | Note |
|-------|--------|-------|
| **Codice fornitore** | Cercare in anagrafica (M_FOR_000) o scrivere se nuovo | Verificare se già esistente |
| **Data** | Data documento ricevuto | formato MM/DD/YYYY |
| **Data Registrazione** | Data registrazione contabile | (diversa da Data se ritardi) |
| **Nr Protocollo** | Sequenziale per anno | Es. 2026 primo=1, secondo=2 |
| **Nr Documento** | Numero fattura fornitore | Es. EU-1 |
| **Fornitore** | Ragione Sociale | Es. HOLDEN INTERNATIONAL LTD |
| **Imponibile import** | Importo netto | €895,00 |
| **Aliquota IVA** | 22 | (campo da scrivere) |
| **Valore iva** | Calcolato al 22% | €196,90 (o calcolo automatico) |
| **Categoria** | Categoria spesa | Es. Formazione, Servizi |
| **Natura** | N6.6 (EXTRA UE) o N1 (varia) | Reverse charge marker |
| **Causale** | "Rev" | Flag reverse charge |
| **Deduzione %** | Trigger da Categoria | Es. 100%, 40% (verificare se via API attiva) |
| **Detrazione %** | Trigger da Categoria | Idem |

**Post-registrazione:**
- FileMaker calcola automaticamente: Totale, Valore IVA (se aliquota impostata)
- Verificare che IVA non sia detraibile (Natura N6.6 → non a credito)

---

### 2️⃣ VENDITA (Ciclo Attivo - V_FAT_000 con Portale Righe)

#### A) Se Reverse Charge ITALIANO (es. ESPRINET):

**Testata V_FAT_000:**

| Campo | Valore | Formula |
|-------|--------|---------|
| **Nr Documento** | REV-{NrProgressivo}{Anno} | Es. REV-1-2026 |
| **Data Registrazione** | Stessa del documento acquisto | 10/15/2025 |
| **Stato** | "Emessa" o bozza | Configurabile |
| **Cliente** | C00024 | INGENIO SOLUTION (autofattura) |
| **Causale** | "Autofattura Reverse Charge" | Identificare il tipo |
| **Imponibile** | Identico all'acquisto | €1.125,91 (Esprinet) |
| **Cod Esenzione IVA** | 22R | Reverse charge marker |

**Portale Righe Vendita (obbligatorio):**

Una riga con:
- **Descrizione**: "Autofattura rif. acquisto merci Art 17 C6 Let C rif fattura {NRFATTACQ} del {DATA} di {FORNITOREORIGINALE}"
  - Es: "Autofattura rif. acquisto merci Art 17 C6 Let C rif fattura ESPRINET del 10/15/2025 di ESPRINET S.P.A."
- **Importo**: €1.125,91
- **Cod IVA**: 22R
- **Quantità**: 1
- **Totale Riga**: €1.125,91 (senza IVA per 22R)

**Post-registrazione:**
- Totale testata: deve coincidere con totale acquisto

---

#### B) Se Reverse Charge EXTRA UE (es. HOLDEN):

**Testata V_FAT_000:**

| Campo | Valore | Formula |
|-------|--------|---------|
| **Nr Documento** | EU-{NrProgressivo}-{Anno} | Es. EU-1-2026 |
| **Data Registrazione** | Stessa del documento acquisto | 09/30/2025 |
| **Cliente** | C00024 | INGENIO SOLUTION (autofattura) |
| **Causale** | "Autofattura Reverse Charge EU" | Identificare tipo EXTRA UE |
| **Imponibile** | Identico all'acquisto | €895,00 (HOLDEN) |
| **Cod Esenzione IVA** | N6.6 | EXTRA UE marker |
| **Ignora in IVA** | 1 | ⚠️ Non trasmettere SDI |

**Portale Righe Vendita:**

⚠️ **PER HOLDEN EXTRA UE NON SERVE RIGA DI AUTOFATTURA** — è già registrata come partita passiva, l'autofattura è solo il corrispettivo per neutralità IVA.

Se serve comunque per completezza, una riga generica:
- **Descrizione**: "Reverse Charge servizio EXTRA UE — neutralità IVA"
- **Importo**: €895,00
- **Cod IVA**: N6.6 o 22R (dipende setup)

---

### Differenza ESPRINET vs HOLDEN

| Aspetto | ESPRINET (IT, Rev Charge IT) | HOLDEN (EXTRA UE) |
|--------|-------------------------------|-------------------|
| **Tipo** | Reverse charge italiano (fornitor IT ma regime RC) | Reverse charge EXTRA UE |
| **Nr Autofattura** | REV-#-2026 | EU-#-2026 |
| **Riga di autofattura** | ✅ **OBBLIGATORIA** (Art 17 C6) | ❌ **NON SERVE** |
| **Descrizione riga** | Riferi mento acquisto (Art 17 C6 Let C) | (Saltare) |
| **Ignora in IVA** | 0 (trasmettere SDI) | 1 (non trasmettere) |
| **Natura** | 22R (o dipende setup) | N6.6 |
| **IVA Contabile** | €196,90 (si annulla) | €196,90 (si annulla) |

---

### 3️⃣ Accesso Portale Righe via API

**Domanda aperta**: Come accedere al portale "Righe Vendita" da V_FAT_000 via FM Data API v2?

Opzioni:
- A) Leggi direttamente da V_FAT_000 (layout parent) → portale dovrebbe essere visibile in `portalData`
- B) Query separata sulla tabella Righe_Vendita con foreign key
- C) Inserimento via portale record (se FM Data API supporta)

**Da verificare tecnicamente** con test POST/PUT su portale.

---

---

## API Registration Flow — Tested & Working (partial)

### ✅ Ciclo Attivo (Sales/Autofattura) — V_FAT_000

**Step 1: Create Fattura Testata**

```bash
curl -s -X POST \
  "https://FM_HOST:FM_PORT/fmi/data/v2/databases/DADEGEST/layouts/V_FAT_000/records" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "fieldData": {
      "Anno": "2026",
      "Nr": "5678",
      "Data": "06/11/2026",
      "Cod Cliente": "C00001",
      "CAUSALE CONTABILE": "Autofattura Reverse Charge EXTRA UE",
      "Cod Esenzione iva": "22",
      "Cod Pagamento": "007"
    }
  }'
```

**Response**: `recordId: 10374`

**Fields Writable via API**:
- `Anno` (year) — string
- `Nr` (invoice number) — must be unique per year
- `Data` (date) — format MM/DD/YYYY or locale-aware
- `Cod Cliente` (customer code) — must exist in M_CLI_000
- `CAUSALE CONTABILE` (accounting reason) — free text
- `Cod Esenzione iva` (IVA exemption code) — e.g. "22", "22R", "N6.6"
- `Cod Pagamento` (payment code) — e.g. "007"

**Fields AUTO-CALCULATED** (read-only via API):
- `Ragione Sociale` (customer name) — lookup from Cod Cliente
- `Indirizzo`, `Cap`, `Città`, etc. — customer anagrafica
- `Totale Imponibile`, `Totale Iva`, `Totale` — sum of righe
- `NR REGISTRO` — auto-incremented
- `Tabella` — auto-set to "FATTURA"
- `percorso file` — generated on print
- `IdTesta` — unique record identifier

---

**Step 2: Create Riga Vendita**

⚠️ **Current Blocker**: Direct POST to `Righe_Vendita` layout returns error 500 "Field cannot be modified" even with minimal fields (IDTESTA, CODICE_ARTICOLO, QTA, Prezzo).

**Workaround Options (to be tested)**:
1. Access via portale record in V_FAT_000 (endpoint syntax TBD)
2. Call FileMaker script via API to trigger riga creation
3. Use PATCH on existing riga instead of POST for new record
4. Check if "Registro Acquisti" layout has different access permissions

**Expected Endpoint** (not yet working):
```bash
POST /fmi/data/v2/databases/DADEGEST/layouts/Righe_Vendita/records
{
  "fieldData": {
    "IDTESTA": "10374",
    "CODICE_ARTICOLO": "S.002",
    "DESCRIZIONE": "Rinnovo Dominio",
    "QTA": "1",
    "Prezzo": "50"
  }
}
```

---

### ⚠️ Ciclo Passivo (Acquisitions) — Registro Acquisti

**Status**: Database `Fatture acq` returns HTTP 401 — token from DADEGEST login not valid for external database access.

**Expected Flow**:
1. Create record in `Fatture acq` → `Registro acquisti` layout
2. Fields: Data, Fornitore, Nr documento, Imponibile, IVA, Natura, Causale

**Next Step**: Verify if Registro Acquisti is accessible via DADEGEST database with linked layout, or requires separate login.

---

## Test Scripts

- `test_fattura_full.mjs` — Creates V_FAT_000 record (✅ working)
- `test_portale.mjs` — Reads fattura with portalData (✅ working)
- `test_riga_via_portale.mjs` — Tries portal POST (❌ endpoint not found)
- `test_riga_articolo_esistente.mjs` — POST to Righe_Vendita with existing articolo (❌ field protection)
- `test_registro_acquisti.mjs` — POST to Registro acquisti (❌ 401 auth)

*Procedura: 11/06/2026 — Partial implementation tested*
