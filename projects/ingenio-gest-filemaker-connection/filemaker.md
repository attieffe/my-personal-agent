# FileMaker Server — DADEGEST

## Connessione

- **Host**: `FM_HOST` (da .env) | **Porta**: `FM_PORT` (da .env) (HTTPS self-signed, FM 19.3.2.203)
- **Credenziali**: vedere `.env` → `FM_USER` / `FM_PASSWORD`
- **API base URL**: `https://FM_HOST:FM_PORT/fmi/data/v2`
- **SSL**: certificato self-signed → bypass obbligatorio in PowerShell (vedere snippet sotto)

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

#### A_FAT_000 — Fatture Acquisto (1 record)
**Tabella**: `Fatture Acq` nel file `Fatture acq`

Struttura simile a V_FAT_000 ma lato fornitore. Campi extra: Nr Documento Fornitore, Data Documento Fornitore.
**Portali**: Righe Acquisto fa, Carichi Acquisto, Righe Acquisto da evadere fa, reso a fornitore

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

## Operazioni API utili

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

*Aggiornato: 2026-05-04*
