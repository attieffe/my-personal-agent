# TRIAGE RULES — aos@ingeniosolution.it

## Scopo della casella

Questa inbox riceve **documenti da archiviare otticamente**. Il flusso non è triage/task management,
ma estrazione allegati → analisi → proposta archiviazione su Drive.

## Cosa processare

### Allegati da archiviare
- PDF, immagini (jpg, png, tiff), documenti Office (docx, xlsx)
- Documenti bancari, fiscali, sanitari, assicurativi, auto, scuola bambini
- Bollette e fatture
- Qualsiasi documento che rientra nelle categorie di `projects/archiviazione-ottica-documenti/README.md`

### Cosa ignorare
- Immagini inline (logo, firma email): `Content-Disposition: inline`
- Allegati con nome tipo `image001.png`, `ATT*.htm` (spazzatura Outlook)
- Email senza allegati e senza corpo-documento (notifiche, conferme di lettura, ecc.)

## Estrazione mittente reale

Le email su questa casella sono spesso **inoltri**. Il mittente reale è chi ha prodotto il documento:

1. Cerca nell'oggetto: `Fwd:`, `I:`, `Gir:`, `Fw:` → l'email è un inoltro
2. Nel corpo cerca pattern tipo `Da: <nome> <email>` o `From: <...>` (header originale copiato nel body)
3. Cerca in `Reply-To:` o `Return-Path:` header originali
4. Se non trovato → mittente = `From:` dell'email stessa

## Priorità analisi allegati

1. **Filename descrittivo** → analisi rapida da filename (archiver.py analyze)
2. **Filename non descrittivo** → notifica Atti che serve OCR
3. **Più allegati nella stessa email** → proposta separata per ciascuno

## Regole speciali

- Se l'email ha oggetto che richiama esplicitamente una categoria (es. "Bolletta Enel"),
  usarlo come hint nella proposta anche senza OCR.
- Le ricevute di pagamento Satispay/PayPal/Revolut ricevute via email (no PDF allegato)
  vanno segnalate come "email senza allegato archiviabile" — non processare.
