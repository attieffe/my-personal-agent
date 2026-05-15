---
description: Cron orario — scarica nuove email da tutte le inbox attive, le analizza e notifica Attilio se ci sono item da revisionare.
schedule: "0 * * * *"
---

# Cron: Hourly Email Check

## Step 1 — Leggi inbox attive

Leggi `projects/email-injection/_system/INBOXES_REGISTRY.md` e ricava la lista delle inbox con `Attiva: ✅`.

---

## Step 2 — Per ogni inbox attiva: scarica nuove email

Esegui in terminale:

```bash
cd projects/email-injection
python imap_check.py --inbox [nome_inbox]
```

Leggi l'output JSON. Se `new_processed` è 0 → nessuna email nuova, salta allo step successivo.

---

## Step 3 — Per ogni .eml nuovo: analizza

Per ogni UID in `processed_uids` dell'output:

1. Individua il file `.eml` appena salvato in `inboxes/[inbox]/00_inbox/`
2. Segui integralmente le istruzioni di `projects/email-injection/_system/analyze_email.prompt.md`
   - Input inbox: `[nome_inbox]`
   - Input eml: percorso del file scaricato
3. Il risultato è un companion `.md` in `inboxes/[inbox]/01_to-be-defined/` e una riga aggiunta all'INDEX

---

## Step 4 — Componi notifica Attilio

Leggi `inboxes/[inbox]/01_to-be-defined/INDEX.md` per tutte le inbox.

- **Se INDEX è vuoto per tutte le inbox** → nessuna notifica, termina silenziosamente.
- **Se ci sono item pendenti** → invia notifica con questo formato:

```
📬 [N] email da revisionare

[Per ogni item nell'INDEX:]
📧 [mittente_reale] — [subject troncato a 60 char]
   Proposta: [tipo_azione] → [target breve] ([confidence_routing]% routing / [confidence_action]% azione)

Rispondi per confermare, rettificare o chiedere dettagli.
```

- Usa linguaggio naturale, niente tecnicismi, niente percorsi file.
- Se un'email ha `confidence_routing < 0.60` oppure `confidence_action < 0.40`, aggiungi ⚠️ prima della riga.

---

## Step 5 — Aggiorna log

Aggiorna `inboxes/[inbox]/02_logs/imap_state.json` → già gestito da `imap_check.py`.
Nessuna altra scrittura necessaria salvo quanto già prodotto dagli step precedenti.
