"""
Orchestratore principale archiviazione documenti.

Comandi:
  analyze <file>           Analizza file in input/, stampa proposta JSON
  execute <proposta_json>  Esegue archiviazione confermata, aggiorna history.md
  list                     Lista file in attesa in input/
"""
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).parent.parent
INPUT_DIR = BASE / "input"
PROCESSED_DIR = BASE / "90_processed"
HISTORY_FILE = BASE / "history.md"
TZ = ZoneInfo("Europe/Rome")

sys.path.insert(0, str(Path(__file__).parent))
import vision_namer
import drive_uploader


def cmd_list():
    files = [f for f in INPUT_DIR.iterdir() if f.is_file() and f.name != ".gitkeep"]
    if not files:
        print("Nessun file in attesa in input/")
        return
    print(f"{len(files)} file in input/:")
    for f in sorted(files):
        size = f.stat().st_size
        print(f"  {f.name}  ({size // 1024} KB)")


def cmd_analyze(file_arg: str):
    path = Path(file_arg)
    if not path.is_absolute():
        path = INPUT_DIR / file_arg
    if not path.exists():
        print(f"ERRORE: file non trovato: {path}", file=sys.stderr)
        sys.exit(1)

    print(f"Analisi in corso: {path.name} ...", file=sys.stderr)
    analysis = vision_namer.analyze(str(path))
    destinations = drive_uploader.build_destinations(analysis)

    proposal = {
        "file_path": str(path),
        "file_originale": path.name,
        "data_documento": analysis.get("data_documento"),
        "nome_proposto": analysis.get("nome_proposto"),
        "categoria": analysis.get("categoria"),
        "mittente": analysis.get("mittente"),
        "importo": analysis.get("importo"),
        "note": analysis.get("note"),
        "confidenza_data": analysis.get("confidenza_data"),
        "filename_finale": f"{analysis.get('data_documento', '00000000')} {analysis.get('nome_proposto', 'documento')}{path.suffix.lower()}",
        "destinazioni": destinations,
    }

    print(json.dumps(proposal, ensure_ascii=False, indent=2))


def cmd_execute(proposal_json: str):
    proposal = json.loads(proposal_json)
    file_path = Path(proposal["file_path"])

    if not file_path.exists():
        print(f"ERRORE: file non trovato: {file_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Archiviazione: {file_path.name} ...", file=sys.stderr)
    results = drive_uploader.upload(str(file_path), proposal["destinazioni"])

    all_ok = all(r["ok"] for r in results)
    now = datetime.now(TZ)
    timestamp = now.strftime("%Y-%m-%d %H:%M")

    # Aggiorna history.md
    entry = _build_history_entry(proposal, results, timestamp, all_ok)
    _prepend_history(entry)

    # Sposta in 90_processed/ (mai cancella)
    dest_processed = PROCESSED_DIR / file_path.name
    if dest_processed.exists():
        # Evita sovrascrittura
        stem = file_path.stem
        dest_processed = PROCESSED_DIR / f"{stem}_{now.strftime('%H%M%S')}{file_path.suffix}"
    shutil.move(str(file_path), str(dest_processed))

    output = {
        "ok": all_ok,
        "timestamp": timestamp,
        "file_archiviato": proposal["filename_finale"],
        "spostato_in": str(dest_processed),
        "destinazioni": results,
        "history_aggiornata": True,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))

    if not all_ok:
        failed = [r["destination"] for r in results if not r["ok"]]
        print(f"\nATTENZIONE: {len(failed)} destinazioni fallite:", file=sys.stderr)
        for f in failed:
            print(f"  {f}", file=sys.stderr)
        sys.exit(2)


def _build_history_entry(proposal: dict, results: list, timestamp: str, all_ok: bool) -> str:
    dest_lines = ""
    for r in results:
        stato = "✅" if r["ok"] else "❌"
        dest_lines += f"  - `{r['destination']}` {stato}\n"
        if not r["ok"] and r.get("output"):
            dest_lines += f"    Errore: {r['output'][:100]}\n"

    importo_str = f"\n- **Importo:** {proposal['importo']}" if proposal.get("importo") else ""
    mittente_str = f"\n- **Mittente:** {proposal['mittente']}" if proposal.get("mittente") else ""
    note_str = f"\n- **Note:** {proposal['note']}" if proposal.get("note") else ""

    return f"""## {timestamp} — {proposal['filename_finale']}
- **Categoria:** {proposal['categoria']}
- **Data documento:** {proposal['data_documento']}{mittente_str}{importo_str}
- **File originale:** `{proposal['file_originale']}`
- **Destinazioni:**
{dest_lines}{note_str}
---

"""


def _prepend_history(entry: str):
    HISTORY_FILE.touch(exist_ok=True)
    content = HISTORY_FILE.read_text(encoding="utf-8")

    # Inserisci dopo l'header (la riga con <!-- ... -->)
    marker = "---\n\n<!-- Esempio"
    if marker in content:
        parts = content.split(marker, 1)
        new_content = parts[0] + "---\n\n" + entry + "<!-- Esempio" + parts[1]
    else:
        # Inserisci all'inizio dopo il titolo
        lines = content.splitlines(keepends=True)
        insert_at = 1
        for i, line in enumerate(lines):
            if line.strip() == "---":
                insert_at = i + 1
                break
        lines.insert(insert_at, "\n" + entry)
        new_content = "".join(lines)

    HISTORY_FILE.write_text(new_content, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "list":
        cmd_list()
    elif cmd == "analyze" and len(sys.argv) >= 3:
        cmd_analyze(sys.argv[2])
    elif cmd == "execute" and len(sys.argv) >= 3:
        cmd_execute(sys.argv[2])
    else:
        print(f"Comando non valido: {cmd}", file=sys.stderr)
        print(__doc__)
        sys.exit(1)
