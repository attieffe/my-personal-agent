# BACKUP.md - Sistema di Backup OpenClaw

Documentazione completa del sistema di backup automatizzato.

---

## 📋 Strategia Backup

### 1. **Backup FTP Completo** (notturno)
- **Cosa**: Backup completo `~/.openclaw` + `/home/openclaw/attibot`
- **Quando**: Ogni notte alle **02:00** (Europe/Rome)
- **Dove**: FTP `ingsoftware.it` (93.151.207.173:221)
- **Retention**: 
  - Ultimi 7 giorni (daily)
  - Primo backup di ogni mese (fino a 12 mesi fa)
- **Notifiche**: Telegram (solo errori o successi significativi)

### 2. **Auto-commit Git** (orario)
- **Cosa**: Commit + push automatico modifiche workspace
- **Quando**: Ogni ora al minuto **:23** (Europe/Rome)
- **Dove**: Repository Git del workspace
- **Notifiche**: Telegram (solo errori)

---

## 🛠️ Componenti Sistema

### Script Bash

#### `/home/openclaw/.openclaw/scripts/telegram_notify.sh`
Helper per inviare notifiche Telegram via API HTTP.

**Utilizzo:**
```bash
/home/openclaw/.openclaw/scripts/telegram_notify.sh "Messaggio di notifica"
```

**Parametri hardcoded:**
- Bot Token: `8699275494:AAFKX13Y_tAJxezbV_pUBtnuuybyerFp0rI`
- Chat ID: `506258994`

#### `/home/openclaw/.openclaw/scripts/git_auto_commit.sh`
Auto-commit modifiche workspace con log e notifiche errori.

**Funzionamento:**
1. Verifica modifiche con `git diff`
2. Se nessuna modifica: esce silenzioso
3. Se modifiche presenti:
   - Stage: `git add -A`
   - Commit: messaggio auto-generato
   - Push: al remote configurato
4. Log in `/home/openclaw/.openclaw/logs/git_auto_commit.log`
5. Notifica Telegram solo in caso di errore

**Messaggio commit:**
- Con modifiche in `memory/`: "Auto-commit: N file(s) - memory updates"
- Altrimenti: "Auto-commit: N file(s) updated"

### Script Python

#### `/home/openclaw/.openclaw/workspace/_utility/static/openclaw_ftp_backup.py`
Backup completo su FTP con retention intelligente.

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

## ⏰ Cron Jobs

### Crontab di Sistema

```cron
# Auto-commit workspace (ogni ora al :23)
23 * * * * /home/openclaw/.openclaw/scripts/git_auto_commit.sh

# Backup FTP notturno (02:00 ogni notte)
0 2 * * * cd /home/openclaw/.openclaw/workspace && /usr/bin/python3 _utility/static/openclaw_ftp_backup.py
```

**Installazione:**
```bash
crontab -e
```

**Verifica cron attivi:**
```bash
crontab -l
```

**Log cron di sistema:**
```bash
grep CRON /var/log/syslog | tail -20
```

---

## 🧪 Test

### Test Notifica Telegram

```bash
/home/openclaw/.openclaw/scripts/telegram_notify.sh "🧪 Test notifica backup"
```

Dovresti ricevere il messaggio su Telegram entro pochi secondi.

### Test Auto-Commit

```bash
# Crea una modifica test
echo "test $(date)" >> /home/openclaw/.openclaw/workspace/memory/test.md

# Lancia script manualmente
/home/openclaw/.openclaw/scripts/git_auto_commit.sh

# Verifica log
tail -20 /home/openclaw/.openclaw/logs/git_auto_commit.log

# Verifica commit
cd /home/openclaw/.openclaw/workspace && git log -1
```

### Test Backup FTP

```bash
# Lancia backup manualmente
cd /home/openclaw/.openclaw/workspace
python3 _utility/static/openclaw_ftp_backup.py

# Verifica log
cat /tmp/openclaw_backup_$(date +%Y%m%d).log
```

---

## 🚨 Troubleshooting

### Auto-commit non funziona

1. **Verifica permessi script:**
   ```bash
   ls -lh /home/openclaw/.openclaw/scripts/git_auto_commit.sh
   # Deve essere -rwxrwxr-x
   ```

2. **Verifica cron attivo:**
   ```bash
   crontab -l | grep git_auto_commit
   ```

3. **Controlla log:**
   ```bash
   tail -50 /home/openclaw/.openclaw/logs/git_auto_commit.log
   ```

4. **Verifica git config:**
   ```bash
   cd /home/openclaw/.openclaw/workspace
   git config user.name
   git config user.email
   ```

### Backup FTP fallisce

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

### Notifiche Telegram non arrivano

1. **Test connettività API:**
   ```bash
   curl -s "https://api.telegram.org/bot8699275494:AAFKX13Y_tAJxezbV_pUBtnuuybyerFp0rI/getMe"
   ```

2. **Verifica bot token in script:**
   ```bash
   grep BOT_TOKEN /home/openclaw/.openclaw/scripts/telegram_notify.sh
   ```

3. **Test manuale:**
   ```bash
   /home/openclaw/.openclaw/scripts/telegram_notify.sh "Test"
   ```

---

## 🔄 Manutenzione

### Rotazione Log

I log di auto-commit crescono nel tempo. Rotazione consigliata:

```bash
# Rotazione manuale (mensile)
mv /home/openclaw/.openclaw/logs/git_auto_commit.log \
   /home/openclaw/.openclaw/logs/git_auto_commit_$(date +%Y%m).log.old

# Cleanup log vecchi (>90 giorni)
find /home/openclaw/.openclaw/logs/ -name "git_auto_commit_*.log.old" -mtime +90 -delete
```

### Verifica Spazio FTP

Retention automatica mantiene ~7-19 backup (7gg + max 12 mesi).  
Stima dimensione: ~100-500MB/backup → max 10GB.

**Controllo manuale spazio:**
```bash
# Lista backup su FTP (richiede FTP client o script Python custom)
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

- **Auto-commit** è silenzioso in caso di successo (evita spam)
- **Backup FTP** notifica solo errori critici o successi dopo N fallimenti
- **Cron di sistema** > OpenClaw cron perché:
  - Zero consumo token LLM
  - Più affidabile (no usage limits)
  - Più veloce (no startup agente)
  - Più prevedibile (script deterministici)

---

## 🔐 Sicurezza

⚠️ **Token e credenziali** sono hardcoded negli script per semplicità cron.  
File `/home/openclaw/.openclaw/scripts/` è leggibile solo da utente `openclaw` (permissions `drwxrwxr-x`).

**Best practice:**
- Non committare script con credenziali in repo pubblici
- Mantenere permissions `700` o `750` su `/home/openclaw/.openclaw/scripts/`
- Rotare token Telegram periodicamente (ogni 6-12 mesi)

---

**Ultimo aggiornamento:** 2026-08-23  
**Autore:** IAcopo (OpenClaw main agent)
