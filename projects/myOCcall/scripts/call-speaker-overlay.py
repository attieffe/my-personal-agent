#!/usr/bin/env python3
"""
call-speaker-overlay.py <call_dir>

Allinea speaker-events.jsonl con transcript-events.jsonl e produce
trascrizione_attribuita.md con formato [HH:MM:SS] Nome: testo.

Richiede in META.md: ffmpeg_start_epoch_ms
"""
import json
import re
import sys
from pathlib import Path


def parse_meta_field(meta_text, key):
    m = re.search(rf'- \*\*{re.escape(key)}:\*\*\s*(\S+)', meta_text)
    return m.group(1) if m else None


def fmt_time(call_sec):
    call_sec = max(0.0, call_sec)
    h = int(call_sec // 3600)
    m = int((call_sec % 3600) // 60)
    s = int(call_sec % 60)
    return f'{h:02d}:{m:02d}:{s:02d}'


def find_speaker(start, end, speaker_events):
    if not speaker_events:
        return 'Sconosciuto'

    # Costruisce intervalli (ev_start, ev_end, speaker)
    intervals = []
    for i, ev in enumerate(speaker_events):
        ev_start = ev['call_sec']
        ev_end = speaker_events[i + 1]['call_sec'] if i + 1 < len(speaker_events) else float('inf')
        intervals.append((ev_start, ev_end, ev['speaker']))

    # Calcola overlap con [start, end]
    overlap = {}
    for iv_start, iv_end, spk in intervals:
        ov = max(0.0, min(iv_end, end) - max(iv_start, start))
        if ov > 0:
            overlap[spk] = overlap.get(spk, 0.0) + ov

    if overlap:
        return max(overlap, key=lambda k: overlap[k])

    # Nessun overlap: usa il parlante attivo immediatamente prima
    candidates = [ev for ev in speaker_events if ev['call_sec'] <= start]
    if candidates:
        return candidates[-1]['speaker']

    return 'Sconosciuto'


def main():
    if len(sys.argv) < 2:
        print('Uso: call-speaker-overlay.py <call_dir>', file=sys.stderr)
        sys.exit(2)

    call_dir = Path(sys.argv[1])
    meta_path = call_dir / 'META.md'
    speaker_events_path = call_dir / 'speaker-events.jsonl'
    transcript_events_path = call_dir / 'transcripts' / 'transcript-events.jsonl'
    out_path = call_dir / 'trascrizione_attribuita.md'

    if not meta_path.exists():
        print('ERRORE: META.md non trovato', file=sys.stderr)
        sys.exit(3)

    meta_text = meta_path.read_text()
    ffmpeg_start_ms = parse_meta_field(meta_text, 'ffmpeg_start_epoch_ms')

    if not ffmpeg_start_ms:
        print('ERRORE: ffmpeg_start_epoch_ms non trovato in META.md', file=sys.stderr)
        sys.exit(3)

    ffmpeg_start_sec = int(ffmpeg_start_ms) / 1000.0

    # Carica speaker events → converti in call_sec
    speaker_events = []
    if speaker_events_path.exists():
        for line in speaker_events_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
                call_sec = ev['epoch_ms'] / 1000.0 - ffmpeg_start_sec
                speaker_events.append({'call_sec': call_sec, 'speaker': ev['speaker']})
            except Exception:
                pass
    speaker_events.sort(key=lambda e: e['call_sec'])

    # Carica transcript events
    transcript_events = []
    if transcript_events_path.exists():
        for line in transcript_events_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
                if ev.get('text', '').strip():
                    transcript_events.append(ev)
            except Exception:
                pass
    transcript_events.sort(key=lambda e: e['call_start_sec'])

    if not transcript_events:
        print('ERRORE: nessun transcript-event trovato', file=sys.stderr)
        sys.exit(4)

    if not speaker_events:
        print('[WARN] Nessun speaker-event — attribuzione impossibile, uso "Sconosciuto"', file=sys.stderr)

    # Genera trascrizione attribuita
    platform = parse_meta_field(meta_text, 'Piattaforma:') or '—'
    # fallback con regex più ampia
    m = re.search(r'\*\*Piattaforma:\*\*\s*(.+)', meta_text)
    platform = m.group(1).strip() if m else '—'

    lines = [f'# Trascrizione attribuita — {platform}\n']
    prev_speaker = None

    for ev in transcript_events:
        ts = fmt_time(ev['call_start_sec'])
        speaker = find_speaker(ev['call_start_sec'], ev['call_end_sec'], speaker_events)
        text = ev['text'].strip()
        if not text:
            continue

        if speaker != prev_speaker:
            lines.append(f'\n**{speaker}**')
            prev_speaker = speaker

        lines.append(f'[{ts}] {text}')

    out_path.write_text('\n'.join(lines) + '\n')
    n_speakers = len({ev['speaker'] for ev in speaker_events}) if speaker_events else 0
    print(f'✓ trascrizione_attribuita.md: {len(transcript_events)} segmenti, {n_speakers} parlanti rilevati')


if __name__ == '__main__':
    main()
