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

### 1️⃣ mio-tesoro (Priorità: ALTA)

**Fonte:** Google Sheets PERSONALE + CASA  
**Responsabile:** IAcopo (AI) esecuzione + MCP Developer Agent (sviluppo)

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

##### C. `insert_registrazione` ⭐ FORTIFICATA
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

#### Procedure Obbligatorie

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

##### B. `search_clienti`
Ricerca clienti per nome, codice, tipo.

**Input:**
```json
{
  "query": "string",
  "query_type": "name|code|all"
}
```

**Output:**
```json
{
  "results": [
    {
      "code": "CLI-001",
      "name": "TProject Group Srl",
      "type": "Azienda",
      "contact": "Mario Maglie",
      "email": "mario@tproject.it"
    }
  ]
}
```

**Validazioni:**
- ✅ Query non vuota
- ✅ FM Server raggiungibile

---

##### C. `create_preventivo` ⭐ FORTIFICATA
Creazione nuovo preventivo con template NOTE.

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
3. ✅ **Prodotti validi:** ogni PRD-code esiste in M_ART_000
4. ✅ **Righe congruenti:** quantity > 0, unit_price > 0
5. ✅ **Template TYPE:** uno tra [hardware, plugin, service, support]
6. ✅ **Note Documento:** auto-generate da template + custom text (se fornito)
7. ✅ **Pagamento valido:** Cod Pagamento in [001-013]
8. ✅ **Email subject:** non vuoto, lunghezza 10-100 char

**Template NOTE Auto-Generate (semplificato):**
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
  "message": "string",
  "validation_details": {
    "customer_valid": true,
    "date_valid": true,
    "products_valid": true,
    "template_applied": "hardware"
  }
}
```

**Errore esempio:**
```json
{
  "status": "error",
  "code": "INVALID_CUSTOMER",
  "message": "Cliente CLI-999 non trovato in M_CLI_000"
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
│   │   ├── miotesoro.js       # Procedure A,B,C
│   │   ├── ingenio.js         # Procedure A,B,C
│   │   └── colzani.js         # Proxy esterno
│   └── middleware/
│       ├── auth.js            # Bearer token (opzionale fase 2)
│       ├── validation.js      # Schema validation
│       └── errorHandler.js    # Error normalization
├── config/
│   ├── miotesoro-spoke.yml    # Schema + auth
│   ├── ingenio-spoke.yml      # Schema + auth
│   └── colzani-spoke.yml      # External endpoint
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

### Fase 1: Setup Hub Base (MCP Dev Agent)
- [ ] Create directory + package.json
- [ ] Express server + PM2 config
- [ ] Nginx config
- [ ] Error handler middleware

**Timeline:** 1 gg  
**Owner:** MCP Developer Agent

### Fase 2: Spoke mio-tesoro (MCP Dev Agent)
- [ ] Implement `search_registrazioni`
- [ ] Implement `search_conti`
- [ ] Implement `insert_registrazione` + validazioni
- [ ] Test con dati veri (Google Sheets PERSONALE)
- [ ] Documentation

**Timeline:** 2-3 gg  
**Owner:** MCP Developer Agent  
**Validazione:** Atti

### Fase 3: Spoke Ingenio (MCP Dev Agent)
- [ ] Implement `search_preventivi`
- [ ] Implement `search_clienti`
- [ ] Implement `create_preventivo` + validazioni + template
- [ ] Test con dati veri (FM DADEGEST)
- [ ] Documentation

**Timeline:** 2-3 gg  
**Owner:** MCP Developer Agent  
**Validazione:** Atti

### Fase 4: Spoke Colzani (MCP Dev Agent)
- [ ] Setup proxy verso MCP esterno
- [ ] Test routing

**Timeline:** 0.5 gg  
**Owner:** MCP Developer Agent

### Fase 5: Integration + Memory (Io + Atti)
- [ ] Update MEMORY.md con MCP discovery
- [ ] Crea `projects/mcp-hub/MCP_TOOLS.md` per schema ogni spoke
- [ ] Test operativo (Io chiamo mcp_hub__query...)
- [ ] Monitoring + healthcheck

**Timeline:** 1 gg  
**Owner:** IAcopo (Io)

---

## ✅ Definition of Done (DDD)

### Per ogni spoke:
- [ ] Tutte le procedure implementate
- [ ] Tutte le validazioni in place
- [ ] Test con dati reali (no mock)
- [ ] Error handling + messaggi chiari
- [ ] Schema YAML aggiornato
- [ ] Documentazione MD con esempi

### Per Hub:
- [ ] Nginx config funzionante
- [ ] PM2 setup + auto-restart
- [ ] Healthcheck endpoint
- [ ] Logging centralizzato
- [ ] Zero downtime su updates (spoke reload)

---

## 🚀 Next Step

**Atti:** Confermi priorità spoke? (mio-tesoro first, poi Ingenio, poi Colzani proxy)

**MCP Developer Agent:** Ready a partire?
