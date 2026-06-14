---
description: Cron ogni 10 minuti — scarica nuove email da aos@ingeniosolution.it, estrae allegati, analizza per archiviazione ottica e notifica Atti su Telegram.
schedule: "*/10 * * * *"
---

# Cron: AOS Email → Archiviazione Ottica (10 min)

Questo cron gestisce la casella `aos@ingeniosolution.it` per l'archiviazione ottica sostitutiva.
Non fare triage di task. Obiettivo: estrarre documenti dagli allegati e proporli ad Atti per l'archiviazione su Drive.

---

## Step 1 — Scarica nuove email

```bash
cd /home/openclaw/.openclaw/workspace/projects/email-ingestion
python imap_check.py --inbox aos
```

Leggi l'output JSON. Se `new_processed` è 0 → termina silenziosamente senza notificare.

---

## Step 2 — Per ogni .eml nuovo: estrai allegati

Per ogni UID in `processed_uids`:

1. Individua il file `.eml` in `inboxes/aos/00_inbox/msg_<UID>_*.eml`
2. Estrai gli allegati:

```bash
python scripts/extract_attachments.py \
  --eml inboxes/aos/00_inbox/msg_<UID>_<ts>.eml \
  --out-dir /home/openclaw/.openclaw/workspace/projects/archiviazione-ottica-documenti/input/
```

L'output JSON contiene:
- `from_raw` — mittente IMAP
- `subject_raw` — oggetto
- `real_sender` — mittente reale (se email inoltrata, estratto dal body)
- `attachments` — lista allegati salvati in `input/`
- `skipped` — allegati ignorati (inline, junk, tipi non supportati)

Se `attachments` è vuoto → non notificare per questa email (log silenzioso).

---

## Step 3 — Per ogni allegato: analizza con archiver

```bash
cd /home/openclaw/.openclaw/workspace/projects/archiviazione-ottica-documenti
python _system/archiver.py analyze <nome_file>
```

- Exit code 0 → proposta JSON valida (stampa su stdout)
- Exit code 3 → filename non descrittivo, serve OCR (`needs_ocr: true`)
- Exit code 1 → errore generico

Raccogli le proposte per la notifica.

---

## Step 4 — Notifica Atti su Telegram

Formato della notifica (una per run, raggruppa tutte le email/allegati trovati):

```
📂 AOS — [N] document[o/i] da archiviare

[Per ogni allegato con proposta valida:]
📄 <nome_file>
   Da: <real_sender o from_raw>
   Oggetto: <subject_raw troncato a 60 char>
   Categoria: <categoria> → <destinazione Drive breve>
   Data documento: <data_documento>
   Confidenza: <confidenza_data>

[Per ogni allegato con needs_ocr:]
📄 <nome_file> ⚠️ filename non descrittivo — serve OCR per classificare
   Da: <real_sender o from_raw>

Rispondi "archivia tutto", "archivia <file>" o "salta <file>" per procedere.
```

- Usa linguaggio naturale, niente percorsi file.
- Se tutti gli allegati richiedono OCR → comunicalo chiaramente e chiedi conferma.
- Non inviare notifica se non ci sono allegati da proporre.

---

## Step 5 — Salva stato pending

Scrivi un file JSON con le proposte in attesa di conferma:

`inboxes/aos/02_logs/pending_proposals.json`

Struttura:
```json
[
  {
    "eml": "inboxes/aos/00_inbox/msg_<UID>_<ts>.eml",
    "uid": "<UID>",
    "from_raw": "...",
    "subject_raw": "...",
    "real_sender": "...",
    "allegati": [
      {
        "saved_path": "...",
        "filename": "...",
        "proposta": { ... },   // output archiver.py analyze
        "needs_ocr": false
      }
    ]
  }
]
```

Quando Atti conferma in chat, l'agente principale legge questo file, esegue
`archiver.py execute '<proposta_json>'` per ogni allegato confermato e pulisce le entry.

---

## Regole operative

- Leggi `inboxes/aos/TRIAGE_RULES.md` per capire cosa archiviare e come estrarre il mittente reale.
- Leggi `inboxes/aos/ROUTING_RULES.md` per correzioni pregresse sulle categorie.
- Non eseguire mai l'archiviazione in autonomia: attendi sempre la conferma di Atti.
- Non cancellare mai i file in `input/` né in `00_inbox/`: rimangono fino a conferma e archiviazione.
- Non notificare se non ci sono nuove email o allegati archiviabili.
