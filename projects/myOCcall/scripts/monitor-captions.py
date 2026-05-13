#!/usr/bin/env python3
"""Monitor Google Meet captions, snapshot ogni 60s → live-captions.txt"""
import subprocess, time, hashlib, re, sys
from datetime import datetime
import pytz

CAPTION_FILE = "/home/openclaw/.openclaw/workspace/projects/myOCcall/data/live-captions.txt"
TARGET = "meet"
INTERVAL = 60
rome = pytz.timezone('Europe/Rome')


def ts():
    return datetime.now(rome).strftime('[%Y-%m-%d %H:%M:%S Europe/Rome]')


def get_captions():
    r = subprocess.run(
        ['openclaw', 'browser', 'snapshot', '--target-id', TARGET],
        capture_output=True, text=True, timeout=30
    )
    lines = r.stdout.split('\n')

    cap_start = next((i for i, l in enumerate(lines) if 'region "Captions"' in l), None)
    if cap_start is None:
        return ''

    base_indent = len(lines[cap_start]) - len(lines[cap_start].lstrip())
    texts = []

    for line in lines[cap_start + 1:]:
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= base_indent:
            break
        m = re.search(r'\]: (.+)$', line)
        if m:
            text = m.group(1).strip()
            # skip refs, empty strings, single punctuation
            if text and not text.startswith('[') and len(text) > 2:
                texts.append(text)

    return ' | '.join(texts)


def append(line):
    with open(CAPTION_FILE, 'a') as f:
        f.write(line + '\n')
        f.flush()
    print(line, flush=True)


if __name__ == '__main__':
    append(f'{ts()} === MONITORAGGIO CAPTIONS AVVIATO ===')
    prev_hash = ''

    while True:
        time.sleep(INTERVAL)
        try:
            captions = get_captions()
            if not captions:
                continue
            h = hashlib.md5(captions.encode()).hexdigest()
            if h == prev_hash:
                continue
            prev_hash = h
            append(f'{ts()} {captions}')
        except subprocess.TimeoutExpired:
            append(f'{ts()} WARN: snapshot timeout')
        except Exception as e:
            append(f'{ts()} ERROR: {e}')
