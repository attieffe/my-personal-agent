# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## TTS

- **Provider:** OpenAI TTS (`tts-1`)
- **Voce default:** `nova` (scelta da Atti)
- **Lingua:** italiano
- Quando trasmetti un file in TTS ad esempio su Whatsapp o Telegram cancellalo poi direttamente dal tuo file system tanto ormai è trasmesso ed è inutile mantenerlo.

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Best Practice: Separazione Algoritmo / Dati

**Ogni tool o automazione deve separare fisicamente due layer:**

### `_system/` — Algoritmo (pseudo-fisso)
- Prompt, flow, schemi, regole di funzionamento
- Cambia solo su richiesta esplicita — è il "codice"
- Non contiene nomi di persone, aziende, contesti specifici
- Portabile: funziona su qualsiasi istanza con dati diversi

### `_knowledge/` o cartella dedicata — Dati e Autoapprendimento
- Regole apprese dagli errori (`ROUTING_RULES.md`)
- Contatti e interlocutori (`INTERLOCUTORS.md`)
- Contesto di dominio (`TRIAGE_RULES.md`, thread noti, ecc.)
- Si aggiorna autonomamente nel tempo — è il "training data"
- Può essere svuotato e ricostruito senza toccare l'algoritmo

### Perché conta
- Puoi resettare la knowledge senza perdere il motore
- Puoi portare l'algoritmo su un nuovo progetto con dati diversi
- Gli errori di triage migliorano i dati, non rompono il codice
- Separa chiaramente chi tocca cosa: tu tocchi `_system/`, il sistema aggiorna `_knowledge/`

### Regola pratica
> Quando crei un nuovo tool: chiediti — *"questa informazione cambierà nel tempo per autoapprendimento?"*
> - SÌ → va in `_knowledge/` (o equivalente nella struttura del tool)
> - NO → va in `_system/`

**Esempio applicato**: `projects/email-injection/` — vedi `_system/FLOW.md` per riferimento.

---

Add whatever helps you do your job. This is your cheat sheet.

## Cron jobs (mio promemoria)

- **myjob / controllo email**: quando mi chiedi “fai girare task di controllo email myjob”, lancio il cron job **"myJob IMAP check hourly (read-only triage)"** (jobId: `01d3cd46-bf16-4df8-8485-80d3a4957da1`).
  
  Il progetto email è ora in `projects/email-injection/` (spostato da `projects/myJob/EMAIL/`). Riferimento operativo: `projects/email-injection/INBOX_WORKFLOW.md`.

  Procedura (finché mi chiedi conferma prima di agire):
  - Dopo il giro, leggo `projects/email-injection/02_logs/incoming_untriaged.md` e riassumo UID trovati.
  - Se ci sono email già gestite in altri file, segnalo che risultano ancora in “untriaged” (il cron può solo importare/accodare e non ripulire automaticamente).
  - Per ogni email “da fare”: propongo qui su Telegram la scelta (es. TODO/assegnazioni/spostamenti/archiviazione) e aspetto la tua conferma prima di modificare file o assegnare task.
  - Quando sintetizzo azioni da fare o note operative, includo sempre un link al contenuto originale della email e una % di confidenza sull’azione proposta.
  - Finché non mi dici di procedere in automatico, tratto la confidenza come metrica da affinare con le tue correzioni.
  - L’esito del task cron va notificato **in questa stessa chat Telegram**.
  - Caso tipico: **GCAT Ecommerce** (UID 3, oggetto “I: GCAT Ecommerce”) contiene richiesta “Segna nella mia todolist …” → la devo mettere nella sezione **“Mia todolist (Atti / Attilio)”** (file `projects/myJob/COLZANI/TEAM/README.md`) e non in quella di Alessandro, perché “mia todolist” = tua.
  - In chat lavorativa myJob ti chiamo sempre **Attilio**.
  - Se una mail è un **inoltro/ripresa di thread** (es. “I:” o risposta con contesto), non la tratto come nuova se contiene una continuazione: devo capire se aggiorna un task già esistente, se apre uno scope nuovo, oppure se richiede solo una nota/aggiornamento di stato.

## Related

- [Agent workspace](/concepts/agent-workspace)
