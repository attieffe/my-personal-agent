# Convenzioni naming (myJob)

## Date
- Formato: **YYYY-MM-DD** (es. 2026-05-13)

## Progetti (WordPress / sviluppo)
- Nome cartella: `PROJ-<cliente-or-ramo>-<slug-breve>-<YYYYMMDD>`
  - Esempio: `PROJ-GetMeDigital-site-giordano-20260513`
- In ogni progetto: file principali
  - `README.md`
  - `CHANGELOG.md`
  - `TODO.md`
  - `DECISIONI.md`
  - `RISCHI.md` (se presenti)

## Clienti diretti
- Nome cartella: `CLIENTE-<NomeCliente>-<slug>`
  - Esempio: `CLIENTE-CroceBiancaGenovese-cas-wordpress`

## Contatti/ruoli
In ogni README progetto/cliente includi sempre:
- referenti interni (es. Fabio / Alessandro)
- consulenti esterni (es. Marco Di Stefano)
- PM / commerciale (es. Giordano / Marco Viganò)

## File e cartelle
- I template stanno in `_TEMPLATE/`
- Per aggiornamenti importanti si usa `CHANGELOG.md`.
- Evitiamo file duplicati: aggiorniamo il markdown “fonte” invece di riscrivere altrove.