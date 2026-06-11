#!/usr/bin/env python3
"""
Wrapper: esegue gemini_render.py, aggiorna la pagina HTML, notifica Telegram.
Exit codes: 0=ok (rendered+published), 2=no pending, 3=billing, 1=error
"""
import subprocess
import sys
import re
import pathlib

HTML_PATH = "/home/openclaw/attibot/reports/condominio/proposte_facciate.html"
RENDER_SCRIPT = "/home/openclaw/.openclaw/workspace/projects/condominio-mazzini-3/gemini_render.py"

def count_done():
    import json
    q = json.load(open("/home/openclaw/.openclaw/workspace/projects/condominio-mazzini-3/RENDERING_QUEUE.json"))
    return sum(1 for x in q["queue"] if x["status"] == "done"), len(q["queue"])

def enable_card(code):
    html = pathlib.Path(HTML_PATH).read_text()
    card_start = html.find(f'id="card-{code}"')
    if card_start == -1:
        return False
    seg = html[card_start:card_start+4000]
    ph = seg.find('<div class="card-photo pending">')
    if ph == -1:
        return False  # already rendered
    abs_start = card_start + ph
    depth = 0
    pos = abs_start
    while pos < len(html):
        if html[pos:pos+4] == '<div':
            depth += 1; pos += 4
        elif html[pos:pos+6] == '</div>':
            depth -= 1
            if depth == 0:
                abs_end = pos + 6; break
            pos += 6
        else:
            pos += 1
    rendered = (
        f'<div class="card-photo rendered">\n'
        f'              <img class="slide active" src="img/{code}_foto1.jpg" alt="Foto 1">\n'
        f'              <img class="slide" src="img/{code}_foto2.jpg" alt="Foto 2">\n'
        f'              <img class="slide" src="img/{code}_foto3.jpg" alt="Foto 3">\n'
        f'              <div class="photo-dots">\n'
        f'                <span class="dot active" onclick="switchSlide(\'{code}\',0)"></span>\n'
        f'                <span class="dot" onclick="switchSlide(\'{code}\',1)"></span>\n'
        f'                <span class="dot" onclick="switchSlide(\'{code}\',2)"></span>\n'
        f'              </div>\n'
        f'            </div>'
    )
    html = html[:abs_start] + rendered + html[abs_end:]

    # Aggiorna status bar
    done, total = count_done()
    html = re.sub(
        r'🖼️ Rendering: <strong>\d+ / \d+</strong> completati',
        f'🖼️ Rendering: <strong>{done} / {total}</strong> completati',
        html
    )
    pathlib.Path(HTML_PATH).write_text(html)
    return True

def main():
    result = subprocess.run(
        [sys.executable, RENDER_SCRIPT],
        capture_output=True, text=True,
        cwd="/home/openclaw/attibot/condominio"
    )
    out = result.stdout + result.stderr

    if "NO_PENDING" in out:
        print("NO_PENDING")
        return 2

    if "BILLING_REQUIRED" in out:
        print("BILLING_REQUIRED")
        return 3

    # Cerca riga NOTIFY
    m = re.search(r'NOTIFY:\s*(.+)', out)
    if m:
        msg = m.group(1).strip()
        # Estrai codice proposta dalla riga NOTIFY (es. "B5")
        code_m = re.search(r'Rendering\s+([A-Z]\d+)\s+completato', msg)
        if code_m:
            code = code_m.group(1)
            updated = enable_card(code)
            if updated:
                msg += " — Pagina aggiornata ✅"
        print(f"NOTIFY: {msg}")
        return 0

    # Fallback: stampa output grezzo
    print(out)
    return result.returncode if result.returncode != 0 else 1

if __name__ == "__main__":
    sys.exit(main())
