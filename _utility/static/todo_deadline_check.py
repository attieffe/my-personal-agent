#!/usr/bin/env python3
"""
Scansiona i file TODO di myJob cercando scadenze.
Supporta:
  - scade DD/MM/YYYY  o  scade YYYY-MM-DD
  - entro DD/MM/YYYY  o  entro YYYY-MM-DD
  - [scade DD/MM/YYYY]
  - deadline: YYYY-MM-DD

Uso:
  python3 todo_deadline_check.py --mode today    # solo oggi
  python3 todo_deadline_check.py --mode week     # prossimi 7 giorni
  python3 todo_deadline_check.py --mode both     # oggi + prossimi 7 giorni
"""

import re
import sys
import argparse
from datetime import date, timedelta
from pathlib import Path

WORKSPACE = Path("/home/openclaw/.openclaw/workspace")

TODO_FILES = [
    WORKSPACE / "projects/myJob/TODO_GENERALE.md",
    WORKSPACE / "projects/myJob/PERSONALE/personale_tempo_libero/12_note_personali.md",
    WORKSPACE / "projects/myJob/COLZANI/TODO.md",
]

# Pattern: cattura data in formato DD/MM/YYYY o YYYY-MM-DD
DATE_PATTERNS = [
    # scade / entro + DD/MM/YYYY
    re.compile(
        r'(?:scade|entro|deadline[:\s])\s*(\d{1,2})/(\d{1,2})/(\d{4})',
        re.IGNORECASE
    ),
    # scade / entro + YYYY-MM-DD
    re.compile(
        r'(?:scade|entro|deadline[:\s])\s*(\d{4})-(\d{1,2})-(\d{1,2})',
        re.IGNORECASE
    ),
    # [scade DD/MM/YYYY]
    re.compile(
        r'\[scade\s+(\d{1,2})/(\d{1,2})/(\d{4})\]',
        re.IGNORECASE
    ),
    # [scade YYYY-MM-DD]
    re.compile(
        r'\[scade\s+(\d{4})-(\d{1,2})-(\d{1,2})\]',
        re.IGNORECASE
    ),
]

YMD_PATTERNS = [1, 3]  # indici dei pattern in formato YYYY-MM-DD (gruppi: anno, mese, giorno)
DMY_PATTERNS = [0, 2]  # indici dei pattern in formato DD/MM/YYYY (gruppi: giorno, mese, anno)


def parse_date_from_match(pattern_idx, match) -> date | None:
    try:
        g = match.groups()
        if pattern_idx in YMD_PATTERNS:
            return date(int(g[0]), int(g[1]), int(g[2]))
        else:
            return date(int(g[2]), int(g[1]), int(g[0]))
    except ValueError:
        return None


def extract_deadlines(filepath: Path) -> list[tuple[date, str, str]]:
    """Restituisce lista di (data_scadenza, descrizione_task, nome_file)"""
    results = []
    if not filepath.exists():
        return results

    file_label = filepath.name
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            # considera solo righe con task aperto: "- [ ]" o "- [~]"
            if not re.match(r'^-\s+\[[ ~]\]', stripped):
                continue
            for idx, pat in enumerate(DATE_PATTERNS):
                m = pat.search(stripped)
                if m:
                    d = parse_date_from_match(idx, m)
                    if d:
                        # pulisce la riga per la descrizione
                        desc = re.sub(r'^-\s+\[[ ~]\]\s*', '', stripped)
                        results.append((d, desc, file_label))
                    break  # un solo match per riga
    return results


def format_items(items: list[tuple[date, str, str]], oggi: date) -> str:
    lines = []
    for d, desc, src in sorted(items, key=lambda x: x[0]):
        delta = (d - oggi).days
        if delta == 0:
            label = "⚠️ OGGI"
        elif delta == 1:
            label = "domani"
        else:
            label = f"tra {delta} giorni"
        lines.append(f"• {d.strftime('%d/%m/%Y')} ({label}) — {desc}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["today", "week", "both"], default="both")
    args = parser.parse_args()

    oggi = date.today()
    fine_settimana = oggi + timedelta(days=7)

    all_deadlines = []
    for f in TODO_FILES:
        all_deadlines.extend(extract_deadlines(f))

    today_items = [(d, desc, src) for d, desc, src in all_deadlines if d == oggi]
    week_items = [(d, desc, src) for d, desc, src in all_deadlines
                  if oggi < d <= fine_settimana]

    output_parts = []

    if args.mode in ("today", "both") and today_items:
        output_parts.append("📅 *Scadenze di OGGI:*\n" + format_items(today_items, oggi))

    if args.mode in ("week", "both") and week_items:
        output_parts.append("🗓 *In scadenza nei prossimi 7 giorni:*\n" + format_items(week_items, oggi))

    if output_parts:
        print("\n\n".join(output_parts))


if __name__ == "__main__":
    main()
