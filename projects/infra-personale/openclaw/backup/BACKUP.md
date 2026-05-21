# Backup OpenClaw — Documentazione

## Infrastruttura FTP

| Campo | Valore |
|---|---|
| Host | ftp.ingsoftware.it |
| Porta | 21 |
| Utente | backup@ingsoftware.it |
| Cartella | /openclaw/ |

Le credenziali complete sono in `_utility/static/openclaw_ftp_backup.py` (non committare in repo pubblici).

---

## Backup Workspace OpenClaw

**Script:** `_utility/static/openclaw_ftp_backup.py`
**Cron:** ogni notte alle 02:00 (Europe/Rome) — job `OpenClaw workspace FTP backup notturno`

### Cosa viene backuppato
- Intero workspace `/home/openclaw/.openclaw/workspace`
- Esclusi: `.git/`, `__pycache__/`, `*.pyc`, `node_modules/`, `.DS_Store`

### Formato file
```
YYYYMMDD openclaw backup.tar.gz
```
Esempio: `20260521 openclaw backup.tar.gz`

### Politica di retention
- **Ultimi 7 giorni:** tutti i backup conservati
- **Da 8 giorni a 12 mesi fa:** solo il primo file disponibile per ogni mese
- **Oltre 12 mesi:** eliminati automaticamente

### Notifica Telegram
Al termine di ogni backup, viene inviato un messaggio nel topic 1 del gruppo IAco Team con:
- File caricato (nome + path completo)
- Dimensione in MB
- Esito trasmissione
- File cancellati (con policy retention)
- File rimasti sul server FTP

---

## Note tecniche

- Il fix `split("/")[-1]` su `ftp.nlst()` gestisce server FTP che restituiscono path completi invece dei soli filename.
- Il backup viene creato in `/tmp/` e rimosso dopo l'upload.
- In caso di errore FTP o errore creazione archivio, la notifica Telegram viene inviata con ❌.
