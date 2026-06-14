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


def load_inbox_config(inbox_dir_root: str, inbox_name: str) -> dict:
    """
    Legge inbox.config.md e ritorna un dict con i path operativi per questa inbox.
    Parsing minimale: estrae i valori dalla sezione 'Credenziali IMAP' e 'Cartelle Operative'.
    """
    config_path = os.path.join(inbox_dir_root, 'inboxes', inbox_name, 'inbox.config.md')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"inbox.config.md non trovato: {config_path}")

    cfg = {}
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Parsing righe tipo: `chiave: valore`
            if ':' in line and not line.startswith('#') and not line.startswith('```'):
                k, _, v = line.partition(':')
                cfg[k.strip()] = v.strip()

    base = inbox_dir_root
    inbox_name_folder = os.path.join(base, 'inboxes', inbox_name)

    return {
        'credentials_key': cfg.get('credentials_key', 'IMAP_MYJOB'),
        'inbox_dir':       os.path.join(inbox_name_folder, '00_inbox'),
        'state_path':      os.path.join(inbox_name_folder, '02_logs', 'imap_state.json'),
        'untriaged_log':   os.path.join(inbox_name_folder, '02_logs', 'incoming_untriaged.md'),
        'logs_dir':        os.path.join(inbox_name_folder, '02_logs'),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['preview'], default='preview')
    ap.add_argument('--inbox', default='myjob',
                    help='Nome inbox da processare (cartella in inboxes/)')
    args = ap.parse_args()

    base = os.path.dirname(os.path.abspath(__file__))
    cred_path = os.path.join(base, '.imap_credentials.env')

    # Carica config inbox
    inbox_cfg = load_inbox_config(base, args.inbox)
    cred_key   = inbox_cfg['credentials_key']
    state_path = inbox_cfg['state_path']
    inbox_dir  = inbox_cfg['inbox_dir']
    untriaged_log = inbox_cfg['untriaged_log']

    # Assicura che le cartelle esistano
    os.makedirs(inbox_dir, exist_ok=True)
    os.makedirs(os.path.dirname(state_path), exist_ok=True)

    env = load_env(cred_path)
    # Supporta sia chiavi specifiche per inbox (IMAP_MYJOB_HOST) sia chiave generica (IMAP_HOST)
    prefix = cred_key + '_'
    host     = env.get(prefix + 'HOST')     or env.get('IMAP_HOST')
    port     = int(env.get(prefix + 'PORT') or env.get('IMAP_PORT', 993))
    user     = env.get(prefix + 'USER')     or env.get('IMAP_USER')
    password = env.get(prefix + 'PASS')     or env.get('IMAP_PASS')

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
        'inbox': args.inbox,
        'new_unseen_found': len(uids),
        'new_processed': len(processed_now),
        'processed_uids': processed_now,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
