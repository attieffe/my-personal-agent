# Generatore PDF Preventivo — FileMaker DADEGEST

Genera un PDF professionale di un preventivo letto via FileMaker Data API. Usa `fetch` nativo di Node 20+ e Chromium headless (via puppeteer) per il PDF.

## Requisiti

- Node.js 20+
- `npm install` (installa puppeteer con Chromium bundled)
- File `.env` nella root del progetto con `FM_HOST`, `FM_PORT`, `FM_USER`, `FM_PASSWORD`
  - Il `.env` è un symlink a `../../.env` (workspace root) — già configurato

## Setup iniziale

```bash
cd projects/ingenio-gest-filemaker-connection
npm install
```

## Uso

Da `projects/ingenio-gest-filemaker-connection/`:

```bash
npm run preventivo -- --nr 5
npm run preventivo -- --nr 5 --anno 2025
npm run preventivo -- --cliente "Condello" --ultimo
npm run preventivo -- --cliente "Rossi" --argomento "PC"
npm run preventivo -- --record-id 301
npm run preventivo -- --nr 5 --iva-inclusa
npm run preventivo -- --nr 5 --keep-html
npm run preventivo -- --nr 5 --html-only
npm run preventivo -- --nr 5 --output "./preventivi/custom.pdf"
```

## Esiti possibili

| Esito | Cosa succede |
|---|---|
| Trovato univoco | PDF generato in `output/preventivi/<anno>/`, riga aggiunta a `logs/YYYY-MM.md` |
| Non trovato | Exit 1, messaggio con suggerimento |
| Non trovato anno corrente, presente anno -1 | Exit 2, suggerisce `--anno YYYY` |
| Più match (cliente ambiguo) | Exit 2, lista candidati su stderr (recordId, Nr/Anno, Data, ragione sociale, totale) |

Quando l'output è ambiguo, **rilanciare** con vincoli più stretti (Nr+Anno, oppure `--argomento`).

## Architettura

```
templates/preventivo/
├── render.mjs          ← entry CLI: arg parsing, orchestrazione, Edge headless print-to-pdf, logging
├── filemaker.mjs       ← client Data API (login, find, get, downloadContainer con redirect+cookie, logout)
├── resolver.mjs        ← resolvePreventivo(token, args) → {status, recordId, candidates}
├── data.mjs            ← orchestra fetch testata + righe (portalData) + Parametri + logo + Iva codes
├── template.mjs        ← generateHtml(data, options) — HTML+CSS A4 print-ready
└── README.md           ← questo file
```

**Sessioni FileMaker**: ne apre 3 distinte (DADEGEST, Parametri, anagrafiche), tutte chiuse con `logout` in `finally`.

**Logo container**: scaricato via redirect manuale + propagazione cookie (FM strippa l'header `Authorization` sui 302).

**TLS bypass**: `process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0'` (sicuro perché solo `https://localhost`).

## Flag di stampa supportati

Letti dalla testata `V_PRE_000`:

| Campo FM | Effetto |
|---|---|
| `STAMPA TOTALE = SI` | Mostra blocco totali (Imponibile, IVA, Totale) |
| `STAMPA FIRMA PER ACCETTAZIONE = SI` | Mostra riquadro "timbro e firma" |
| `Stampa SENZA QTA` non vuoto | Nasconde colonne Qtà + Prezzo unit. |
| `Stampa SENZA PARZIALI` non vuoto | Nasconde colonna Imponibile per riga |
| `STAMPA SALTO PAGINA CON REQIUSITI` non vuoto | `page-break-before` sulle note |

Inoltre da CLI (override runtime):
- `--iva-inclusa` → riga mostra "Totale (IVA incl.)" invece di Imponibile

## Logging

Ogni run aggiunge una riga a `logs/<YYYY-MM>.md` con timestamp + descrizione + path output + esito.

## Limiti noti / TODO

- Variante "IVA esplicita per riga" gestita solo a runtime; valutare flag testata persistente in futuro
- Font: usa fallback di sistema (Segoe UI / Helvetica). Per look custom embeddare un webfont
- Nessuna paginazione automatica per testate molto lunghe — la tabella usa `page-break-inside: avoid` sulle righe
- Solo letture: il template **non modifica nulla** in FM (no PATCH/POST sui record)
