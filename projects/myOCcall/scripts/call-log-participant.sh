#!/bin/bash
# call-log-participant.sh — Fase 3 (In-call monitoring)
#
# Aggiorna la tabella partecipanti in META.md con un evento di join o leave.
#
# Uso: ./call-log-participant.sh <call_dir> <nome> <evento>
#   <evento>: join | leave

set -euo pipefail

if [ "$#" -lt 3 ]; then
    echo "Uso: $0 <call_dir> <nome> <join|leave>" >&2
    exit 2
fi

CALL_DIR="$1"
NAME="$2"
EVENT="$3"

if [ "$EVENT" != "join" ] && [ "$EVENT" != "leave" ]; then
    echo "ERRORE: evento deve essere 'join' o 'leave' (ricevuto: $EVENT)" >&2
    exit 2
fi

META="$CALL_DIR/META.md"
if [ ! -f "$META" ]; then
    echo "ERRORE: META.md non trovato in $CALL_DIR" >&2
    exit 3
fi

NOW_HM="$(TZ=Europe/Rome date +'%H:%M')"

python3 - "$META" "$NAME" "$EVENT" "$NOW_HM" <<'PY'
import sys, re, pathlib

meta_path = pathlib.Path(sys.argv[1])
name      = sys.argv[2]
event     = sys.argv[3]
hm        = sys.argv[4]

text = meta_path.read_text()
lines = text.splitlines(keepends=False)

# Trova la sezione tabella partecipanti
# Convenzione: parte dopo "## Partecipanti" e termina alla riga vuota o prossima sezione
hdr_idx = None
for i, l in enumerate(lines):
    if l.strip() == "## Partecipanti":
        hdr_idx = i
        break

if hdr_idx is None:
    sys.stderr.write("Sezione '## Partecipanti' non trovata\n")
    sys.exit(4)

# Trova l'inizio della tabella (riga "| Nome ...")
table_start = None
for i in range(hdr_idx + 1, len(lines)):
    if lines[i].startswith("| Nome"):
        table_start = i
        break
if table_start is None:
    sys.stderr.write("Header tabella partecipanti non trovato\n")
    sys.exit(4)

# Trova fine tabella (prima riga che non comincia per "|")
table_end = len(lines)
for i in range(table_start + 1, len(lines)):
    if not lines[i].startswith("|"):
        table_end = i
        break

# Le righe dati sono table_start+2 .. table_end-1 (la +1 è il separatore "|---|---|")
data_start = table_start + 2
data_rows = lines[data_start:table_end]

def split_row(r):
    # "| nome | entrata | uscita |"
    parts = [p.strip() for p in r.strip().strip("|").split("|")]
    while len(parts) < 3:
        parts.append("")
    return parts[0], parts[1], parts[2]

def build_row(n, e, u):
    return f"| {n} | {e if e else '—'} | {u if u else '—'} |"

found = False
new_rows = []
for r in data_rows:
    n, e, u = split_row(r)
    if n.lower() == name.lower() and not found:
        found = True
        if event == "join":
            # Se già ha un'entrata e un'uscita "—", aggiorna entrata.
            # Se già ha entrata e uscita popolate, crea nuova riga (rientrato).
            if e and e != "—" and u and u != "—":
                # rientro: mantieni la riga precedente e aggiungi nuova
                new_rows.append(build_row(n, e, u))
                new_rows.append(build_row(n, hm, "—"))
            else:
                new_rows.append(build_row(n, hm if not e or e == "—" else e, u))
        else:  # leave
            new_rows.append(build_row(n, e, hm))
    else:
        new_rows.append(build_row(n, e, u))

if not found:
    if event == "join":
        new_rows.append(build_row(name, hm, "—"))
    else:
        new_rows.append(build_row(name, "—", hm))

new_lines = lines[:data_start] + new_rows + lines[table_end:]
meta_path.write_text("\n".join(new_lines) + ("\n" if text.endswith("\n") else ""))
PY

echo "Partecipante: $NAME — $EVENT @ $NOW_HM"
