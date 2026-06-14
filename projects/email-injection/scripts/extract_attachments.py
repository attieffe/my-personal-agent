"""
Estrae allegati da un file .eml e tenta di identificare il mittente reale
(utile per email inoltrate in cui il From: è Atti stesso).

Uso:
  python extract_attachments.py --eml <path.eml> --out-dir <dir>

Output JSON su stdout:
{
  "eml": "<path>",
  "from_raw": "...",
  "subject_raw": "...",
  "real_sender": "...",   # mittente reale estratto (se inoltro)
  "attachments": [
    {"filename": "...", "content_type": "...", "size": 12345, "saved_path": "..."}
  ],
  "skipped": [...]        # allegati ignorati (inline, spazzatura)
}
"""
import argparse
import json
import os
import re
import sys
from email import policy
from email.parser import BytesParser
from pathlib import Path

JUNK_PATTERNS = re.compile(
    r"^(image\d+\.(png|jpg|gif|bmp)|att\d+\.(htm|html)|winmail\.dat)$",
    re.IGNORECASE,
)

FORWARD_PREFIXES = re.compile(r"^(fwd?:|i:|gir:|fw:)\s*", re.IGNORECASE)

REAL_SENDER_PATTERNS = (
    re.compile(r"(?:^|\n)(?:Da|From)\s*:\s*(.+?)(?:\n|$)", re.IGNORECASE | re.MULTILINE),
    re.compile(r"(?:^|\n)(?:Mittente|Sender)\s*:\s*(.+?)(?:\n|$)", re.IGNORECASE | re.MULTILINE),
)

ARCHIVABLE_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/tiff",
    "image/gif",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/zip",
    "application/x-zip-compressed",
}


def decode_header_value(value) -> str:
    if value is None:
        return ""
    from email.header import decode_header as _dh
    parts = _dh(str(value))
    result = []
    for raw, charset in parts:
        if isinstance(raw, bytes):
            result.append(raw.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(raw)
    return "".join(result).strip()


def extract_real_sender(msg) -> str | None:
    """Tenta di trovare il mittente originale in email inoltrate."""
    subject = decode_header_value(msg.get("subject", ""))
    if not FORWARD_PREFIXES.match(subject.strip()):
        return None  # non sembra un inoltro

    # Cerca nel body text/plain
    for part in msg.walk():
        if part.get_content_type() != "text/plain":
            continue
        disp = str(part.get("Content-Disposition") or "")
        if "attachment" in disp.lower():
            continue
        payload = part.get_payload(decode=True)
        if not payload:
            continue
        charset = part.get_content_charset() or "utf-8"
        body = payload.decode(charset, errors="replace")
        for pat in REAL_SENDER_PATTERNS:
            m = pat.search(body)
            if m:
                return m.group(1).strip()

    return None


def is_junk(filename: str, content_type: str, disposition: str) -> bool:
    if JUNK_PATTERNS.match(filename or ""):
        return True
    if "inline" in (disposition or "").lower() and content_type.startswith("image/"):
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eml", required=True, help="Percorso file .eml")
    ap.add_argument("--out-dir", required=True, help="Directory dove salvare gli allegati")
    args = ap.parse_args()

    eml_path = Path(args.eml)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(eml_path, "rb") as f:
        raw = f.read()

    msg = BytesParser(policy=policy.default).parsebytes(raw)

    from_raw = decode_header_value(msg.get("from"))
    subject_raw = decode_header_value(msg.get("subject"))
    real_sender = extract_real_sender(msg)

    attachments = []
    skipped = []

    seen_names: dict[str, int] = {}

    for part in msg.walk():
        content_type = part.get_content_type()
        disposition = str(part.get("Content-Disposition") or "")
        filename = part.get_filename()
        if filename:
            filename = decode_header_value(filename)

        # Salta multipart containers
        if content_type.startswith("multipart/"):
            continue

        # Deve avere un filename o essere un tipo archiviabile con attachment disposition
        is_attachment = "attachment" in disposition.lower()
        has_filename = bool(filename and filename.strip())

        if not (is_attachment or (has_filename and content_type in ARCHIVABLE_TYPES)):
            continue

        if not has_filename:
            # Genera nome di fallback
            ext = content_type.split("/")[-1] if "/" in content_type else "bin"
            filename = f"allegato.{ext}"

        if is_junk(filename, content_type, disposition):
            skipped.append({"filename": filename, "reason": "junk/inline"})
            continue

        if content_type not in ARCHIVABLE_TYPES:
            skipped.append({"filename": filename, "reason": f"tipo non archiviabile: {content_type}"})
            continue

        # Deduplicazione nome file
        base_name = Path(filename).stem
        suffix = Path(filename).suffix or ".bin"
        if filename in seen_names:
            seen_names[filename] += 1
            save_name = f"{base_name}_{seen_names[filename]}{suffix}"
        else:
            seen_names[filename] = 0
            save_name = filename

        payload = part.get_payload(decode=True)
        if not payload:
            skipped.append({"filename": filename, "reason": "payload vuoto"})
            continue

        save_path = out_dir / save_name
        with open(save_path, "wb") as f:
            f.write(payload)

        attachments.append({
            "filename": save_name,
            "content_type": content_type,
            "size": len(payload),
            "saved_path": str(save_path),
        })

    result = {
        "eml": str(eml_path),
        "from_raw": from_raw,
        "subject_raw": subject_raw,
        "real_sender": real_sender,
        "attachments": attachments,
        "skipped": skipped,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
