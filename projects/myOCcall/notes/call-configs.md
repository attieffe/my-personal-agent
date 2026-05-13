# Appunti configurazioni call

Questo file è il mio quaderno personale per le configurazioni specifiche di ogni piattaforma.
Aggiornato man mano che Atti mi insegna come configurare le singole call.

---

## Google Meet

- **Script join:** `scripts/call-join-meet.js`
- **Login:** nessuno richiesto per join come ospite; per account Google configurare profilo Chromium
- **Nome visualizzato:** "Attilio F." (hardcoded in call-join-meet.js)
- **Webcam/mic:** disattivati al pre-join

### Selettori CSS (verificare ad ogni aggiornamento di Meet)

| Elemento | Selettore | Note |
|---|---|---|
| Campo nome ospite | `input[placeholder*="nome"]` | Compare solo per ospiti non loggati |
| Bottone mic attivo | `[data-is-muted="false"][aria-label*="microfono"]` | Solo se mic è attivo |
| Bottone cam attivo | `[data-is-muted="false"][aria-label*="fotocamera"]` | Solo se cam è attiva |
| Partecipa ora | `[data-idom-class="nCP5yc"][jsname]` | Join diretto senza lobby |
| Chiedi di partecipare | `[jsname="Qx7uuf"]` | Join con approvazione host |
| Abbandona call | `[aria-label*="Abbandona"]` | Per leave alla fine |
| Badge partecipanti | `[data-participant-id]` | Per contare persone in call |

### Note operative
- Meet può mostrare il campo nome SOLO se il browser non ha sessione Google attiva
- Se c'è una lobby (host deve ammettere), il bot aspetta max 2 minuti
- `browser-status.json` viene aggiornato ogni 30s con conteggio partecipanti
- `active.lock` viene creato al join e rimosso allo shutdown

---

## Microsoft Teams

_Da configurare_

- Login: ?
- Gestione sala d'attesa: ?
- Note: ?

---

## Zoom

_Da configurare_

- Login: ?
- Gestione waiting room: ?
- Note: ?

---

## Note generali

- Whisper API key: da configurare in OpenClaw
- Timeout consigliato per cattura: TBD
- Formato audio ottimale per Whisper: MP3 o M4A, max 25MB per chunk
