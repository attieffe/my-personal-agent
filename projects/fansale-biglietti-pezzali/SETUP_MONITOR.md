# Setup Monitor Automatico - FanSale Max Pezzali

## ✅ Cosa ho configurato

1. **Script monitor** (`_system/monitor.py`)
   - Controlla tutte e 7 le date Milano ogni 30 minuti
   - Filtra: Quantità ≥2, posti numerati (no Parterre, no "Posto Unico")
   - **🔴 ALERT SPECIALE per BLOCCO B** (notifica con grande risalto)
   - Salva risultati in `_logs/monitor_YYYYMMDD_HHMMSS.json`

2. **Cron job OpenClaw**
   - Esegue automaticamente ogni 30 minuti
   - ID job: `4865a61f-65a4-4d1f-96e5-4a7b5b3f4b67`
   - Stato: **ATTIVO** ✅

---

## 🔧 Setup richiesto (da fare UNA VOLTA)

### 1. Configura Telegram

Il file `_system/config.json` ha già i placeholder. Devi solo aggiornare:

```json
{
  "telegram": {
    "enabled": true,
    "chat_id": "TUO_CHAT_ID_QUI",    ← inserisci qui il tuo chat_id
    "token": "TUO_BOT_TOKEN_QUI",     ← inserisci qui il token del bot
    "topic_id": 1125                   ← già configurato
  }
}
```

**Come trovare chat_id e token:**
- Se hai già un bot Telegram, usa quello
- Altrimenti segui la guida in `CRON_SETUP.md` (sezione "Step 1: Configurare Telegram")

### 2. Aggiorna il cron job con il tuo chat_id

Dopo aver configurato Telegram, esegui:

```bash
# Modifica il cron job per usare il tuo chat_id
openclaw cron update 4865a61f-65a4-4d1f-96e5-4a7b5b3f4b67 \
  --delivery.to "TUO_CHAT_ID_QUI"
```

Oppure usa il comando OpenClaw:
```
/cron update 4865a61f --delivery.to <tuo-chat-id>
```

---

## 📋 Come funziona

### Controlli automatici
Ogni 30 minuti lo script:
1. **Aggiornamento lista eventi** (dalla pagina principale)
   - Controlla https://www.fansale.it/tickets/all/max-pezzali/482766
   - Cerca nuovi eventi MILANO (esclude pacchetti)
   - Aggiorna `_system/eventi_list.json` se trova novità
   - Se il sito blocca → usa la lista esistente
2. **Scansione date**
   - Apre Chromium in modalità headless
   - Visita tutte le date nella lista aggiornata
   - Estrae i biglietti disponibili
3. **Filtri**
   - Quantità ≥2 e posti numerati
   - Esclude: Parterre, "Posto Unico", pacchetti
4. **Salvataggio**
   - Risultati in `_logs/monitor_YYYYMMDD_HHMMSS.json`
   - Lista eventi in `_system/eventi_list.json`

### Notifiche Telegram

Ogni notifica include:
- ✅/ℹ️ Status aggiornamento lista eventi
- 🕐 Timestamp ultimo aggiornamento
- 🔴 ALERT speciale se BLOCCO B trovato
- 📋 Altri blocchi disponibili
- ❌ Info se nessun biglietto trovato

**Esempio con BLOCCO B trovato:**
```
🎫 BIGLIETTI MAX PEZZALI DISPONIBILI

✅ Lista eventi aggiornata
🕐 Ultimo aggiornamento: 2026-08-19T17:30:00

---

🔴🔴🔴 BLOCCO B TROVATO! 🔴🔴🔴

📅 Sabato 2026-12-26
🎯 Ingresso 4 | Fila 18 | Posto 27, 28 | Blocco B10
💰 € 132,16
🔗 https://www.fansale.it/tickets/all/max-pezzali/482766/21343715

---

📋 Altri blocchi disponibili:

📅 Mercoledì 2026-12-30
🎯 Ingresso 4 | Fila 1 | Posto 1, 4 | Blocco C4
💰 € 144,48
```

**Esempio senza biglietti:**
```
🎫 BIGLIETTI MAX PEZZALI DISPONIBILI

ℹ️ Lista eventi invariata
🕐 Ultimo aggiornamento: 2026-08-19T17:30:00

---

❌ Nessun biglietto trovato con Quantità ≥2 in posti numerati
📊 Eventi monitorati: 7
```

---

## 🛠️ Comandi utili

### Controllo manuale (test immediato)
```bash
cd /home/openclaw/.openclaw/workspace/projects/fansale-biglietti-pezzali
python3 _system/monitor.py
```

### Gestione cron job
```bash
# Stato del job
openclaw cron list --job-id 4865a61f

# Disabilita temporaneamente
openclaw cron update 4865a61f --enabled false

# Riabilita
openclaw cron update 4865a61f --enabled true

# Forza esecuzione immediata
openclaw cron run 4865a61f
```

### Log delle esecuzioni
```bash
# Ultimi risultati
ls -lt _logs/monitor_*.json | head -5

# Leggi ultimo risultato
cat _logs/monitor_*.json | tail -1 | jq .
```

---

## 🎯 Date monitorate

1. **Martedì 22 dicembre 2026** (ID: 21343215)
2. **Mercoledì 23 dicembre 2026** (ID: 21343717)
3. **Sabato 26 dicembre 2026** (ID: 21343715) ⭐
4. **Domenica 27 dicembre 2026** (ID: 21343722)
5. **Martedì 29 dicembre 2026** (ID: 21343718)
6. **Mercoledì 30 dicembre 2026** (ID: 21343719) ⭐⭐
7. **Domenica 3 gennaio 2027** (ID: 21928067)

---

## ⚠️ Note importanti

- **BLOCCO B**: Lo script darà notifica con grande risalto solo per biglietti nel blocco B
- **Posti numerati**: Esclude automaticamente Parterre e "Posto Unico"
- **Quantità minima**: Cerca solo biglietti con almeno 2 posti disponibili
- **Frequenza**: Ogni 30 minuti (1800000 ms)

---

## ✅ Status attuale

- ✅ Script monitor pronto
- ✅ Cron job creato e attivo
- ⏳ **DA FARE:** Configurare token e chat_id Telegram in `_system/config.json`
- ⏳ **DA FARE:** Aggiornare delivery del cron job con il tuo chat_id

**Prossimo step:** Configura Telegram e testa con `python3 _system/monitor.py`
