#!/usr/bin/env python3
"""
Backup notturno del workspace OpenClaw su FTP ingsoftware.it
Retention: ultimi 7 giorni + primo file disponibile per ogni mese (fino a 12 mesi fa)
"""

import os
import sys
import tarfile
import ftplib
import re
import requests
from datetime import datetime, timedelta
import zoneinfo

# --- CONFIG ---
WORKSPACE = "/home/openclaw/.openclaw/workspace"
FTP_HOST = "ftp.ingsoftware.it"
FTP_PORT = 21
FTP_USER = "backup@ingsoftware.it"
FTP_PASS = "jvRMO*W+^;#Zg$MR"
FTP_DIR = "/openclaw"

TZ = zoneinfo.ZoneInfo("Europe/Rome")
NOW = datetime.now(TZ)
DATE_STR = NOW.strftime("%Y%m%d")
BACKUP_FILENAME = f"{DATE_STR} openclaw backup.tar.gz"
LOCAL_TMP = f"/tmp/{BACKUP_FILENAME}"

TELEGRAM_TOKEN = "8699275494:AAE13PcCiRgMr5ELrAtJMHodaCHCcbtQM3A"
TELEGRAM_CHAT_ID = "-1003877516285"
TELEGRAM_TOPIC_ID = 1

FILE_RE = re.compile(r"^(\d{8}) openclaw backup\.tar\.gz$")


def log(msg):
    print(f"[{NOW.strftime('%H:%M:%S')}] {msg}")


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "message_thread_id": TELEGRAM_TOPIC_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()
    except Exception as e:
        log(f"Telegram error: {e}")


def create_backup():
    log(f"Creo archivio: {LOCAL_TMP}")
    excludes = {".git", "__pycache__", "*.pyc", "node_modules", ".DS_Store"}

    def exclude_filter(tarinfo):
        name = tarinfo.name
        for exc in excludes:
            if exc.startswith("*"):
                if name.endswith(exc[1:]):
                    return None
            elif exc in name.split(os.sep):
                return None
        return tarinfo

    with tarfile.open(LOCAL_TMP, "w:gz") as tar:
        tar.add(WORKSPACE, arcname="workspace", filter=exclude_filter)

    size = os.path.getsize(LOCAL_TMP)
    log(f"Archivio creato: {size:,} bytes ({size / 1024 / 1024:.1f} MB)")
    return size


def connect_ftp():
    ftp = ftplib.FTP()
    ftp.connect(FTP_HOST, FTP_PORT, timeout=60)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.set_pasv(True)
    try:
        ftp.cwd(FTP_DIR)
    except ftplib.error_perm:
        ftp.mkd(FTP_DIR)
        ftp.cwd(FTP_DIR)
    return ftp


def list_backups(ftp):
    """Ritorna lista di filename che corrispondono al pattern, ordinata per data."""
    files = []
    for name in ftp.nlst():
        m = FILE_RE.match(name.strip())
        if m:
            files.append(name.strip())
    files.sort()
    return files


def compute_retention(files):
    """Calcola quali file tenere e quali cancellare."""
    today = NOW.date()
    cutoff_12m = today - timedelta(days=365)

    keep = set()
    delete = []

    # Ultimi 7 giorni
    recent_threshold = today - timedelta(days=7)

    # Primo file per ogni mese (da 1 a 12 mesi fa)
    monthly_kept = {}  # "YYYYMM" -> filename

    for fname in files:
        m = FILE_RE.match(fname)
        if not m:
            continue
        date_str = m.group(1)
        try:
            fdate = datetime.strptime(date_str, "%Y%m%d").date()
        except ValueError:
            continue

        if fdate < cutoff_12m:
            # Più vecchio di 12 mesi → sempre cancella
            delete.append(fname)
            continue

        if fdate >= recent_threshold:
            # Ultimi 7 giorni → tieni
            keep.add(fname)
            continue

        # Tra 7 giorni e 12 mesi fa → tieni solo il primo del mese
        month_key = fdate.strftime("%Y%m")
        if month_key not in monthly_kept:
            monthly_kept[month_key] = (fdate, fname)
        else:
            existing_date, _ = monthly_kept[month_key]
            if fdate < existing_date:
                monthly_kept[month_key] = (fdate, fname)

    for _date, fname in monthly_kept.values():
        keep.add(fname)

    for fname in files:
        if fname not in keep and fname not in delete:
            delete.append(fname)

    return keep, delete


def upload_file(ftp, local_path, remote_name):
    log(f"Upload: {remote_name}")
    with open(local_path, "rb") as f:
        ftp.storbinary(f"STOR {remote_name}", f, blocksize=65536)
    log("Upload completato")


def delete_files(ftp, files):
    deleted = []
    for fname in files:
        try:
            ftp.delete(fname)
            log(f"Cancellato: {fname}")
            deleted.append(fname)
        except Exception as e:
            log(f"Errore cancellazione {fname}: {e}")
    return deleted


def main():
    errors = []
    uploaded_size = 0
    deleted_files = []
    remaining_files = []
    upload_ok = False

    # 1. Crea backup locale
    try:
        uploaded_size = create_backup()
    except Exception as e:
        msg = f"❌ Backup OpenClaw FALLITO — errore creazione archivio: {e}"
        log(msg)
        send_telegram(msg)
        sys.exit(1)

    # 2. Connessione FTP
    try:
        ftp = connect_ftp()
        log(f"FTP connesso: {FTP_HOST}{FTP_DIR}")
    except Exception as e:
        msg = f"❌ Backup OpenClaw FALLITO — errore FTP: {e}"
        log(msg)
        send_telegram(msg)
        os.unlink(LOCAL_TMP)
        sys.exit(1)

    try:
        # 3. Lista file esistenti
        existing = list_backups(ftp)
        log(f"File esistenti: {len(existing)}")

        # 4. Upload nuovo backup
        try:
            upload_file(ftp, LOCAL_TMP, BACKUP_FILENAME)
            upload_ok = True
        except Exception as e:
            errors.append(f"Upload fallito: {e}")
            log(f"Errore upload: {e}")

        # 5. Aggiorna lista dopo upload
        all_files = list_backups(ftp)

        # 6. Calcola retention
        keep, to_delete = compute_retention(all_files)

        # 7. Cancella file da rimuovere
        deleted_files = delete_files(ftp, to_delete)

        # 8. Lista file rimanenti
        remaining_files = list_backups(ftp)

    finally:
        try:
            ftp.quit()
        except Exception:
            pass
        # Pulisci file temporaneo locale
        if os.path.exists(LOCAL_TMP):
            os.unlink(LOCAL_TMP)

    # 9. Notifica Telegram
    size_mb = uploaded_size / 1024 / 1024
    status_icon = "✅" if upload_ok and not errors else "⚠️"

    lines = [
        f"{status_icon} <b>Backup OpenClaw</b> — {NOW.strftime('%d/%m/%Y %H:%M')}",
        "",
        f"📦 <b>File caricato:</b> {FTP_HOST}{FTP_DIR}/{BACKUP_FILENAME}",
        f"📏 <b>Dimensione:</b> {size_mb:.1f} MB",
        f"🔄 <b>Trasmissione:</b> {'OK' if upload_ok else 'FALLITA'}",
    ]

    if errors:
        lines.append(f"⚠️ <b>Errori:</b> {'; '.join(errors)}")

    if deleted_files:
        lines.append("")
        lines.append(f"🗑 <b>Cancellati ({len(deleted_files)}):</b>")
        for f in deleted_files:
            lines.append(f"  • {f}")
    else:
        lines.append("🗑 <b>Cancellati:</b> nessuno")

    lines.append("")
    lines.append(f"📁 <b>File sul server ({len(remaining_files)}):</b>")
    for f in remaining_files[-10:]:  # mostra ultimi 10 max
        lines.append(f"  • {f}")
    if len(remaining_files) > 10:
        lines.append(f"  … e altri {len(remaining_files) - 10}")

    send_telegram("\n".join(lines))
    log("Notifica Telegram inviata")


if __name__ == "__main__":
    main()
