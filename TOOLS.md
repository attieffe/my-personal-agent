# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Camera names, SSH hosts, TTS preferences, device nicknames — anything environment-specific.

## TTS

- **Provider:** OpenAI TTS (`tts-1`)
- **Voce default:** `nova` (scelta da Atti)
- **Lingua:** italiano
- Quando trasmetti un file in TTS ad esempio su Whatsapp o Telegram cancellalo poi direttamente dal tuo file system tanto ormai è trasmesso ed è inutile mantenerlo.

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Best Practice: Separazione Algoritmo/Dati

Tool/automazioni: separare `_system/` (algoritmo fisso) da `_knowledge/` (dati/apprendimento). Esempio: [[projects/email-ingestion/_system/FLOW]].

---

## Regola: aggiunta/aggiornamento note e informazioni

**Quando Atti mi dà una nota o un'informazione da aggiungere/aggiornare:**

1. **MAI creare un nuovo file `.md` senza chiedergli conferma.**
2. Cercare prima il file `.md` esistente più adatto (per tema, contesto, progetto).
3. Se trovo un file adatto → aggiornarlo direttamente.
4. Se NON trovo un file adatto → **chiedere conferma** prima di crearne uno nuovo, proponendo il path ipotizzato.

> Regola: aggiorna, non proliferare. Un file ben aggiornato vale più di dieci file nuovi.

---

## Convenzioni archiviazione dati
### Files e allegati non .MD

- I file gestiti nel workspace diversi dai file .MD ma collegati a informazioni in file MD vanno in [[_attachments/static/]]
- i file gestiti nel workspace ai fini tecnici di download/upload lavorazioni temporanee o transitorie vanno gestiti in [[_attachments/temp/]]

### Utility IA
- script Python, JS, bash, powershell e similari da conservare perchè riutilizzabili vanno archiviati in [[_utility/static]]
- - script Python, JS, bash, powershell e similari da usare on the fly, temporaneamente, per singole attività, vanno depositati in [[_utility/temp]]
---

Add whatever helps you do your job. This is your cheat sheet.

## Cron jobs

- **Email myJob**: job `01d3cd46-bf16-4df8-8485-80d3a4957da1` → workflow in [[projects/email-ingestion/_system/FLOW]]

## Related

- [Agent workspace](/concepts/agent-workspace)

---

## Report Web

**URL pubblici:** `https://attibot.ingeniosolution.it/reports/YYYYMMDD_<nome>/index.html`  
**Path locale:** `/home/openclaw/attibot/reports/`
