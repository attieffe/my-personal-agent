# GIT_AUTOMATION.md - Auto-Commit Workspace

Sistema di auto-commit automatico per versioning git del workspace.

---

## 📋 Strategia

### Auto-commit Git (orario)
- **Cosa**: Commit + push automatico modifiche workspace
- **Quando**: Ogni ora al minuto **:23** (Europe/Rome)
- **Dove**: Repository Git del workspace
- **Notifiche**: Telegram (solo errori)
- **Log**: `/home/openclaw/.openclaw/logs/git_auto_commit.log`

---

## 🛠️ Implementazione

### Script Bash

#### `/home/openclaw/.openclaw/scripts/git_auto_commit.sh`

Auto-commit modifiche workspace con log e notifiche errori.

**Funzionamento:**
1. Verifica modifiche con `git diff`
2. Se nessuna modifica: esce silenzioso
3. Se modifiche presenti:
   - Stage: `git add -A`
   - **Filtro sicurezza**: rimuove `.env` dallo stage (previene leak secrets)
   - Commit: messaggio auto-generato
   - Push: al remote configurato
4. Log in `/home/openclaw/.openclaw/logs/git_auto_commit.log`
5. Notifica Telegram solo in caso di errore

**Messaggio commit:**
- Con modifiche in `memory/`: "Auto-commit: N file(s) - memory updates"
- Altrimenti: "Auto-commit: N file(s) updated"

---

## ⏰ Scheduling

### Crontab di Sistema

```cron
# Auto-commit workspace (ogni ora al :23)
23 * * * * /home/openclaw/.openclaw/scripts/git_auto_commit.sh >> /home/openclaw/.openclaw/logs/git_auto_commit_cron.log 2>&1
```

**Installazione:**
```bash
crontab -e
```

**Verifica:**
```bash
crontab -l | grep git_auto_commit
```

---

## 🔐 Security

### Filtro `.env`

Lo script **esclude automaticamente `.env`** dallo staging per prevenire leak di secrets (API keys, credenziali, ecc.).

```bash
# Remove .env from staging if present (security)
git reset HEAD .env 2>/dev/null || true
```

Questo previene blocchi GitHub Push Protection e leak accidentali.

---

## 🧪 Test

### Test Notifica Telegram

```bash
/home/openclaw/.openclaw/scripts/telegram_notify.sh "🧪 Test notifica git automation"
```

### Test Auto-Commit

```bash
# Crea una modifica test
echo "test $(date)" >> memory/test.md

# Lancia script manualmente
/home/openclaw/.openclaw/scripts/git_auto_commit.sh

# Verifica log
tail -20 /home/openclaw/.openclaw/logs/git_auto_commit.log

# Verifica commit
cd /home/openclaw/.openclaw/workspace && git log -1
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

### Push fallisce (GitHub Protection)

Se GitHub blocca il push per secrets rilevati:

1. **Verifica file in staging:**
   ```bash
   git status
   ```

2. **Rimuovi file sensibili:**
   ```bash
   git reset HEAD .env
   git commit --amend
   git push
   ```

3. **Aggiorna `.gitignore`:**
   Assicurati che `.env` e altri file sensibili siano nel `.gitignore`.

### Notifiche Telegram non arrivano

1. **Test connettività API:**
   ```bash
   curl -s "https://api.telegram.org/bot8699275494:AAFKX13Y_tAJxezbV_pUBtnuuybyerFp0rI/getMe"
   ```

2. **Verifica bot token:**
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

I log crescono nel tempo. Rotazione consigliata:

```bash
# Rotazione manuale (mensile)
mv /home/openclaw/.openclaw/logs/git_auto_commit.log \
   /home/openclaw/.openclaw/logs/git_auto_commit_$(date +%Y%m).log.old

# Cleanup log vecchi (>90 giorni)
find /home/openclaw/.openclaw/logs/ -name "git_auto_commit_*.log.old" -mtime +90 -delete
```

---

## 📝 Note

- **Silenzioso in caso di successo** (evita spam Telegram)
- **Notifica solo errori critici** (push failed, git error, ecc.)
- **Cron di sistema** > OpenClaw cron perché:
  - Zero consumo token LLM
  - Più affidabile (no usage limits)
  - Più veloce (no startup agente)
  - Più prevedibile (script deterministico)

---

## 🔧 Utility

### Script Telegram Notify

**Path:** `/home/openclaw/.openclaw/scripts/telegram_notify.sh`

Helper riutilizzabile per inviare notifiche Telegram via API HTTP.

**Utilizzo:**
```bash
/home/openclaw/.openclaw/scripts/telegram_notify.sh "Messaggio di notifica"
```

**Parametri hardcoded:**
- Bot Token: `8699275494:AAFKX13Y_tAJxezbV_pUBtnuuybyerFp0rI`
- Chat ID: `506258994`

---

## 🔗 Related

- [[_system/BACKUP]] - Backup FTP completo
- [[AGENTS]] - Filosofia agente e memory management

---

**Ultimo aggiornamento:** 2026-08-23  
**Autore:** IAcopo (OpenClaw main agent)
