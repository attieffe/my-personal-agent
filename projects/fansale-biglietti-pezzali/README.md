# FanSale Max Pezzali Milano - Biglietti Tracker

**Obiettivo:** Cercare biglietti di Max Pezzali a Milano su FanSale, escludendo pacchetti, ogni 30 minuti.  
**Criterio:** Biglietti disponibili con Quantità >1 in posti numerati (no Parterre).  
**Deliverable:** Report via Telegram con DATA EVENTO + posti disponibili.

---

## Flusso da Implementare

### Fase 1: Esplorazione (Adesso)
- [ ] Esplorare il sito con `undetected-chromedriver` per mappare:
  - Struttura HTML dei biglietti
  - Selettori CSS/XPath per filtrare "BIGLIETTI" vs "PACCHETTI"
  - Comportamento del pulsante "VISUALIZZA"
  - Dati disponibili nella pagina di dettaglio (quantità, tipo posto, data evento)

**Risultati esplorazione:** `EXPLORATION.md` (selettori, flusso, accorgimenti)

### Fase 2: Automazione Ricorrente
- [ ] Script `fansale_collector.py` che:
  1. Apre il sito con `undetected-chromedriver`
  2. Filtra biglietti Milano (esclude PACCHETTI)
  3. Per ogni biglietto, clicca "VISUALIZZA"
  4. Estrae: DATA_EVENTO, QUANTITÀ, TIPO_POSTO, PREZZO
  5. Filtra quelli con QTÀ>1 e posto NUMERATO
  6. Salva in JSON con timestamp

**Output:** `_logs/scan_YYYYMMDD_HHMMSS.json`

### Fase 3: Monitoraggio Ricorrente
- [ ] Cron job (ogni 30 min) che:
  - Esegue `fansale_collector.py`
  - Legge log precedente
  - Confronta: quali biglietti sono NUOVI o CAMBIATI
  - Invia report Telegram (non spam: solo differenze rilevanti)
  - Log: `_logs/changes_YYYYMMDD.md`

### Fase 4: Gestione Banner/WAF
- [ ] Documentare accorgimenti per:
  - Chiudere banner che appaiono dinamicamente
  - Retry se Cloudflare blocca
  - Delay tra click per evitare trigger bot check

---

## File da Creare

```
projects/fansale-biglietti-pezzali/
├── README.md (questo)
├── EXPLORATION.md (risultati mappatura sito)
├── _system/
│   ├── fansale_collector.py (script automazione)
│   └── send_report.py (notifica Telegram)
├── _logs/
│   ├── scan_YYYYMMDD_HHMMSS.json (scan raw)
│   └── changes_YYYYMMDD.md (differenze giornaliere)
└── cron_setup.md (configurazione job ricorrente)
```

---

## Note Tecniche

- **Bot Detection:** Sito usa Cloudflare WAF → usare `undetected-chromedriver`
- **Rate Limiting:** Delay >2s tra click per evitare blocchi
- **Banner:** Monitorare e chiudere dinamicamente se appare overlay
- **Persitenza:** Salvare HTML raw per debug, JSON per dati strutturati

---

**Status:** In esplorazione - step 1  
**Ultima modifica:** 2026-08-19 16:45
