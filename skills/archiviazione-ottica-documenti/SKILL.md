---
name: "archiviazione-ottica-documenti"
description: "Archiviazione ottica documenti Atti: filename-first, OCR su permesso, upload Drive condiviso con --drive-shared-with-me, conferma obbligatoria."
---

# Archiviazione Ottica Documenti

Usa per archiviare documenti (PDF, foto, estratti conto, certificati) per Atti: analisi, naming, upload Google Drive, log.

## Motore canonico

Tutto vive nel progetto `/home/openclaw/.openclaw/workspace/projects/archiviazione-ottica-documenti/`:
- `_system/archiver.py` — orchestratore (`analyze` / `analyze --ocr` / `execute` / `list`)
- `_system/drive_uploader.py` — upload rclone (include già `--drive-shared-with-me`)
- `_system/vision_namer.py` — OCR/vision via OpenAI gpt-4o
- `_system/photos_to_pdf.py` — unisce più foto in un unico PDF (PyMuPDF)
- `README.md` — regole complete di routing (fonte canonica)
- `history.md` — log archiviazioni
- lifecycle file: `input/` → `90_processed/`

NON duplicare script o regole: esegui sempre gli script del progetto. Se una regola cambia, si aggiorna il README del progetto.

## Workflow

1. **Prepara**: file in `input/`. Più foto di un documento → prima un PDF unico con `_system/photos_to_pdf.py`. Se Atti fornisce già data+titolo, usali per il naming finale.
2. **Analizza**: `python3 _system/archiver.py analyze <file>` (dalla root del progetto)
   - Filename-first: se filename basta, niente OCR
   - Exit code 3 → filename insufficiente: chiedi permesso OCR ad Atti, poi `analyze --ocr`
3. **Proponi**: mostra a Atti filename finale `YYYYMMDD titolo.ext`, categoria, destinazioni Drive. ASPETTA conferma esplicita.
4. **Esegui**: `python3 _system/archiver.py execute '<proposal_json>'` → upload Drive + history.md + sposta originale in `90_processed/`
5. **Verifica**: controlla exit code (0 ok, 2 upload parzialmente fallito) e riporta destinazioni con esito.

## Regole critiche (mai violare)

- **`--drive-shared-with-me` SEMPRE** in ogni comando rclone verso `gdrive:Atti/` o `gdrive:Ingenio/`. Senza flag il file finisce nel My Drive dell'account di servizio (errore già successo il 2026-08-21). Gli script del progetto lo includono già; per rclone manuale aggiungerlo a mano.
- **Conferma di Atti obbligatoria** prima di ogni upload su Drive.
- **Filename-first**: OCR/vision solo se filename ambiguo, categoria incerta, o su richiesta di Atti.
- **Mai cancellare originali**: si spostano in `90_processed/` (mai rm).
- **Naming**: `YYYYMMDD titolo.ext`. La data già presente nel filename vince. Non rinominare "per estetica". Se Atti fornisce data e titolo espliciti, quelli vincono su tutto.
- Ricette senza importo NON sono SPESE_MEDICHE (categoria CERTIFICATI_SANITARI o ALTRO).
- Casi dubbi → categoria ALTRO + domanda ad Atti.

## Destinazioni Drive (riassunto)

- **Primaria SEMPRE**: `gdrive:Atti/Documenti/Archiviazione ottica/{ANNO}/`
- Extra per categoria:
  - BANCA → `Atti/Documenti/Banche/{sottocartella}/{ANNO}/`
  - CERTIFICATI_SANITARI → `Atti/Documenti/Sanità/`
  - SPESE_MEDICHE → `Atti/Documenti/DICHIARAZIONE DEI REDDITI/{anno+1}x{anno}/`
  - INGENIO_SOLUTION → `Ingenio/DOCUMENTI FISCALI/{ANNO}/`
  - AUTO → `Atti/Documenti/AUTO/{targa} {modello}/`
  - SCUOLA_BAMBINI → `Atti/Documenti/DICHIARAZIONE DEI REDDITI/{anno+1}x{anno}/Bambini/{figlio}/`
  - ALTRO → solo primaria

Mapping banche (Revolut, Isybank, BBVA, Satispay, Paypal, Webank, Intesa, BPM Ingenio, Revolut Ingenio, Revolut Cointestato; fallback BPM Ingenio): vedi `README.md` progetto.

## Dipendenze

- rclone con remote `gdrive` configurato
- Python: fitz (PyMuPDF), PIL, openai + dotenv (per OCR; OPENAI_API_KEY in `.env` del progetto)
