# BACKUP.md - Sistema Backup OpenClaw

Documentazione del backup completo notturno su FTP.

---

## 📋 Strategia Backup

### Backup FTP Completo (notturno)
- **Cosa**: Backup completo `~/.openclaw` + `/home/openclaw/attibot`
- **Quando**: Ogni notte alle **02:00** (Europe/Rome)
- **Dove**: FTP `ingsoftware.it` (93.151.207.173:221)
- **Retention**: 
  - Ultimi 7 giorni (daily)
  - Primo backup di ogni mese (fino a 12 mesi fa)
- **Notifiche**: Telegram (solo errori o successi significativi)

---

## 🛠️ Implementazione

### Script Python

**Path:** `/home/openclaw/.openclaw/workspace/_utility/static/openclaw_ftp_backup.py`

**Funzionamento:**
1. Usa `openclaw backup create` (comando ufficiale)
2. Aggiunge `/home/openclaw/attibot` all'archivio
3. Upload su FTP `ingsoftware.it`
4. Cleanup retention (7gg + 1/mese)
5. Notifica Telegram con esito

**Configurazione FTP:**
- Host: `93.151.207.173:221`
- User: `backupAtti`
- Path: `/home/backupAtti/Openclaw`

---

## ⏰ Scheduling

### Crontab di Sistema

```cron
# Backup FTP notturno (02:00 ogni notte)
0 2 * * * /usr/bin/python3 /home/openclaw/.openclaw/workspace/_utility/static/openclaw_ftp_backup.py >> /home/openclaw/.openclaw/logs/ftp_backup_cron.log 2>&1
```

**Installazione:**
```bash
crontab -e
```

**Verifica:**
```bash
crontab -l | grep backup
```

---

## 🧪 Test

### Test Manuale

```bash
# Lancia backup
cd /home/openclaw/.openclaw/workspace
python3 _utility/static/openclaw_ftp_backup.py

# Verifica log
cat /tmp/openclaw_backup_$(date +%Y%m%d).log
```

---

## 🚨 Troubleshooting

### Backup fallisce

1. **Verifica connettività FTP:**
   ```bash
   nc -zv 93.151.207.173 221
   ```

2. **Verifica credenziali:**
   ```bash
   grep -E "FTP_(HOST|USER|PASS)" /home/openclaw/.openclaw/workspace/_utility/static/openclaw_ftp_backup.py
   ```

3. **Test manuale:**
   ```bash
   python3 /home/openclaw/.openclaw/workspace/_utility/static/openclaw_ftp_backup.py
   ```

4. **Controlla log:**
   ```bash
   cat /tmp/openclaw_backup_$(date +%Y%m%d).log
   ```

### Verifica Spazio FTP

Retention automatica mantiene ~7-19 backup (7gg + max 12 mesi).  
Stima dimensione: ~100-500MB/backup → max 10GB.

**Controllo manuale spazio:**
```bash
python3 << 'EOF'
import ftplib
ftp = ftplib.FTP()
ftp.connect("93.151.207.173", 221)
ftp.login("backupAtti", "FhHuK%IMItBm07nc#")
ftp.cwd("/home/backupAtti/Openclaw")
ftp.retrlines("LIST")
ftp.quit()
EOF
```

---

## 📝 Note

- **Notifiche Telegram** via script interno (token hardcoded)
- **Cron di sistema** > OpenClaw cron perché:
  - Zero consumo token LLM
  - Più affidabile (no usage limits)
  - Più veloce (no startup agente)
  - Più prevedibile (script deterministico)

---

## 🔗 Related

- [[_system/GIT_AUTOMATION]] - Auto-commit git workspace

---

**Ultimo aggiornamento:** 2026-08-23  
**Autore:** IAcopo (OpenClaw main agent)
