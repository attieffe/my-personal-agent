#!/bin/bash
# call-log-join.sh — Fase 2 (Join)
#
# Registra in META.md l'orario di join del bot (Attilio F.).
#
# Uso: ./call-log-join.sh <call_dir>

set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "Uso: $0 <call_dir>" >&2
    exit 2
fi

CALL_DIR="$1"
META="$CALL_DIR/META.md"

if [ ! -f "$META" ]; then
    echo "ERRORE: META.md non trovato in $CALL_DIR" >&2
    exit 3
fi

NOW_FULL="$(TZ=Europe/Rome date +'%Y-%m-%d %H:%M')"
NOW_HM="$(TZ=Europe/Rome date +'%H:%M')"

# 1) Aggiorna riga "Bot join" nella sezione Info call
#    Sostituisce la prima occorrenza di "- **Bot join:**" con il timestamp.
python3 - "$META" "$NOW_FULL" "$NOW_HM" <<'PY'
import sys, re, pathlib
meta_path = pathlib.Path(sys.argv[1])
full_ts   = sys.argv[2]
hm        = sys.argv[3]
text = meta_path.read_text()

# Aggiorna riga Bot join (solo la prima occorrenza)
text2, n = re.subn(
    r'^- \*\*Bot join:\*\*.*$',
    f'- **Bot join:** {full_ts} (Europe/Rome)',
    text,
    count=1,
    flags=re.MULTILINE,
)

# Aggiorna entrata del bot nella tabella partecipanti
text2, _ = re.subn(
    r'^\| Attilio F\. \(bot\) \| [^|]*\| ([^|]*)\|',
    lambda m: f'| Attilio F. (bot) | {hm} | {m.group(1).strip()} |' if False else f'| Attilio F. (bot) | {hm} | {m.group(1)}|',
    text2,
    count=1,
    flags=re.MULTILINE,
)

meta_path.write_text(text2)
PY

echo "Bot join: $NOW_FULL"
