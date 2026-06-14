# ROUTING RULES — aos@ingeniosolution.it

> Aggiornato automaticamente quando Atti corregge una proposta errata.
> Consultare prima di proporre categorie o destinazioni.

---

## Regole

### R01 — Fatture IONOS → INGENIO_SOLUTION
- **Pattern email:** From/real_sender contiene `ionos.it` oppure subject contiene `IONOS`
- **Categoria:** `INGENIO_SOLUTION`
- **Destinazione Drive:** `gdrive:Ingenio/DOCUMENTI FISCALI/{ANNO}/{YYYYMMDD} {titolo}.{ext}`
- **Filename:** usa la data estratta dal filename (`YYYY-MM-DD` o `YYYYMMDD`); nome proposto = `Fattura IONOS {numero_fattura}` se numero leggibile dall'oggetto
- **OCR richiesto:** no — data e categoria ricavabili da filename + contesto email
- **Aggiunto:** 2026-06-14 su indicazione di Atti

---

## Casi di Test

*(nessun caso ancora)*
