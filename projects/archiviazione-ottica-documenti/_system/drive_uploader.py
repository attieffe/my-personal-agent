"""
Copia file su Google Drive via rclone (remote: gdrive).
Gestisce le destinazioni multiple secondo le regole di archiviazione.
"""
import subprocess
import sys
from pathlib import Path


RCLONE_REMOTE = "gdrive"


def _rclone_copy(src: str, dst_remote: str) -> tuple[bool, str]:
    """Esegue rclone copy. Ritorna (successo, output)."""
    cmd = ["rclone", "copy", src, f"{RCLONE_REMOTE}:{dst_remote}", "--progress"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    ok = result.returncode == 0
    output = result.stdout + result.stderr
    return ok, output


def _rclone_copyto(src: str, dst_remote_path: str) -> tuple[bool, str]:
    """Copia un file rinominandolo in destinazione (rclone copyto)."""
    cmd = ["rclone", "copyto", "--drive-shared-with-me", src, f"{RCLONE_REMOTE}:{dst_remote_path}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    ok = result.returncode == 0
    output = result.stdout + result.stderr
    return ok, output


def upload(src_path: str, destinations: list[dict]) -> list[dict]:
    """
    Carica il file in tutte le destinazioni indicate.

    destinations: lista di dict con:
      - path: str  (path su Drive, senza gdrive:)
      - filename: str  (nome finale del file su Drive)

    Ritorna lista di risultati con ok/errore per ogni destinazione.
    """
    results = []
    for dest in destinations:
        drive_path = dest["path"]
        filename = dest["filename"]
        full_remote = f"{drive_path}/{filename}"

        ok, output = _rclone_copyto(src_path, full_remote)
        results.append({
            "destination": f"gdrive:{full_remote}",
            "ok": ok,
            "output": output.strip() if not ok else "",
        })

    return results


def build_destinations(analysis: dict) -> list[dict]:
    """
    Costruisce la lista di destinazioni Drive in base alla categoria
    e alla data estratta dal documento.
    """
    categoria = analysis.get("categoria", "ALTRO")
    data_raw = analysis.get("data_documento", "00000000")
    nome = analysis.get("nome_proposto", "documento")
    file_orig = analysis.get("file_originale", "file.jpg")
    ext = Path(file_orig).suffix.lower()

    # Normalizza data
    anno = data_raw[:4] if len(data_raw) >= 4 and data_raw != "00000000" else "0000"
    filename = f"{data_raw} {nome}{ext}"

    destinations = []

    if categoria == "CERTIFICATI_SANITARI":
        # Va SOLO in Sanità (non in Archiviazione ottica)
        destinations.append({
            "path": "Atti/Documenti/Sanità",
            "filename": filename,
        })
    else:
        # Destinazione primaria: sempre (tranne CERTIFICATI_SANITARI)
        destinations.append({
            "path": f"Atti/Documenti/Archiviazione ottica/{anno}",
            "filename": filename,
        })

        if categoria == "SPESE_MEDICHE" and anno != "0000":
            anno_dichiarazione = str(int(anno) + 1)
            destinations.append({
                "path": f"Atti/Documenti/DICHIARAZIONE DEI REDDITI/{anno_dichiarazione}x{anno}",
                "filename": filename,
            })

        elif categoria == "INGENIO_SOLUTION":
            destinations.append({
                "path": f"Ingenio/DOCUMENTI FISCALI/{anno}",
                "filename": filename,
            })

    return destinations


if __name__ == "__main__":
    import json
    if len(sys.argv) < 3:
        print("Uso: python drive_uploader.py <file> '<destinations_json>'", file=sys.stderr)
        sys.exit(1)
    src = sys.argv[1]
    dests = json.loads(sys.argv[2])
    results = upload(src, dests)
    print(json.dumps(results, ensure_ascii=False, indent=2))
