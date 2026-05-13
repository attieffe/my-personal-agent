import argparse
import imaplib
import ssl
import json
import os
from datetime import datetime, timezone
from email import policy
from email.parser import BytesParser


def load_env(path):
    env = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()
    return env


def load_state(path):
    if not os.path.exists(path):
        return {"processed_uids": [], "last_run_utc": None}
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if "processed_uids" not in data:
        data["processed_uids"] = []
    return data


def save_state(path, state):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def decode_any(s):
    try:
        if s is None:
            return ''
        if isinstance(s, bytes):
            return s.decode('utf-8', errors='replace')
        return str(s)
    except Exception:
        return ''


def extract_preview(msg):
    # Prefer text/plain first, else text/html stripped-ish.
    text_parts = []
    for part in msg.walk():
        ctype = part.get_content_type()
        disp = str(part.get('Content-Disposition', '') or '')
        if 'attachment' in disp.lower():
            continue
        if ctype not in ('text/plain', 'text/html'):
            continue
        try:
            payload = part.get_payload(decode=True)
            if not payload:
                continue
            charset = part.get_content_charset() or 'utf-8'
            content = payload.decode(charset, errors='replace')
            # light normalization
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            text_parts.append(content)
        except Exception:
            continue

    if not text_parts:
        return ''
    preview = text_parts[0]
    # trim
    preview = preview.strip()
    if len(preview) > 800:
        preview = preview[:800] + '…'
    # collapse newlines
    preview = ' '.join(preview.split())
    return preview


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['preview'], default='preview')
    args = ap.parse_args()

    base = os.path.dirname(__file__)
    cred_path = os.path.join(base, '.imap_credentials.env')
    state_path = os.path.join(base, '02_logs', 'imap_state.json')
    inbox_dir = os.path.join(base, '00_inbox')
    untriaged_log = os.path.join(base, '02_logs', 'incoming_untriaged.md')

    env = load_env(cred_path)
    host = env['IMAP_HOST']
    port = int(env['IMAP_PORT'])
    user = env['IMAP_USER']
    password = env['IMAP_PASS']

    state = load_state(state_path)
    processed = set(str(x) for x in state.get('processed_uids', []))

    ctx = ssl.create_default_context()
    processed_now = []

    imap = imaplib.IMAP4_SSL(host, port, ssl_context=ctx)
    imap.login(user, password)

    imap.select('INBOX')

    # Search UNSEEN only (read-only). We'll avoid re-processing UIDs via state.
    status, data = imap.search(None, 'UNSEEN')
    if status != 'OK':
        raise RuntimeError(f"IMAP search failed: {status} {data}")

    uids = []
    if data and data[0]:
        uids = data[0].split()

    # Sort newest first (UIDs are increasing)
    uids = sorted(uids, key=lambda b: int(b), reverse=True)

    # Limit to keep runs lightweight
    max_fetch = 10
    uids = uids[:max_fetch]

    for uid_b in uids:
        uid = str(uid_b.decode('ascii', errors='ignore') if isinstance(uid_b, bytes) else uid_b)
        if uid in processed:
            # Anche se l’UID è già stato triaggiato in passato, qui lo marchiamo come letto
            # per evitare che resti in stato UNSEEN.
            try:
                imap.store(uid_b, '+FLAGS', '\\Seen')
            except Exception:
                pass
            continue

        # Fetch full message (BODY.PEEK non marca come letto automaticamente)
        status, msg_data = imap.fetch(uid_b, '(BODY.PEEK[])')
        if status != 'OK' or not msg_data:
            continue

        raw = None
        for item in msg_data:
            if isinstance(item, tuple):
                raw = item[1]
                break
        if not raw:
            continue

        msg = BytesParser(policy=policy.default).parsebytes(raw)

        subject = decode_any(msg['subject'])
        from_ = decode_any(msg.get('from'))
        date_ = decode_any(msg.get('date'))
        preview = extract_preview(msg)

        filestr = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        out_eml = os.path.join(inbox_dir, f"msg_{uid}_{filestr}.eml")
        with open(out_eml, 'wb') as f:
            f.write(raw)

        # Append to untriaged log
        with open(untriaged_log, 'a', encoding='utf-8') as f:
            f.write(f"\n---\nUID: {uid}\nDate: {date_}\nFrom: {from_}\nSubject: {subject}\nEML: {os.path.relpath(out_eml, base)}\nPreview: {preview}\n")

        # Ora che abbiamo scaricato la mail, la marchiamo come letta
        try:
            imap.store(uid_b, '+FLAGS', '\\Seen')
        except Exception:
            pass

        processed_now.append(uid)

    # Update state
    if processed_now:
        processed.update(processed_now)
    # Keep state bounded
    state['processed_uids'] = sorted(list(processed), key=lambda x: int(x) if str(x).isdigit() else 0)[-500:]
    state['last_run_utc'] = datetime.now(timezone.utc).isoformat()
    save_state(state_path, state)

    imap.logout()

    # Print a short summary to stdout for cron logs
    print(json.dumps({
        'new_unseen_found': len(uids),
        'new_processed': len(processed_now),
        'processed_uids': processed_now,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
