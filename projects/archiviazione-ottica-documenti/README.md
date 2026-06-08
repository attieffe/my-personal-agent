# Archiviazione Ottica Documenti

Archivio documenti per Atti.

## Input

- Telegram topic `2069` "Archiviazione documenti"
- AttiBot upload
- File copiati in `input/`

## Regole base

- Prima prova sempre il `filename`.
- OCR/vision solo se il filename non basta, il file è ambiguo o Atti lo chiede.
- Se filename + data + categoria sono già chiari, non fare OCR.
- BPM Ingenio Business / quietanze F24 sono filename-first: niente OCR di default.
- I file originali non si cancellano: finiscono in `90_processed/`.
- Su Drive si usa sempre la fonte `Condivisi con me` / shared, mai lo spazio personale `myjob@`.

## Naming

- Formato finale: `YYYYMMDD titolo.ext`
- Se il filename ha già una data, quella vince.
- Se il filename è già descrittivo, non rinominare “per estetica”.

## Routing

**Regola primaria:** Tutto finisce sempre sotto `gdrive:Atti/Documenti/Archiviazione ottica/{ANNO}/` (destinazione primaria obbligatoria).

Destinazioni specifiche per categoria (in aggiunta alla primaria):
- `BANCA` -> `gdrive:Atti/Documenti/Banche/{sottocartella}/{ANNO}/{YYYYMMDD} {titolo}.{ext}`
- `CERTIFICATI_SANITARI` -> `gdrive:Atti/Documenti/Sanità/{YYYYMMDD} {titolo}.{ext}`
- `INGENIO_SOLUTION` -> `gdrive:Ingenio/DOCUMENTI FISCALI/{ANNO}/{YYYYMMDD} {titolo}.{ext}`
- `SPESE_MEDICHE` -> `gdrive:Atti/Documenti/DICHIARAZIONE DEI REDDITI/{anno+1}x{anno}/{YYYYMMDD} {titolo}.{ext}`
- `AUTO` -> `gdrive:Atti/Documenti/AUTO/{targa} {modello}/{YYYYMMDD} {titolo}.{ext}`
- `SCUOLA_BAMBINI` -> `gdrive:Atti/Documenti/DICHIARAZIONE DEI REDDITI/{anno+1}x{anno}/Bambini/{figlio}/{YYYYMMDD} {titolo}.{ext}`
- `ALTRO` -> nessuna aggiunta (solo primaria)

## Banca

- Revolut personale -> `Revolut`
- Isybank -> `Isybank`
- BBVA -> `BBVA`
- Satispay -> `Satispay`
- PayPal -> `Paypal`
- BPM Ingenio -> `BPM Ingenio`
- Revolut Ingenio -> `Revolut Ingenio`
- Webank -> `WB / WB Chiara`
- Revolut cointestato -> `Revolut Cointestato`
- Intesa Sanpaolo / Intesa Mutui -> `Intesa`
- Fallback se la banca non è chiara: `BPM Ingenio`

## Note operative

- Conferma di Atti obbligatoria prima di copiare su Drive.
- I casi dubbi restano `ALTRO`.
- Le ricette senza importo non sono `SPESE_MEDICHE`.
- Vedi esempi e log in [[history]].

## Backlog minimo

- OCR testo completo solo se serve davvero.
- Test di regressione per il fast path filename-first su BPM Ingenio / F24.
