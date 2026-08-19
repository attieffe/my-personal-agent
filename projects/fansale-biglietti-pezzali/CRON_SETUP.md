# Setup Cron Job - FanSale Collector

**Obiettivo:** Eseguire il collector ogni 30 minuti per monitorare biglietti Max Pezzali.

---

## Step 1: Configurare Telegram (OBBLIGATORIO)

Devi creare un bot Telegram per ricevere le notifiche:

1. **Apri Telegram** e cerca **@BotFather**
2. **Crea nuovo bot:** `/newbot`
   - Nome: "FanSale Biglietti" (o quello che vuoi)
   - Username: "fansale_pezzali_bot" (DEVE terminare in _bot)
3. **Copia il TOKEN** (es: `123456:ABCdef...`)
4. **Trova il tuo CHAT_ID:**
   - Scrivi un messaggio al bot che hai appena creato
   - Visita: `https://api.telegram.org/botTOKEN/getUpdates`
   - Sostituisci TOKEN con quello ricevuto
   - Cerca `"chat":{"id":XXXXXXXXX}` — copia quel numero

5. **Aggiorna `_system/config.json`:**
   ```json
   {
     "telegram": {
       "token": "TUO_BOT_TOKEN_QUI",
       "chat_id": "TUO_CHAT_ID_QUI"
     }
   }
   ```

---

## Step 2: Test Locale

Verifica che lo script funzioni:

```bash
cd /home/openclaw/.openclaw/workspace/projects/fansale-biglietti-pezzali

# Esegui il collector manualmente
python3 _system/fansale_collector.py

# Controlla l'output
ls -lh _logs/scan_*.json
cat _logs/scan_LATEST.json | head -50
```

**Output atteso:**
- File JSON salvato in `_logs/scan_YYYYMMDD_HHMMSS.json`
- Messaggio su Telegram (se config OK)

---

## Step 3: Setup Cron Job

### Opzione A: OpenClaw Cron (CONSIGLIATO)

Usa il cron di OpenClaw per eseguire ogni 30 minuti:

```bash
# Comando da eseguire in OpenClaw
/schedule \
  --name "FanSale Biglietti Collector" \
  --interval "every 30 minutes" \
  --command "python3 /home/openclaw/.openclaw/workspace/projects/fansale-biglietti-pezzali/_system/fansale_collector.py"
```

### Opzione B: System Crontab

Se preferisci crontab di sistema:

```bash
# Apri crontab editor
crontab -e

# Aggiungi questa riga (esegui ogni 30 minuti)
*/30 * * * * cd /home/openclaw/.openclaw/workspace/projects/fansale-biglietti-pezzali && python3 _system/fansale_collector.py >> _logs/cron.log 2>&1

# Salva (Ctrl+X → Y → Enter)
```

### Opzione C: SystemD Service + Timer

```bash
# Crea file service
sudo nano /etc/systemd/system/fansale-collector.service

[Unit]
Description=FanSale Biglietti Max Pezzali Collector
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/home/openclaw/.openclaw/workspace/projects/fansale-biglietti-pezzali
ExecStart=/usr/bin/python3 /home/openclaw/.openclaw/workspace/projects/fansale-biglietti-pezzali/_system/fansale_collector.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target

# Salva e exit: Ctrl+X → Y → Enter
```

```bash
# Crea file timer
sudo nano /etc/systemd/system/fansale-collector.timer

[Unit]
Description=FanSale Collector Timer (ogni 30 min)
Requires=fansale-collector.service

[Timer]
OnBootSec=1min
OnUnitActiveSec=30min
AccuracySec=1s

[Install]
WantedBy=timers.target

# Salva e exit: Ctrl+X → Y → Enter
```

```bash
# Abilita e avvia
sudo systemctl daemon-reload
sudo systemctl enable fansale-collector.timer
sudo systemctl start fansale-collector.timer

# Verifica
sudo systemctl status fansale-collector.timer
sudo systemctl list-timers fansale-collector.timer
```

---

## Step 4: Verifica Esecuzione

### Check Cron Execution Log

```bash
# Visualizza i log delle scansioni
ls -lh _logs/scan_*.json | tail -5

# Conta quante scansioni sono state fatte
ls _logs/scan_*.json | wc -l

# Leggi l'ultima scansione
cat _logs/scan_*.json | tail -1 | python3 -m json.tool | head -50
```

### Check Telegram Notifications

Controlla il chat Telegram per messaggi da bot.

Se non ricevi messaggi:
- Verifica che `config.json` abbia token e chat_id corretti
- Verifica che il bot sia effettivamente aggiunto alla chat
- Guarda `_logs/cron.log` per errori

---

## Step 5: Configurazione Report

Attualmente il collector **scarica** i biglietti. Per inviare report su Telegram:

1. Crea file `_system/fansale_reporter.py` (da implementare)
2. Configura il reporter per:
   - Leggere l'ultima scansione
   - Confrontare con la precedente
   - Inviare notifica Telegram con DIFFERENZE RILEVANTI
3. Aggiungi il reporter al cron (dopo il collector)

---

## Troubleshooting

### Errore: "playwright not installed"
```bash
pip install playwright --break-system-packages
playwright install chromium
```

### Errore: "Chromium fails to launch"
```bash
# Installa dipendenze Chromium
sudo apt-get install -y gconf-service libasound2 libatk1.0-0 libatk-bridge2.0-0 libc6
```

### Errore: "Cloudflare blocks access"
- Verifica di navigare da HOME first (il collector lo fa automaticamente)
- Aumenta delay tra navigazioni in `fansale_collector.py`
- Controlla i log: `_logs/cron.log`

### Telegrambot non invia messaggi
- Verifica chat_id: visita `https://api.telegram.org/botTOKEN/getUpdates` (replace TOKEN)
- Verifica che il bot sia aggiunto alla chat
- Controlla permessi bot su Telegram

---

## Manutenzione

### Pulizia Log Vecchi

```bash
# Cancella scansioni più vecchie di 7 giorni
find _logs/scan_*.json -mtime +7 -delete

# Oppure mantenere solo ultimi 100 file
ls -t _logs/scan_*.json | tail -n +101 | xargs rm -f
```

### Monitoraggio Health

```bash
# Quante scansioni negli ultimi 30 giorni?
find _logs/scan_*.json -mtime -30 | wc -l

# Sono eseguite regolarmente? (dovrebbero essere ~1440 in 30 giorni, 1 ogni 30 min)
find _logs/scan_*.json -mtime -30 | wc -l  # Dovrebbe essere ~1440
```

---

## Status

- ✅ Collector script pronto
- ⏳ Reporter script da implementare
- ⏳ Cron setup da eseguire
- ⏳ Telegram token da configurare

**Prossimo step:** Configura Telegram token in `_system/config.json` e esegui il primo test!
