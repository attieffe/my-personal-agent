# TODO

## Completato

- [x] Prima elaborazione PDF v1 (46 pagine) — 2026-06-21, CF trovati: 22/46 (48%)
- [x] Miglioramento DPI 200→300, prompt più aggressivo, normalizzazione date/importi
- [x] Riprocessamento v2 — 2026-06-21, CF trovati: 28/46 (61%)

## Pagine senza CF (da assegnare manualmente nel foglio)

Pagine dove il CF non è stampato o illeggibile:
`1, 3, 4, 5, 6, 7, 8, 9, 10, 14, 18, 19, 20, 25, 26, 29, 30, 31`

- **Pagine 1–22 (scontrini farmacia):** molte non stampano il CF — normale per scontrini SSN
- **Pagina 25:** CF letto male (`HSCCRH66E95IVC`) — struttura "MOSCATELLO CHIARA" → probabilmente Chiara
- **Pagina 26:** CF non trovato — struttura "Politerapico s.r.l." — verificare a mano
- **Pagine 7, 8:** CF di persona esterna (farmacista?) — non in whitelist, da ignorare o classificare

## Da fare

- [ ] Verificare CF Alice: `FMNLCA22L65B729C` su codicefiscale.it
- [ ] Correggere manualmente le 18 righe senza CF nel foglio Excel
- [ ] Verificare pagina 25 (struttura = nome di Chiara ma CF non decodificato)

## Idee future

- [ ] Aggiungere colonna "Anno" per filtri veloci nel foglio
- [ ] Export diretto su Google Sheets
