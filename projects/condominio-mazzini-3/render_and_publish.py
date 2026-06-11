#!/usr/bin/env python3
"""
Wrapper: esegue gemini_render.py, aggiorna la pagina HTML, notifica Telegram.
Exit codes: 0=ok (rendered+published), 2=no pending, 3=billing, 1=error
"""
import subprocess
import sys
import re
import json
import html as html_lib
import pathlib
import os

HTML_PATH = "/home/openclaw/attibot/reports/condominio/proposte_facciate.html"
RENDER_SCRIPT = "/home/openclaw/.openclaw/workspace/projects/condominio-mazzini-3/gemini_render.py"
QUEUE = "/home/openclaw/.openclaw/workspace/projects/condominio-mazzini-3/RENDERING_QUEUE.json"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gemini_render import make_prompt


def text_color(hex_color):
    h = hex_color.lstrip('#')
    if len(h) != 6:
        return 'rgba(0,0,0,0.75)'
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return 'rgba(0,0,0,0.75)' if lum > 0.5 else 'rgba(255,255,255,0.9)'


def build_render_summary(proposal):
    def swatch_html(color, label):
        if not color or not color.get("hex"):
            return ""
        tc = text_color(color["hex"])
        name = html_lib.escape(color.get("name", ""))
        hex_val = html_lib.escape(color.get("hex", ""))
        code = html_lib.escape(color.get("code", ""))
        name_full = f"{name} · {code}" if code else name
        return (
            f'<div class="rpal-swatch" style="background:{color["hex"]};color:{tc};">'
            f'<span class="rpal-label">{label}</span>'
            f'<span class="rpal-name">{name_full}</span>'
            f'<span class="rpal-hex">{hex_val}</span>'
            f'</div>'
        )

    palette_html = (
        '<div class="render-palette">'
        + swatch_html(proposal.get("dominant"), "Dominante")
        + swatch_html(proposal.get("secondary"), "Secondario")
        + swatch_html(proposal.get("accessory"), "Accessori")
        + '</div>'
    )

    prompt_text = html_lib.escape(make_prompt(proposal, "FOTO1_FACCIATA"))
    prompt_html = (
        '<details class="prompt-details">'
        '<summary>📝 Prompt rendering (facciata)</summary>'
        f'<pre class="prompt-text">{prompt_text}</pre>'
        '</details>'
    )

    return f'\n            <div class="render-summary">{palette_html}{prompt_html}</div>'


def count_done():
    q = json.load(open(QUEUE))
    return sum(1 for x in q["queue"] if x["status"] == "done"), len(q["queue"])


def get_proposal(code):
    q = json.load(open(QUEUE))
    return next((x for x in q["queue"] if x["code"] == code), None)


def _find_div_end(html, abs_start):
    """Trova la posizione di chiusura del div aperto in abs_start."""
    depth = 0
    pos = abs_start
    while pos < len(html):
        if html[pos:pos+4] == '<div':
            depth += 1; pos += 4
        elif html[pos:pos+6] == '</div>':
            depth -= 1
            if depth == 0:
                return pos + 6
            pos += 6
        else:
            pos += 1
    return None


def enable_card(code, proposal=None):
    """Sostituisce card-photo pending con rendered + inietta render-summary."""
    html = pathlib.Path(HTML_PATH).read_text()
    card_start = html.find(f'id="card-{code}"')
    if card_start == -1:
        return False
    seg = html[card_start:card_start + 4000]
    ph = seg.find('<div class="card-photo pending">')
    if ph == -1:
        return False  # already rendered
    abs_start = card_start + ph
    abs_end = _find_div_end(html, abs_start)
    if abs_end is None:
        return False

    rendered = (
        f'<div class="card-photo rendered">\n'
        f'              <img class="slide active" src="img/{code}_foto1.jpg" alt="Foto 1 — Facciata principale">\n'
        f'              <img class="slide" src="img/{code}_foto2.jpg" alt="Foto 2 — Balconi e fasce">\n'
        f'              <img class="slide" src="img/{code}_foto3.jpg" alt="Foto 3 — Dettagli">\n'
        f'              <img class="slide" src="img/{code}_foto4.jpg" alt="Foto 4 — Facciata laterale">\n'
        f'              <div class="photo-dots">\n'
        f'                <span class="dot active" onclick="switchSlide(\'{code}\',0)"></span>\n'
        f'                <span class="dot" onclick="switchSlide(\'{code}\',1)"></span>\n'
        f'                <span class="dot" onclick="switchSlide(\'{code}\',2)"></span>\n'
        f'                <span class="dot" onclick="switchSlide(\'{code}\',3)"></span>\n'
        f'              </div>\n'
        f'            </div>'
    )

    summary = build_render_summary(proposal) if proposal else ''
    html = html[:abs_start] + rendered + summary + html[abs_end:]

    done, total = count_done()
    html = re.sub(
        r'🖼️ Rendering: <strong>\d+ / \d+</strong> completati',
        f'🖼️ Rendering: <strong>{done} / {total}</strong> completati',
        html
    )
    pathlib.Path(HTML_PATH).write_text(html)
    return True


def retroactive_add_summaries():
    """Aggiunge render-summary alle card già renderizzate che non ce l'hanno."""
    q = json.load(open(QUEUE))
    done_proposals = [x for x in q["queue"] if x["status"] == "done"]
    if not done_proposals:
        return

    html = pathlib.Path(HTML_PATH).read_text()
    changed = False

    for proposal in done_proposals:
        code = proposal["code"]
        card_start = html.find(f'id="card-{code}"')
        if card_start == -1:
            continue

        card_seg_len = 10000
        card_seg = html[card_start:card_start + card_seg_len]

        # Salta se render-summary è già presente prima di card-body
        body_pos = card_seg.find('class="card-body"')
        summary_pos = card_seg.find('class="render-summary"')
        if summary_pos != -1 and (body_pos == -1 or summary_pos < body_pos):
            continue  # già presente

        ph = card_seg.find('<div class="card-photo rendered">')
        if ph == -1:
            continue

        abs_start = card_start + ph
        abs_end = _find_div_end(html, abs_start)
        if abs_end is None:
            continue

        summary = build_render_summary(proposal)
        html = html[:abs_end] + summary + html[abs_end:]
        changed = True

    if changed:
        pathlib.Path(HTML_PATH).write_text(html)
        print(f"  retroactive: aggiornate {len(done_proposals)} card con palette+prompt")


def main():
    retroactive_add_summaries()

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

    m = re.search(r'NOTIFY:\s*(.+)', out)
    if m:
        msg = m.group(1).strip()
        code_m = re.search(r'Rendering\s+([A-Z]\d+)\s+completato', msg)
        if code_m:
            code = code_m.group(1)
            proposal = get_proposal(code)
            updated = enable_card(code, proposal)
            if updated:
                msg += " — Pagina aggiornata ✅"
        print(f"NOTIFY: {msg}")
        return 0

    print(out)
    return result.returncode if result.returncode != 0 else 1


if __name__ == "__main__":
    sys.exit(main())
