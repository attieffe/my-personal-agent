### 10.1.87.226 NAS SYNOLOGY
- esegue backup con HyperBackup
- **destinazione**: 10.1.87.160 -Raspberry PI mediate 
- **tecnologia**: r-sync
- **user**: backupuser
- **cartella condivisa**: nasbak
- **Directory**: nasgenio_bk
- **Periodicità**: giornaliera

### ULTAHOST SERVER
- backup su ingsoftware in cartella backup/intv
- l'utente FTP logga in backup
- SQL: dump di db totale ogni notte
- File system solo i delta e trasmette i delta con **duplicity**

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