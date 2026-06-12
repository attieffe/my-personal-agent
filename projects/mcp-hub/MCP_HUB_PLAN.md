# MCP Hub — Piano Sviluppo

Documento di architettura e procedure per sviluppo spoke MCP.

**Data:** 2026-06-12  
**Infrastruttura:** Node.js + PM2 (localhost:9000) proxied da Nginx `attibot.ingeniosolution.it/mcp-hub/`

---

## 🎯 Obiettivi

1. **Consolidare operazioni dati** come procedure MCP (non script ad hoc)
2. **Fortificare logica** con validazioni built-in
3. **Ridurre token** AI (query routing → MCP, non reasoning)
4. **Estendere facilmente** (spoke modulari)

---

## 📋 Spoke Prioritarie

**Riepilogo procedure:**
- **mio-tesoro:** 4 procedure (search_registrazioni, search_conti, insert_conti, insert_registrazione)
- **Ingenio:** 11 procedure (preventivi, DDT, fatture vendita, fatture acquisto, registro acquisti, anagrafiche)
- **Colzani:** proxy esterno

---

### 1️⃣ mio-tesoro (Priorità: ALTA)

**Fonte:** Google Sheets PERSONALE + CASA  
**Responsabile:** IAcopo (AI) esecuzione + MCP Developer Agent (sviluppo)  
**Procedure:** 4

#### Procedure Obbligatorie

##### A. `search_registrazioni` 
Ricerca registrazioni per testo, categoria, conto, note, importo.

**Input:**
```json
{
  "sheet_name": "PERSONALE|CASA",
  "search_type": "text|category|account|note|amount",
  "query": "string|array",
  "date_range": {"from": "YYYY-MM-DD", "to": "YYYY-MM-DD"}
}
```

**Output:**
```json
{
  "results": [
    {
      "row_id": "N",
      "date": "YYYY-MM-DD",
      "account": "conto_xx",
      "category": "Categoria",
      "amount": 100.00,
      "description": "testo"
    }
  ],
  "total_rows": 10,
  "confidence": 0.95
}
```

**Validazioni:**
- ✅ Sheet esiste (PERSONALE ≠ CASA, schema diverso)
- ✅ Query non vuota
- ✅ Date logiche (from ≤ to)

---

##### B. `search_conti`
Ricerca conti nel piano dei conti.

**Input:**
```json
{
  "sheet_name": "PERSONALE|CASA",
  "query": "nome_conto|codice",
  "filter_type": "attivo|all"
}
```

**Output:**
```json
{
  "results": [
    {
      "code": "1.01.001",
      "name": "Conto Corrente",
      "type": "Asset",
      "balance": 5000.00
    }
  ]
}
```

**Validazioni:**
- ✅ Query non vuota
- ✅ Sheet valido

---

##### C. `insert_conti` ⭐ FORTIFACATA
Inserimento nuovo conto nel piano dei conti.

**Input:**
```json
{
  "sheet_name": "PERSONALE|CASA",
  "code": "1.02.001",
  "name": "Conto Deposito",
  "type": "Asset|Liability|Equity|Income|Expense",
  "parent_code": "1.02",
  "notes": "optional"
}
```

**Validazioni (OBBLIGATORIE):**
1. ✅ **Code univoco:** non esiste già il codice nel sheet
2. ✅ **Name non vuoto:** lunghezza 3-100 char
3. ✅ **Type valido:** uno tra i 5 tipi contabili
4. ✅ **Parent esiste:** parent_code deve esistere (se fornito)
5. ✅ **Struttura gerarchica:** il code deve seguire la gerarchia (es. 1.02.001 sotto 1.02)

**Output:**
```json
{
  "status": "success|error",
  "code": "1.02.001",
  "message": "Conto creato",
  "validation_details": {
    "code_unique": true,
    "hierarchy_valid": true
  }
}
```

---

##### D. `insert_registrazione` ⭐ FORTIFICATA
Inserimento registrazione con validazioni SEVERE.

**Input:**
```json
{
  "sheet_name": "PERSONALE|CASA",
  "date": "YYYY-MM-DD",
  "description": "string",
  "lines": [
    {"account": "1.01.001", "debit": 100, "credit": 0, "category": "Spese"},
    {"account": "2.01.001", "debit": 0, "credit": 100, "category": "Pagamenti"}
  ],
  "notes": "optional"
}
```

**Validazioni (OBBLIGATORIE):**
1. ✅ **Somma doppia:** Σ(debit) === Σ(credit) — se no, ERRORE
2. ✅ **Min 2 righe:** len(lines) >= 2
3. ✅ **Conti validi:** ogni account esiste in piano dei conti
4. ✅ **Date logiche:** date <= today
5. ✅ **Non duplicato:** no reg identica (stesso date+amount+account coppia)
6. ✅ **Formule propagate:** alla riga aggiunta, ricalcola balance conti

**Output:**
```json
{
  "status": "success|error",
  "row_id": "N",
  "message": "string",
  "validation_details": {
    "double_entry": true,
    "min_lines": true,
    "accounts_valid": true
  }
}
```

**Errore esempio:**
```json
{
  "status": "error",
  "code": "DEBIT_CREDIT_MISMATCH",
  "message": "Somma debito (200) ≠ somma credito (150). Differenza: 50",
  "validation_details": {
    "total_debit": 200,
    "total_credit": 150,
    "difference": 50
  }
}
```

---

### 2️⃣ Ingenio FileMaker (Priorità: ALTA)

**Fonte:** DADEGEST FileMaker 19.3.2  
**Host:** `ingenio.ddns.net:2296`  
**Responsabile:** MCP Developer Agent (sviluppo) + IAcopo (esecuzione)

#### Ciclo Attivo (VENDITE)

##### A. `search_preventivi`
Ricerca preventivi per cliente, data, stato.

**Input:**
```json
{
  "customer_code": "optional|string",
  "date_range": {"from": "MM/DD/YYYY", "to": "MM/DD/YYYY"},
  "status": "open|closed|all"
}
```

**Output:**
```json
{
  "results": [
    {
      "number": "PRE-2026-001",
      "customer": "TProject Group Srl",
      "date": "06/12/2026",
      "amount": 5000.00,
      "status": "open",
      "notes_preview": "Fornitura PC..."
    }
  ]
}
```

**Validazioni:**
- ✅ FM Server raggiungibile (try/catch con msg "FM non disponibile")
- ✅ Customer esiste (se fornito)
- ✅ Date in formato FM (MM/DD/YYYY)

---

##### B. `create_preventivo` ⭐ FORTIFICATA
Creazione nuovo preventivo con template NOTE e ciclo attivo.

**Input:**
```json
{
  "customer_code": "CLI-001",
  "date": "MM/DD/YYYY",
  "lines": [
    {
      "product_code": "PRD-001",
      "quantity": 1,
      "unit_price": 1000.00,
      "description": "PC Desktop configurato"
    }
  ],
  "template_type": "hardware|plugin|service|support",
  "notes_custom": "optional_text",
  "payment_code": "001",
  "email_subject": "Preventivo: descrizione breve"
}
```

**Validazioni (OBBLIGATORIE):**
1. ✅ **Cliente valido:** Cod Cliente esiste in M_CLI_000
2. ✅ **Data valida:** MM/DD/YYYY formato FM, <= today
3. ✅ **Prodotti validi:** ogni PRD-code esiste in M_ART_000 + Tipologia Articolo coerente
4. ✅ **Righe congruenti:** quantity > 0, unit_price > 0
5. ✅ **Template TYPE:** uno tra [hardware, plugin, service, support]
6. ✅ **IVA valida:** CodiceIva esiste in Iva (M_ART_000)
7. ✅ **Pagamento valido:** Cod Pagamento in [001-013]
8. ✅ **Email subject:** non vuoto, lunghezza 10-100 char

**Template NOTE Auto-Generate:**
- **hardware:** "Fornitura [N] componenti: [lista] | Tempo consegna: 14 giorni | Condizioni pagamento: [default]"
- **plugin:** "Sviluppo plugin WordPress... [attività] | Fatturazione: [default] | Tempi: [N] giorni"
- **service:** "Attività previste: [lista] | Modalità rilascio: PRODUZIONE | Tempi: [N] giorni"
- **support:** "Attività di [tipo]: [step 1,2,3] | [Condizioni]"

**Output:**
```json
{
  "status": "success|error",
  "preventivo_number": "PRE-2026-XXX",
  "fm_record_id": "12345",
  "message": "string"
}
```

---

##### C. `search_ddt`
Ricerca DDT (Documenti di Trasporto) per cliente, data, stato.

**Input:**
```json
{
  "customer_code": "optional|string",
  "date_range": {"from": "MM/DD/YYYY", "to": "MM/DD/YYYY"},
  "status": "open|closed|all"
}
```

**Output:** Lista DDT con numero, data, cliente, totale, stato.

---

##### D. `create_ddt` ⭐ FORTIFICATA
Creazione DDT da preventivo/ordine.

**Input:**
```json
{
  "customer_code": "CLI-001",
  "date": "MM/DD/YYYY",
  "transport_type": "Auto|Pallet|Corriere",
  "lines": [
    {"product_code": "PRD-001", "quantity": 1}
  ]
}
```

**Validazioni:**
- ✅ Cliente valido
- ✅ Data valida
- ✅ Prodotti validi
- ✅ Quantity <= giacenza disponibile (M_ART_000.Giacenza)

---

##### E. `search_fatture_vendita`
Ricerca fatture vendita con scadenzario.

**Input:**
```json
{
  "customer_code": "optional|string",
  "date_range": {"from": "MM/DD/YYYY", "to": "MM/DD/YYYY"},
  "status": "open|closed|all"
}
```

**Output:**
```json
{
  "results": [
    {
      "number": "FAT-2026-001",
      "customer": "TProject Group Srl",
      "date": "06/12/2026",
      "amount": 5000.00,
      "scadenze": [
        {"date": "07/12/2026", "amount": 2500.00, "paid": 2500.00, "remaining": 0},
        {"date": "08/12/2026", "amount": 2500.00, "paid": 0, "remaining": 2500.00}
      ],
      "total_remaining": 2500.00
    }
  ]
}
```

---

##### F. `create_fattura_vendita` ⭐ FORTIFICATA
Creazione fattura vendita da DDT/Ordine con gestione IVA e scadenzario.

**Input:**
```json
{
  "customer_code": "CLI-001",
  "date": "MM/DD/YYYY",
  "lines": [
    {
      "product_code": "PRD-001",
      "quantity": 1,
      "iva_code": "22"
    }
  ],
  "payment_code": "001",
  "scadenze": [
    {"date": "MM/DD/YYYY", "percentage": 50},
    {"date": "MM/DD/YYYY", "percentage": 50}
  ]
}
```

**Validazioni:**
1. ✅ Cliente valido
2. ✅ Prodotti validi + Tipologia Articolo coerente
3. ✅ **IVA valida:** CodiceIva esiste in Iva
4. ✅ **Scadenzario:** somma percentuali = 100%
5. ✅ **No reverse charge per vendite interne:** IVA != "22R" (reverse charge è su acquisti)
6. ✅ Pagamento valido

---

#### Ciclo Passivo (ACQUISTI)

##### G. `search_fatture_acquisto`
Ricerca fatture acquisto con reverse charge e natura IVA.

**Input:**
```json
{
  "supplier_code": "optional|string",
  "date_range": {"from": "MM/DD/YYYY", "to": "MM/DD/YYYY"},
  "filter_iva": "all|reverse_charge|esente|extra_ue"
}
```

**Output:**
```json
{
  "results": [
    {
      "number": "FAT-ACQ-2026-001",
      "supplier": "Fornitore SpA",
      "date": "06/12/2026",
      "amount": 5000.00,
      "iva_aliquota": 22,
      "natura_iva": "ordinaria",
      "reverse_charge": false
    }
  ]
}
```

---

##### H. `create_fattura_acquisto` ⭐ FORTIFICATA
Creazione fattura acquisto con reverse charge, extra UE, esente.

**Input:**
```json
{
  "supplier_code": "FOR-001",
  "date": "MM/DD/YYYY",
  "supplier_invoice_number": "FAT-001",
  "supplier_invoice_date": "MM/DD/YYYY",
  "lines": [
    {
      "product_code": "PRD-001",
      "quantity": 1,
      "unit_price": 1000.00,
      "iva_code": "22",
      "natura": "ordinaria|N4|N1|N2"
    }
  ],
  "categoria_spesa": "Servizi|Manutenzione|Hardware|Formazione"
}
```

**Validazioni:**
1. ✅ Fornitore valido (M_FOR_000)
2. ✅ Prodotti validi
3. ✅ **IVA + Natura coerente:**
   - `N4` (reverse charge interno) → IVA=0, mostra_iva_esente=1
   - `N1` (EXTRA UE) → IVA=0, mostra_iva_esente=1, fornitore.CodNazione != IT
   - `N2` (Esente) → IVA=0
   - ordinaria → IVA > 0
4. ✅ **Deducibilità:** calcola % DEDUCIBILITÀ (100% ordinaria, 40% esente, 20% mista)
5. ✅ **Categoria spesa:** valida e tracciata in Registro Acquisti

**Registro Acquisti (auto-generate):**
- Crea riga in `Registro Acquisti` con Nr Reg., Data, Data Reg., Fornitore, Nr Documento, Categoria, P.IVA, IVA, Imponibile, Valore IVA, %, DED, Natura

---

##### I. `search_registro_acquisti`
Ricerca nel Registro Acquisti per fornitori, natura IVA, deducibilità, categoria spesa.

**Input:**
```json
{
  "date_range": {"from": "MM/DD/YYYY", "to": "MM/DD/YYYY"},
  "filter_natura": "all|reverse_charge|esente|extra_ue|ordinaria",
  "filter_categoria": "all|Servizi|Manutenzione|Hardware|Formazione"
}
```

**Output:** Lista registrazioni di acquisto con riepilogo IVA per natura.

---

#### Anagrafiche

##### J. `search_articoli`
Ricerca articoli/prodotti con tipologia, famiglia, giacenza.

**Input:**
```json
{
  "query": "string",
  "tipologia_articolo": "optional",
  "famiglia": "optional",
  "filter_giacenza": "disponibile|esaurito|all"
}
```

**Output:**
```json
{
  "results": [
    {
      "code": "PRD-001",
      "description": "PC Desktop i7",
      "tipologia": "Hardware",
      "famiglia": "PC",
      "iva_code": "22",
      "prezzo_costo": 800.00,
      "prezzo_vendita": 1000.00,
      "giacenza": 5,
      "in_ordine": 2,
      "resa": 0
    }
  ]
}
```

---

##### K. `search_clienti`
Ricerca clienti per nome, codice, email.

**Input:**
```json
{
  "query": "string",
  "query_type": "name|code|email|all"
}
```

**Output:** Cliente con anagrafica completa, fatturazione elettronica, agente commerciale.

---

##### L. `search_iva`
Ricerca codici IVA con aliquota e natura.

**Input:**
```json
{
  "query": "optional",
  "filter": "all|ordinaria|reverse_charge|esente|extra_ue"
}
```

**Output:**
```json
{
  "results": [
    {
      "code": "22",
      "description": "IVA 22%",
      "aliquota": 22,
      "natura": "ordinaria"
    },
    {
      "code": "22R",
      "description": "Reverse Charge 22%",
      "aliquota": 22,
      "natura": "N4"
    }
  ]
}
```

---

### 3️⃣ Colzani MCP (Esterno)

**Fonte:** MCP server esterno (già configurato)  
**Responsabile:** IAcopo (esecuzione)

#### Procedure Disponibili

Proxy verso MCP esterno:
- `query_as400` 
- `query_mysql`
- `query_nav`
- `query_wms`

(No sviluppo interno, solo passthrough)

---

## 🏗️ Architettura Hub

### Directory Structure

```
/home/openclaw/mcp-hub/
├── package.json
├── ecosystem.config.js        # PM2 config
├── .env                        # credenziali (no git)
├── src/
│   ├── hub.js                 # Express server + routing
│   ├── spokes/
│   │   ├── miotesoro.js       # Procedure A,B,C,D (4 procedure)
│   │   ├── ingenio.js         # Procedure A-L (11 procedure)
│   │   └── colzani.js         # Proxy esterno (2-3 procedure)
│   └── middleware/
│       ├── auth.js            # Bearer token (opzionale fase 2)
│       ├── validation.js      # Schema validation
│       ├── errorHandler.js    # Error normalization
│       └── fm-error-handler.js # FileMaker-specific error handling
├── config/
│   ├── miotesoro-spoke.yml    # Schema + auth
│   ├── ingenio-spoke.yml      # Schema + auth + IVA rules
│   └── colzani-spoke.yml      # External endpoint
├── docs/
│   ├── PROCEDURES.md          # Lista completa procedure con signature
│   └── VALIDATION_RULES.md    # Regole di validazione by spoke
└── __tests__/
    ├── miotesoro.test.js
    ├── ingenio.test.js
    └── integration/
```

### API Endpoint (unified)

```
POST /query
{
  "spoke": "miotesoro|ingenio|colzani",
  "procedure": "search_registrazioni|search_preventivi|...",
  "params": {...}
}

Response:
{
  "status": "success|error",
  "data": {...},
  "timestamp": "ISO8601",
  "execution_time_ms": 150
}
```

### Nginx Config

```nginx
location /mcp-hub/ {
    proxy_pass http://localhost:9000/;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_connect_timeout 10s;
    proxy_read_timeout 30s;
}
```

---

## 📊 Fasi di Sviluppo

### Fase 0: Planning + Setup Base (MCP Dev Agent)
- [ ] Create directory + package.json
- [ ] Express server + PM2 config
- [ ] Nginx config + reverse proxy
- [ ] Error handler middleware
- [ ] FM-specific error handler (try/catch raggiungibilità, timeout, auth)
- [ ] Logging centralizzato

**Timeline:** 1-1.5 gg  
**Owner:** MCP Developer Agent

### Fase 1: Spoke mio-tesoro (MCP Dev Agent)
- [ ] Implement `search_registrazioni`
- [ ] Implement `search_conti`
- [ ] Implement `insert_conti` + validazione gerarchica
- [ ] Implement `insert_registrazione` + validazioni severe (somma=0, ≥2 righe, formule)
- [ ] Test con dati veri (Google Sheets PERSONALE + CASA)
- [ ] Documentation + schema YAML

**Timeline:** 2-3 gg  
**Owner:** MCP Developer Agent  
**Validazione:** Atti

### Fase 2a: Spoke Ingenio — Ciclo Attivo (MCP Dev Agent)
- [ ] Implement `search_preventivi`
- [ ] Implement `create_preventivo` + template NOTE per 4 categorie + validazioni IVA
- [ ] Implement `search_ddt` + `create_ddt` + validazione giacenza
- [ ] Implement `search_fatture_vendita` + scadenzario
- [ ] Implement `create_fattura_vendita` + scadenzario + IVA
- [ ] Test con dati veri (FM DADEGEST ciclo attivo)
- [ ] Documentation

**Timeline:** 3-4 gg  
**Owner:** MCP Developer Agent  
**Validazione:** Atti

### Fase 2b: Spoke Ingenio — Ciclo Passivo + Anagrafiche (MCP Dev Agent)
- [ ] Implement `search_fatture_acquisto` + filtri natura IVA
- [ ] Implement `create_fattura_acquisto` + **reverse charge (N4), extra UE (N1), esente (N2)**
- [ ] Implement `search_registro_acquisti` + riepilogo IVA per natura
- [ ] Implement `search_articoli` + `search_clienti` + `search_iva`
- [ ] **Validation rules:** deducibilità IVA, natura coerente, reverse charge interno
- [ ] Test con dati veri (FM DADEGEST ciclo passivo)
- [ ] Documentation + VALIDATION_RULES.md

**Timeline:** 3-4 gg  
**Owner:** MCP Developer Agent  
**Validazione:** Atti

### Fase 3: Spoke Colzani (MCP Dev Agent)
- [ ] Setup proxy verso MCP esterno (già configurato)
- [ ] Test routing + error handling

**Timeline:** 0.5 gg  
**Owner:** MCP Developer Agent

### Fase 4: Integration + Memory (Io + Atti)
- [ ] Update MEMORY.md con MCP discovery
- [ ] Crea `projects/mcp-hub/MCP_TOOLS.md` per schema ogni spoke
- [ ] Crea `projects/mcp-hub/PROCEDURES.md` con lista signature complete
- [ ] Test operativo (Io chiamo mcp_hub__query...)
- [ ] Monitoring + healthcheck
- [ ] Performance audit (response time per procedure)

**Timeline:** 1-1.5 gg  
**Owner:** IAcopo (Io)

---

## ✅ Definition of Done (DDD)

### Per ogni procedure:
- [ ] Implementazione completa
- [ ] Tutte le validazioni in place (con dettagli in VALIDATION_RULES.md)
- [ ] Test con dati reali (no mock, nessun test su dati fake)
- [ ] Error handling + messaggi chiari per ogni codice errore
- [ ] Response schema con status, data, timestamp, execution_time_ms
- [ ] Documentazione nel PROCEDURES.md

### Per spoke mio-tesoro (specifico):
- [ ] Somma doppia validazione (debit === credit)
- [ ] Min 2 righe obbligatorio
- [ ] Conti validi in piano dei conti
- [ ] No duplicati (stesso date+amount+account)
- [ ] Formule propagate al ricalcolo balance
- [ ] Insert conti con gerarchia corretta

### Per spoke Ingenio (specifico):
- [ ] IVA rules:
  - Codici validi (22, 22R, 10, 0, NI*, ESC*, ecc.)
  - Reverse charge (N4) = IVA 0 + mostra_iva_esente=1
  - Extra UE (N1) = IVA 0 + fornitore.CodNazione != IT
  - Esente (N2) = IVA 0
  - Ordinaria = IVA > 0
- [ ] Deducibilità % calcolata (100% ordinaria, 40% esente, 20% mista)
- [ ] Scadenzario fatture (somma % = 100%)
- [ ] Giacenza validazione (QTA <= Giacenza)
- [ ] Template NOTE auto-generati per 4 categorie (hardware, plugin, service, support)
- [ ] Test con dati veri FM (preventivi, DDT, fatture, fatture acquisto)

### Per Hub:
- [ ] Nginx config funzionante (test con curl)
- [ ] PM2 setup + auto-restart + logs in /var/log/pm2/
- [ ] Healthcheck endpoint: `GET /health` → JSON con status spoke
- [ ] Logging centralizzato (JSON format, timestamps ISO8601)
- [ ] Zero downtime su updates (spoke reload, no PM2 restart necessario)
- [ ] TLS bypass per FM (NODE_TLS_REJECT_UNAUTHORIZED=0 in .env)

---

## 🚀 Next Step

**Atti:** Confermi priorità spoke? (mio-tesoro first, poi Ingenio, poi Colzani proxy)

**MCP Developer Agent:** Ready a partire?
