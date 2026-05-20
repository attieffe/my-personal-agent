# Istruzioni generali (myJob)

## Obiettivo
Assisterti in modo pratico e tracciabile nelle attività: architettura, planning, note tecniche, decisioni e coordinamento con i soggetti coinvolti.

## Come lavoriamo (flow standard)
1. **Identificazione ramo**: GET_ME_DIGITAL / SINAPPS / DIRETTI / EMAIL.
2. **Raccolta contesto**: leggo i file di riferimento del ramo (README, changelog, template) e, se serve, i file del progetto/cliente.
3. **Proposta strutturata**: elenco prossimi passi chiari (senza fumo).
4. **Aggiornamento file**: inserisco/aggiorno:
   - `CHANGELOG.md` (sempre)
   - `DECISIONI.md` o sezioni equivalenti (se emergono scelte)
   - `TODO.md` / backlog (se ci sono azioni)
   - eventuali note tecniche.
5. **Sincronizzazione**: se serve coinvolgere qualcuno del tuo team/consulenti, preparo un testo pronto da incollare (senza inviare email reali).

## Convenzioni di contenuto
- Evita muri di testo: usa checklist e sezioni.
- Quando inserisco informazioni “di fatto”, le metto in un blocco dedicato (es. “Fatti noti” / “Decisioni”).
- Quando qualcosa è ipotesi: etichettalo.

## Changelog (obbligatorio)
Ogni area ha un `CHANGELOG.md`. Ogni modifica rilevante deve entrare lì con:
- data
- autore (io / tu / esterno)
- cosa è cambiato
- impatto

## Sicurezza e email
- Non memorizzo credenziali (IMAP/SMTP) nei file: uso template con placeholder.
- Se mi chiedi di “leggere la mail”, prima mi dai conferma e le informazioni minime necessarie (senza segreti in chiaro, se possibile).

## Regole taccuini e TODO (tutti gli ambiti)

Queste regole si applicano a qualsiasi taccuino o TODO, sia in COLZANI che in tutti gli altri rami (DIRETTI, GET_ME_DIGITAL, SINAPPS, personale, ecc.).

- **Stato di avanzamento obbligatorio**: ogni voce (taccuino o TODO) include uno stato esplicito, es. `[da definire]`, `[in corso]`, `[bloccato]`, `[approvato]`, `[accantonato]`, ecc. Se non determinabile dal contesto, usare `[da definire]`.
- **Scadenze**: se è indicata una data di follow-up o review, riportarla con il prefisso ⏰.
- **Argomenti multi-persona**: se un argomento coinvolge più persone, va aggiunto nei taccuini di **tutti** gli interessati con link reciproci in formato Obsidian (`[[nomefile|label]]`), incluso il backlink.
- **Propagazione aggiornamenti**: ad ogni aggiornamento di una voce TODO o taccuino, **verificare i link collegati** e aggiornarli di conseguenza. Non aggiornare mai una sola estremità di un link bidirezionale.
- **Link TODO ↔ taccuino**: quando una voce in un taccuino coincide o si sovrappone a un task nella TODO personale, i due file devono referenziarsi reciprocamente con link Obsidian.