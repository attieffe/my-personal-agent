#!/usr/bin/env python3
"""
Backup notturno OpenClaw su FTP ingsoftware.it

Strategia:
1. Usa `openclaw backup create` (comando ufficiale) → copre ~/.openclaw completo
   (config, state, credentials, workspace, workspace-colzani, workspace-miotesoro)
2. Aggiunge cartella attibot (esterna a ~/.openclaw)
3. Combina tutto in un archivio giornaliero e carica su FTP
4. Retention: ultimi 7 giorni + primo file disponibile per ogni mese (fino a 12 mesi fa)
"""

import os
import sys
import subprocess
import tarfile
import glob
import ftplib
import re
import requests
from datetime import datetime, timedelta
import zoneinfo

# --- CONFIG ---
ATTIBOT = "/home/openclaw/attibot"
OPENCLAW_CMD = "openclaw"  # path del comando openclaw
FTP_HOST = "ftp.ingsoftware.it"
FTP_PORT = 21
FTP_USER = "backup@ingsoftware.it"
FTP_PASS = "jvRMO*W+^;#Zg$MR"
FTP_DIR = "/openclaw"

TZ = zoneinfo.ZoneInfo("Europe/Rome")
NOW = datetime.now(TZ)
DATE_STR = NOW.strftime("%Y%m%d")
BACKUP_FILENAME = f"{DATE_STR} openclaw backup.tar.gz"
LOCAL_TMP_FINAL = f"/tmp/{BACKUP_FILENAME}"
WORK_DIR = "/tmp/openclaw_backup_work"

TELEGRAM_TOKEN = "8699275494:AAE13PcCiRgMr5ELrAtJMHodaCHCcbtQM3A"
TELEGRAM_CHAT_ID = "506258994"
TELEGRAM_TOPIC_ID = None

FILE_RE = re.compile(r"^(\d{8}) openclaw backup\.tar\.gz$")


def log(msg):
    print(f"[{NOW.strftime('%H:%M:%S')}] {msg}")


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    if TELEGRAM_TOPIC_ID:
        payload["message_thread_id"] = TELEGRAM_TOPIC_ID
    try:
        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()
    except Exception as e:
        log(f"Telegram error: {e}")


def run_openclaw_backup(output_dir):
    """
    Esegue `openclaw backup create --output <dir> --verify --json`
    e ritorna il path del file creato (letto dall'output JSON del comando).
    """
    os.makedirs(output_dir, exist_ok=True)
    log(f"Eseguo: {OPENCLAW_CMD} backup create --output {output_dir} --verify --json")

    result = subprocess.run(
        [OPENCLAW_CMD, "backup", "create", "--output", output_dir, "--verify", "--json"],
        capture_output=True,
        text=True,
        timeout=600,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"openclaw backup create fallito (exit {result.returncode}):\n"
            f"stdout: {result.stdout.strip()}\n"
            f"stderr: {result.stderr.strip()}"
        )

    # Leggi archivePath dall'output JSON
    import json
    try:
        info = json.loads(result.stdout.strip())
        archive_path = info["archivePath"]
    except Exception:
        # Fallback: cerca il file .tar.gz nella cartella di output
        archives = sorted(glob.glob(os.path.join(output_dir, "*-openclaw-backup.tar.gz")))
        if not archives:
            raise RuntimeError(
                f"openclaw backup create completato ma nessun archivio trovato in {output_dir}.\n"
                f"stdout: {result.stdout.strip()}"
            )
        archive_path = archives[-1]

    if not os.path.isfile(archive_path):
        raise RuntimeError(f"Archivio segnalato da openclaw non trovato: {archive_path}")

    size = os.path.getsize(archive_path)
    log(f"Backup ufficiale OpenClaw: {os.path.basename(archive_path)} ({size / 1024 / 1024:.1f} MB)")
    return archive_path


def create_combined_backup(official_archive, final_path):
    """
    Crea l'archivio combinato:
    - openclaw-official.tar.gz  (il backup ufficiale openclaw)
    - attibot/                  (cartella attibot se presente)
    """
    log(f"Creo archivio combinato: {final_path}")

    excludes_ext = {".pyc", ".DS_Store"}
    excludes_dir = {"__pycache__", "node_modules", ".git"}

    def exclude_filter(tarinfo):
        name = os.path.basename(tarinfo.name)
        parts = set(tarinfo.name.split(os.sep))
        if name in excludes_ext or any(name.endswith(e) for e in excludes_ext):
            return None
        if parts & excludes_dir:
            return None
        return tarinfo

    with tarfile.open(final_path, "w:gz") as tar:
        # 1. Include il backup ufficiale openclaw come file
        tar.add(official_archive, arcname=f"openclaw-official/{os.path.basename(official_archive)}")
        log(f"  + openclaw-official/{os.path.basename(official_archive)}")

        # 2. Include cartella attibot
        if os.path.isdir(ATTIBOT):
            tar.add(ATTIBOT, arcname="attibot", filter=exclude_filter)
            log(f"  + attibot/")
        else:
            log(f"  ! attibot non trovato: {ATTIBOT} — saltato")

    size = os.path.getsize(final_path)
    log(f"Archivio combinato: {size:,} bytes ({size / 1024 / 1024:.1f} MB)")
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
        basename = name.strip().split("/")[-1]
        m = FILE_RE.match(basename)
        if m:
            files.append(basename)
    files.sort()
    return files


def compute_retention(files):
    """Calcola quali file tenere e quali cancellare."""
    today = NOW.date()
    cutoff_12m = today - timedelta(days=365)
    recent_threshold = today - timedelta(days=7)

    keep = set()
    delete = []
    monthly_kept = {}  # "YYYYMM" -> (date, filename)

    for fname in files:
        m = FILE_RE.match(fname)
        if not m:
            continue
        try:
            fdate = datetime.strptime(m.group(1), "%Y%m%d").date()
        except ValueError:
            continue

        if fdate < cutoff_12m:
            delete.append(fname)
            continue

        if fdate >= recent_threshold:
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
    log(f"Upload FTP: {remote_name}")
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


def cleanup(*paths):
    for p in paths:
        try:
            if os.path.isfile(p):
                os.unlink(p)
            elif os.path.isdir(p):
                import shutil
                shutil.rmtree(p, ignore_errors=True)
        except Exception:
            pass


def main():
    errors = []
    uploaded_size = 0
    deleted_files = []
    remaining_files = []
    upload_ok = False
    official_archive = None
    attibot_included = os.path.isdir(ATTIBOT)

    # 1. Backup ufficiale OpenClaw
    try:
        official_archive = run_openclaw_backup(WORK_DIR)
    except Exception as e:
        msg = f"❌ Backup OpenClaw FALLITO — errore openclaw backup create: {e}"
        log(msg)
        send_telegram(msg)
        cleanup(WORK_DIR)
        sys.exit(1)

    # 2. Crea archivio combinato (openclaw ufficiale + attibot)
    try:
        uploaded_size = create_combined_backup(official_archive, LOCAL_TMP_FINAL)
    except Exception as e:
        msg = f"❌ Backup OpenClaw FALLITO — errore creazione archivio combinato: {e}"
        log(msg)
        send_telegram(msg)
        cleanup(WORK_DIR, LOCAL_TMP_FINAL)
        sys.exit(1)
    finally:
        cleanup(WORK_DIR)  # rimuovi cartella di lavoro temporanea

    # 3. Connessione FTP
    try:
        ftp = connect_ftp()
        log(f"FTP connesso: {FTP_HOST}{FTP_DIR}")
    except Exception as e:
        msg = f"❌ Backup OpenClaw FALLITO — errore connessione FTP: {e}"
        log(msg)
        send_telegram(msg)
        cleanup(LOCAL_TMP_FINAL)
        sys.exit(1)

    try:
        existing = list_backups(ftp)
        log(f"File esistenti sul server: {len(existing)}")

        try:
            upload_file(ftp, LOCAL_TMP_FINAL, BACKUP_FILENAME)
            upload_ok = True
        except Exception as e:
            errors.append(f"Upload fallito: {e}")
            log(f"Errore upload: {e}")

        all_files = list_backups(ftp)
        keep, to_delete = compute_retention(all_files)
        deleted_files = delete_files(ftp, to_delete)
        remaining_files = list_backups(ftp)

    finally:
        try:
            ftp.quit()
        except Exception:
            pass
        cleanup(LOCAL_TMP_FINAL)

    # 4. Notifica Telegram
    size_mb = uploaded_size / 1024 / 1024
    status_icon = "✅" if upload_ok and not errors else "⚠️"

    lines = [
        f"{status_icon} <b>Backup OpenClaw</b> — {NOW.strftime('%d/%m/%Y %H:%M')}",
        "",
        f"📦 <b>File:</b> {FTP_HOST}{FTP_DIR}/{BACKUP_FILENAME}",
        f"📏 <b>Dimensione:</b> {size_mb:.1f} MB",
        f"🔄 <b>Upload:</b> {'OK' if upload_ok else 'FALLITO'}",
        "",
        f"📂 <b>Contenuto archivio:</b>",
        f"  • openclaw-official/ (backup ufficiale <code>openclaw backup create</code>)",
        f"  • {'attibot/ ✓' if attibot_included else 'attibot/ ⚠️ non trovato'}",
    ]

    if errors:
        lines.append(f"\n⚠️ <b>Errori:</b> {'; '.join(errors)}")

    if deleted_files:
        lines.append(f"\n🗑 <b>Cancellati per retention ({len(deleted_files)}):</b>")
        for f in deleted_files:
            lines.append(f"  • {f}")
    else:
        lines.append("🗑 <b>Retention:</b> nessun file rimosso")

    lines.append(f"\n📁 <b>File sul server ({len(remaining_files)}):</b>")
    for f in remaining_files[-10:]:
        lines.append(f"  • {f}")
    if len(remaining_files) > 10:
        lines.append(f"  … e altri {len(remaining_files) - 10}")

    send_telegram("\n".join(lines))
    log("Notifica Telegram inviata")

    if not upload_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
