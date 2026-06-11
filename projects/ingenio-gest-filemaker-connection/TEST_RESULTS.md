# FileMaker API Test Results — 2026-06-11

## 🎯 Obiettivo
Dimostrare la capacità di registrare fatture via FM Data API v2:
- Ciclo Passivo: Registro Acquisti (fatture ricevute)
- Ciclo Attivo: V_FAT_000 + Righe_Vendita (autofatture)

---

## ✅ Successi

### 1. Autenticazione FM Data API v2
- **Endpoint**: `POST /fmi/data/v2/databases/DADEGEST/sessions`
- **Auth**: Basic Auth con FM_USER / FM_PASSWORD da .env
- **Token**: Valido per accesso a DADEGEST
- **Status**: ✅ FUNZIONA

### 2. Lettura dati V_FAT_000
- **Query**: GET `/fmi/data/v2/databases/DADEGEST/layouts/V_FAT_000/records`
- **Risultato**: Lettura record storici, analisi campi disponibili
- **Campi analizzati**: Anno, Nr, Data, Ragione Sociale, Totale, etc.
- **Status**: ✅ FUNZIONA

### 3. Creazione Fattura V_FAT_000
- **Endpoint**: `POST /fmi/data/v2/databases/DADEGEST/layouts/V_FAT_000/records`
- **Campi inviati**: Anno, Nr, Data, Cod Cliente, CAUSALE CONTABILE, Cod Esenzione iva, Cod Pagamento
- **Risultato**: recordId 10374 creato
- **Note**: 
  - Campi calcolati (Totale, Ragione Sociale) ignorati correttamente
  - Nr deve essere univoco per anno (controllo FM)
- **Status**: ✅ FUNZIONA

### 4. Lettura Portale Righe Vendita
- **Endpoint**: GET `/fmi/data/v2/databases/DADEGEST/layouts/V_FAT_000/records/{id}`
- **Portale**: "Righe Vendita Fatture" accessibile in portalData
- **Risultato**: Struttura portalData visibile, vuota per fattura nuova
- **Status**: ✅ FUNZIONA (lettura)

---

## ❌ Blocchi

### 1. Creazione Riga via Righe_Vendita Layout
- **Endpoint**: `POST /fmi/data/v2/databases/DADEGEST/layouts/Righe_Vendita/records`
- **Errore**: HTTP 500 — `Field cannot be modified`
- **Campo testato**: IDTESTA, CODICE_ARTICOLO, DESCRIZIONE, QTA, Prezzo
- **Causa**: Layout ha protezioni di campo che impediscono INSERT via API
- **Status**: ❌ BLOCCATO

### 2. Creazione Riga via Portale POST
- **Endpoint ipotizzato**: `POST /fmi/data/v2/databases/DADEGEST/layouts/V_FAT_000/records/{id}/{portalName}`
- **Errore**: HTTP 404 — `Cannot POST /fmi/data/v2/.../Righe Vendita Fatture`
- **Nota**: FM Data API v2 non supporta POST su portali (diversamente da v1)
- **Status**: ❌ ENDPOINT NON ESISTE

### 3. Accesso Database Fatture acq
- **Endpoint**: `POST /fmi/data/v2/databases/Fatture acq/layouts/Registro acquisti/records`
- **Errore**: HTTP 401 — `Invalid FileMaker Data API token (*)`
- **Causa**: Token da DADEGEST non valido per accedere a database esterno
- **Possibile causa**: Requisito di login separato o permissions mancanti
- **Status**: ❌ ACCESSO NEGATO

---

## 🔍 Analisi campi Righe_Vendita

Campi presenti in riga di esempio (FA46_VE462):
```
IDTESTA: FA46 ✓ (foreign key — funziona)
IDRIGA: VE462 (auto-generato)
ID_ARTICOLO: SER.S.002 (lookup formula)
CODICE_ARTICOLO: S.002 (user input)
DESCRIZIONE: RINNOVO DOMINIO ANNUALE (user input)
QTA: 1 (user input)
Prezzo: 30 (user input)
CodiceIva: 22 (user input)
Aliquota Iva: 22 (lookup)
Prezzo_Netto: 30 (calculated)
imponibile: 30 (calculated)
Iva: 6.6 (calculated)
Totale riga: 36.6 (calculated)
```

**Evidenza**: Anche con input minimalista (solo IDTESTA + QTA), FM rifiuta il write con "Field cannot be modified".

---

## 📋 Campi Scrivibili V_FAT_000 (Verificati)

| Campo | Tipo | Note |
|---|---|---|
| `Anno` | string | Anno fiscale, required |
| `Nr` | string | Numero fattura, unique per anno |
| `Data` | string (date) | Data emissione |
| `Cod Cliente` | string | Lookup M_CLI_000, required |
| `CAUSALE CONTABILE` | string | Descrizione fattura |
| `Cod Esenzione iva` | string | Codice IVA ("22", "22R", "N6.6", etc.) |
| `Cod Pagamento` | string | Lookup Pagamenti Preventivo |

**Campi non scrivibili** (auto-calcolati):
- Totale Imponibile, Totale Iva, Totale
- Ragione Sociale (lookup da Cod Cliente)
- Indirizzo, Cap, Città (lookup anagrafica)
- NR REGISTRO (auto-increment)
- Tabella (hardcoded "FATTURA")

---

## 🛠️ Prossimi Step

### A) Riga di Vendita (priorità ALTA)

Opzioni da testare:
1. **Approccio PATCH**: Modificare un record Riga_Vendita ESISTENTE via PATCH (meno problematico che POST)
2. **Script FM**: Creare riga via script FileMaker richiamato dall'API (via GET con param script)
3. **Importazione XML**: Usare import Data API per mandare record batch se supportato
4. **Contatto FM**: Verificare se Righe_Vendita layout richiede setup speciale per API writes

### B) Ciclo Passivo (priorità MEDIA)

1. Verificare se Registro Acquisti è accessibile tramite layout in DADEGEST (non come database esterno)
2. Alternativa: Registrare passivi via A_FAT_000 + tabella intermedia
3. Se "Fatture acq" richiede login separato, aggiungere credenziali specifiche in .env

### C) Documenta

Salvare in filemaker.md:
- Procedura completa con campo obbligatorio vs optional
- Errori conosciuti e workaround
- Script di esempio per full workflow (login → create fattura → create righe)

---

## 💡 Osservazioni

1. **FM Data API v2** è REST-based e ha limitazioni rispetto all'UI di FileMaker (ad es. portali readonly)
2. **Field protection** in layout FM può bloccare API writes anche se non protetti in UI
3. **Multi-file system** di FM: DADEGEST è master, ma accesso a file esterni potrebbe richiedere setup diverso
4. **Token scope**: Un login su DADEGEST non necessariamente copre tutti i database collegati

---

**Contesto**: Testing per implementare automated invoice registration system  
**Data**: 2026-06-11  
**Esito**: Parziale — Ciclo attivo testata funziona, blocchi su righe e ciclo passivo  
