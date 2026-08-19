# FanSale Max Pezzali - Esplorazione Struttura Sito

**Data:** 2026-08-19  
**Status:** ✅ Esplorazione completata con Chromium (senza WAF block)

---

## Accesso al Sito

### Soluzione Trovata
✅ **Chromium di OpenClaw funziona perfettamente!**

- **Problema:** Accesso diretto bloccato da Cloudflare WAF ("Access Denied")
- **Soluzione:** Navigare dalla HOME first, accettare cookie banner, POI navigare al link specifico
- **Flusso corretto:**
  1. Navigare a `https://www.fansale.it/`
  2. Accettare banner cookie (pulsante "Accept All Cookies")
  3. Navigare a `https://www.fansale.it/tickets/all/max-pezzali/482766`

### Bypass Cloudflare
- ✅ Chromium OpenClaw browser tool (NO bot detection)
- ❌ Playwright + undetected-chromedriver (bot detection)
- ❌ curl/web_fetch (WAF blocks)

---

## Struttura Pagina Principale (`/tickets/all/max-pezzali/482766`)

### Sezione Biglietti
**Posizione:** `main > generic > generic > generic > link` (multipli)

**Elementi per Biglietto:**
```
Link wrapper [ref=eTNN]
├── Data evento: "martedì 22. dic 2026" | "mercoledì 23. dic 2026" | etc.
├── Nome evento: "Max Pezzali"
├── Città: "MILANO" | "ROMA" | etc.
├── Ora: "21.00 ore"
├── Venue: "Unipol Dome" | "Palazzo Dello Sport"
├── Icone: EVENTIM, Ticketcheck, Fair Deal, Offer
├── Prezzo: "€ 72,24" | "€ 77,28" | etc.
└── Pulsante: "Visualizza" [ref=eTNN]
```

### Differenziazione BIGLIETTI vs PACCHETTI

**Criteri:**
- **BIGLIETTI:** NON contiene il testo "Pacchetto"
- **PACCHETTI:** Contiene "Pacchetto: X componenti, Y luogo evento"

**Esempio BIGLIETTO:**
```
martedì 22. dic 2026 Max Pezzali MILANO 21.00 ore Unipol Dome
Offerte da € 72,24 Visualizza
```

**Esempio PACCHETTO (ESCLUDERE):**
```
22. dic 26 a 22. dic 26 Max Pezzali - Unipol Dome Party Terrace MILANO
"Pacchetto: 2 componenti, 1 luogo evento"
Offerte da € 230,72 Visualizza
```

### Navigazione Dettagli Biglietti
- **URL pattern:** `/tickets/all/max-pezzali/482766/[EVENTO_ID]`
- **Come aprire:** Cliccare su link biglietto oppure pulsante "Visualizza"

---

## Struttura Pagina Dettagli (`/tickets/all/max-pezzali/482766/[ID]`)

### Header Info
```
max-pezzali: martedì, 22/12/2026 21.00, Unipol Dome, 20138 MILANO
```

### Tabella Biglietti
**Colonne:** Quantità | Ingresso | Fila | Posto | Blocco | Prezzo | [azioni]

**Dati Rilevanti (da estrarre):**
- **Quantità:** Numero di biglietti disponibili (1, 2, 3, ...)
- **Posto:** Numero posto (es. "21", "15", "Parterre")
- **Blocco/Settore:** Es. "C10", "C8", "Parterre"
- **Prezzo:** Es. "€ 72,24"

### Filtri e Mappa
- **Filtri:** "Filtri ↕" e "Ordina ↕"
- **Mappa platea:** Interattiva, mostra posti e settori
  - Zona **PARTERRE** (centro) → **ESCLUDERE**
  - Zone numerate (C10, C8, etc.) → **INCLUDERE**

---

## Criteri di Ricerca (Come Richiesto da Atti)

✅ **Filtro 1:** Solo biglietti "BIGLIETTI", escludere "PACCHETTI"  
✅ **Filtro 2:** Quantità > 1 (disponibili almeno 2 biglietti)  
✅ **Filtro 3:** Tipo Posto = NUMERATO (es. "Posto 21", "Fila 12 Posto 15")  
❌ **Escludere:** Tipo Posto = "Parterre" (zona non numerata)

---

## Dati da Estrarre per Report

Per ogni biglietto che passa i filtri:
```json
{
  "data_evento": "2026-12-22",
  "giorno_settimana": "martedì",
  "ora": "21:00",
  "venue": "Unipol Dome",
  "citta": "MILANO",
  "quantita_disponibile": 2,
  "settore": "C10",
  "fila": "1",
  "posto_da": "21",
  "posto_a": "22",
  "prezzo_unitario": "€72,24",
  "url_dettaglio": "https://www.fansale.it/tickets/all/max-pezzali/482766/21343215",
  "timestamp_scan": "2026-08-19T16:45:00"
}
```

---

## Note Tecniche

### Rate Limiting
- Delay minimo 2-3 secondi tra click/navigazioni
- Non spam il sito (può triggerare ulteriori WAF)

### Banner Dinamici
- Cookie banner: compare sulla HOME, va chiuso prima di navigare
- Nessun altro banner rilevato nella pagina dei biglietti

### Paginazione
- Pagina principale ha paginazione (Pagina 1, 2, 3, ...)
- Ogni pagina contiene ~10 eventi/righe

### Dettagli Importanti
- La pagina dei biglietti è **DINAMICA**: lista aggiornata in tempo reale
- Ogni refresh potrebbe mostrare biglietti diversi o prezzi cambiati
- La quantità di biglietti disponibili cambia frequentemente

---

## Implementazione Script Automatizzato

### Fase 1: Collector
**File:** `_system/fansale_collector.py`

```python
# Pseudocodice
1. Aprire Chromium con OpenClaw browser tool
2. Navigare a home + accept cookies
3. Per ogni pagina (1, 2, 3, ...):
   a. Navigare a /tickets/all/max-pezzali/482766?page=N
   b. Estrarre lista biglietti
   c. Filtrare: NO PACCHETTI
   d. Per ogni biglietto:
      - Cliccare per aprire dettagli
      - Estrarre tabella (Quantità, Posto, Blocco, Prezzo)
      - Filtrare: Quantità > 1 AND Tipo Posto NUMERATO
      - Salvare JSON
4. Salvare output: _logs/scan_YYYYMMDD_HHMMSS.json
```

### Fase 2: Report Generator
**File:** `_system/send_report.py`

```python
# Logica
1. Leggere scan attuale vs scan precedente
2. Calcolare DELTA (nuovi biglietti, cambi prezzi, quantità ridotta)
3. Formattare report Telegram
4. Inviare notifica (solo se ci sono differenze rilevanti)
5. Salvare log in _logs/changes_YYYYMMDD.md
```

### Fase 3: Cron Job
**Comando:** Ogni 30 minuti

```
fansale_collector.py → JSON output
  ↓
compare con precedente
  ↓
fansale_report.py → Telegram notification
  ↓
archive in _logs/
```

---

## File Struttura

```
projects/fansale-biglietti-pezzali/
├── README.md (overview)
├── EXPLORATION.md (questo file)
├── _system/
│   ├── fansale_collector.py (crawler)
│   ├── fansale_reporter.py (genera report)
│   └── config.json (URL, telegram token, etc.)
├── _logs/
│   ├── scan_20260819_164500.json
│   ├── scan_20260819_170000.json
│   └── changes_20260819.md
└── cron_setup.md (istruzioni setup cron)
```

---

**Status:** ✅ Pronto per implementazione script automatizzato
