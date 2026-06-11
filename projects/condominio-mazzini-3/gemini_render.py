#!/usr/bin/env python3
"""
Condominio Mazzini 3 — Gemini Rendering Pipeline
Legge RENDERING_QUEUE.json, genera una proposta completa (3 foto),
salva le immagini, marca il task come done, restituisce msg di notifica.

Exit codes: 0=ok, 1=errore, 2=no pending, 3=billing required
"""
import json
import os
import sys
import pathlib
import datetime
import time

BASE_DIR  = "/home/openclaw/attibot/condominio"
QUEUE     = "/home/openclaw/.openclaw/workspace/projects/condominio-mazzini-3/RENDERING_QUEUE.json"
IMG_DIR   = f"{BASE_DIR}/img"
ORIG_DIR  = f"{BASE_DIR}/img/originali"

GEMINI_KEY = None
env_file = f"{BASE_DIR}/.env"
if os.path.exists(env_file):
    for line in pathlib.Path(env_file).read_text().splitlines():
        if line.startswith("GEMINI_API_KEY="):
            GEMINI_KEY = line.split("=", 1)[1].strip()

MODELS = [
    "gemini-3.1-flash-image",
    "gemini-3.1-flash-image-preview",
    "gemini-3-pro-image",
    "gemini-3-pro-image-preview",
]

PHOTOS = [
    {"file": "foto1.jpg", "focus": "FOTO1_FACCIATA"},
    {"file": "foto2.jpg", "focus": "FOTO2_BALCONI"},
    {"file": "foto3.jpg", "focus": "FOTO3_DETTAGLI"},
    {"file": "foto4.jpg", "focus": "FOTO4_LATERALE"},
]

_SYSTEM_DIR = pathlib.Path(__file__).parent / "_system"

# ---------------------------------------------------------------------------
# Prompt — caricato da _system/, colori come pure variabili
# ---------------------------------------------------------------------------

def _load_focus_templates():
    path = _SYSTEM_DIR / "focus_templates.txt"
    content = path.read_text()
    templates = {}
    current_key = None
    lines = []
    for line in content.splitlines():
        if line.startswith("[") and line.endswith("]") and not line.startswith("#"):
            if current_key:
                templates[current_key] = "\n".join(lines).strip()
            current_key = line[1:-1]
            lines = []
        elif current_key and not line.startswith("#"):
            lines.append(line)
    if current_key:
        templates[current_key] = "\n".join(lines).strip()
    return templates

_PROMPT_TEMPLATE = (_SYSTEM_DIR / "prompt_template.txt").read_text()
_FOCUS_TEMPLATES = _load_focus_templates()


def make_prompt(proposal, focus):
    dom = proposal["dominant"]
    sec = proposal["secondary"]
    acc = proposal.get("accessory", {})

    acc_line = ""
    if acc.get("hex"):
        acc_line = f"• ACCESSORI — contorni finestre, pilastri, bordi strutturali, soglie: {acc['hex']} · {acc['name']} · {acc.get('code', '')}"

    focus_key = focus if focus in _FOCUS_TEMPLATES else "FOTO1_FACCIATA"
    focus_desc = _FOCUS_TEMPLATES[focus_key]

    return _PROMPT_TEMPLATE.format(
        PROPOSAL_TITLE=proposal["title"],
        DOMINANT_HEX=dom["hex"],
        DOMINANT_NAME=dom["name"],
        DOMINANT_CODE=dom.get("code", ""),
        SECONDARY_HEX=sec["hex"],
        SECONDARY_NAME=sec["name"],
        SECONDARY_CODE=sec.get("code", ""),
        ACCESSORY_LINE=acc_line,
        FOCUS_DESC=focus_desc,
    )


# ---------------------------------------------------------------------------
# Generazione Gemini
# ---------------------------------------------------------------------------

def generate_images(proposal):
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GEMINI_KEY)
    code = proposal["code"]
    results = []

    for i, photo in enumerate(PHOTOS, 1):
        src = os.path.join(ORIG_DIR, photo["file"])
        dst = os.path.join(IMG_DIR, f"{code}_foto{i}.jpg")

        img_bytes = pathlib.Path(src).read_bytes()
        prompt_text = make_prompt(proposal, photo["focus"])

        last_err = None
        for model in MODELS:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=[
                        types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                        types.Part.from_text(text=prompt_text),
                    ],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE", "TEXT"]
                    ),
                )
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "inline_data") and part.inline_data:
                        pathlib.Path(dst).write_bytes(part.inline_data.data)
                        results.append(f"img/{code}_foto{i}.jpg")
                        print(f"  ✅ {code}_foto{i}.jpg ({model})")
                        last_err = None
                        break
                if last_err is None:
                    break
            except Exception as e:
                err_str = str(e)
                last_err = err_str
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    # Billing required — stop immediately, no point trying other models
                    raise RuntimeError(f"BILLING_REQUIRED: {err_str[:200]}")
                print(f"  ⚠️  {model}: {err_str[:120]}")
                time.sleep(2)

        if last_err and "BILLING_REQUIRED" not in last_err:
            raise RuntimeError(f"All Gemini models failed for foto{i}: {last_err}")

    return results


# ---------------------------------------------------------------------------
# Queue management
# ---------------------------------------------------------------------------

def read_queue():
    with open(QUEUE) as f:
        return json.load(f)

def write_queue(data):
    data["last_updated"] = now_iso()
    with open(QUEUE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def now_iso():
    tz = datetime.timezone(datetime.timedelta(hours=2))
    return datetime.datetime.now(tz).isoformat()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not GEMINI_KEY:
        print("ERROR: GEMINI_API_KEY not found in .env")
        return 1

    data = read_queue()
    pending = [item for item in data["queue"] if item["status"] == "pending"]

    if not pending:
        print("NO_PENDING: Queue is empty, nothing to do.")
        return 2

    proposal = pending[0]
    code = proposal["code"]
    print(f"\n→ Processing {code} — {proposal['title']}")
    print(f"  Remaining after this: {len(pending)-1}")

    try:
        images = generate_images(proposal)

        # Mark done
        for item in data["queue"]:
            if item["code"] == code:
                item["status"] = "done"
                item["done"] = now_iso()
                item["output_images"] = images
        write_queue(data)

        remaining = len(pending) - 1
        url = f"https://attibot.ingeniosolution.it/reports/condominio/proposte_facciate.html#{code}"
        print(f"\nNOTIFY: ✅ Rendering {code} completato ({proposal['title'][:35]}). "
              f"Rimangono {remaining} proposte. Vedi: {url}")
        return 0

    except RuntimeError as e:
        err = str(e)
        if "BILLING_REQUIRED" in err:
            print(f"\nBILLING_REQUIRED: Gemini image generation richiede fatturazione attiva su Google AI Studio.")
            return 3
        print(f"\nERROR: {err}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
