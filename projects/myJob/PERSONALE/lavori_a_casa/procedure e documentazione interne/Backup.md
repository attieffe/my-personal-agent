### 10.1.87.226 NAS SYNOLOGY
- esegue backup con HyperBackup
- **destinazione**: 10.1.87.160 -Raspberry PI mediate 
- **tecnologia**: r-sync
- **user**: backupuser
- **cartella condivisa**: nasbak
- **Directory**: nasgenio_bk
- **Periodicità**: giornaliera

### OPENCLAW WORKSPACE (attibot.ingeniosolution.it)
- **Destinazione**: FTP `93.151.207.173` porta 221 — cartella `/home/backupAtti/Openclaw`
- **User FTP**: `backupAtti`
- **Periodicità**: ogni notte alle 02:00 (Europe/Rome)
- **Nome file**: `YYYYMMDD openclaw backup.tar.gz`
- **Contenuto**: intero workspace `/home/openclaw/.openclaw/workspace` (esclusi `.git`, `node_modules`, `__pycache__`)
- **Retention**:
  - Ultimi 7 giorni: tutti
  - Da 8 giorni a 12 mesi fa: solo il **primo file disponibile** per ogni mese
  - Oltre 12 mesi: cancellati automaticamente
- **Script**: `_utility/static/openclaw_ftp_backup.py`
- **Cron job ID**: `68058dab-617c-445b-afcd-a45e333f4ebd`
- **Notifica**: Telegram (IAco Team, topic principale) con dimensione, percorso, file cancellati e lista file rimanenti
- Metodo: FTP su 10.1.87.226 - User backupAtti (password su LastPass) aperto all'esterno su porta 221 router vodafone

### ULTAHOST SERVER
- backup su ingsoftware in cartella backup/intv
- l'utente FTP logga in backup
- SQL: dump di db totale ogni notte
- File system solo i delta e trasmette i delta con **duplicity**
- Metodo: FTP su 10.1.87.226 - User backupAtti (password su LastPass)

### 10.1.87.148 (LAN) 10.1.87.149 (WIFI) PC ATTI SAETTA
- software Duplicati su porta 8300
- se problemi con la password:
	- C:\Program Files\Duplicati 2>Duplicati.CommandLine.ServerUtil.exe change-password --hosturl=http://127.0.0.1:8300 --server-datafolder "C:\ProgramData\Duplicati"
- 3 Piani di backup:
	- **Dropbox**:
		- Metodo: Dropbox Sync su user: ing.fiumano@gmail.com
		- Dati:
			- Include database di Filemaker da D:\Filemaker\Databases
			- C:\Users\ralf0\Documents\FATTURE
		- Dimensione: 383 MB
	- **NAS**:
		- Metodo: FTP su 10.1.87.226 - User backupAtti (password su LastPass)
			-  Include database di Filemaker da D:\Filemaker\Databases
			-  C:\Users\ralf0\Documents\FATTURE
			-  c:\Users\ralf0\Documents\Progetti
		- Dimensione: 14GB
	- **Local**:
		- Metodo: hard disk locale su F:\
		- Dati:
			- Include database di Filemaker da D:\Filemaker\Databases
			-  C:\Users\ralf0\Documents\FATTURE
			-  c:\Users\ralf0\Documents\Progetti
		- Dimensione: 14GB
