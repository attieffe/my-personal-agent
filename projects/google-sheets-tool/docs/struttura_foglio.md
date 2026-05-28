# Foglio "Rendicontazione Lavori" — Appunti operativi

**Sinonimi / come Atti lo chiama:** "rendicontazione lavori", "foglio lavori", "Lavori attilio", "il foglio"
**Spreadsheet ID:** `1PdJYvqA-23CiucnjwkJvQLXT1tQhQhPeuruUwlUP5fk`
**Account Google:** `ralf00@gmail.com`
**Accesso verificato:** 2026-05-28

---

## Foglio principale operativo: `Lavori`

### Struttura colonne

| Col | Campo | Valori / Note |
|---|---|---|
| A | **canale** | `DIRECT`, `INGENIO`, `GET ME DIGITAL` — identifica il tipo di cliente |
| B | **data attività** | Data del lavoro svolto (vari formati: gg/mm/aaaa, gg/mm/aa) |
| C | **Cliente** | Nome cliente (non normalizzato, stessa entità può avere nomi leggermente diversi) |
| D | **Contratto** | Codice contratto o vuoto (usato soprattutto su INGENIO/tproject) |
| E | **tariffa oraria** | Es. `€ 30,00` — dipende da cliente/canale |
| F | **ore** | Ore lavorate (decimali con virgola) |
| G | **tot** | Totale calcolato (formula nel foglio) |
| H | **Note** | Descrizione attività svolta |
| I | **fatturate** | **Data fatturazione** (es. `30/04/2026`) se fatturata, **vuota** se ancora aperta, `annullata` se annullata |
| J | **ricorrente** | Flag `1` per voci ricorrenti (canoni, abbonamenti) |

### Logica "fatturate"
- **Vuota** = lavoro aperto, non ancora fatturato
- **Data** = fatturato in quella data (si fattura in batch, più righe stessa data = stessa fattura)
- **`annullata`** = riga annullata
- I clienti vengono fatturati *molto dopo* rispetto al lavoro — è normale nel suo workflow

---

## Cluster per canale

### DIRECT — Clienti diretti (no agenzia)
- 134 righe storiche | 224.5h | ~€7.235 fatturato
- Aperte: 13 righe | **€927,50 da fatturare**
- Tariffa tipica: **€35/h**
- Clienti:
  - **rizzi** (principale, 102 righe) — cliente diretto principale, lavori continuativi
  - **ballabio** (17 righe) — anche presente su INGENIO
  - **paladini** (15 righe)

### INGENIO — Fatturazione tramite Ingenio Solution S.a.s.
- 123 righe storiche | 280.5h | ~€10.850 fatturato
- Aperte: 4 righe | **€450 da fatturare**
- Tariffa tipica: **€30-60/h** (variabile per cliente)
- Clienti:
  - **tproject** (principale, 70 righe) — lavori continuativi, contratti blancone/fibermap/altri
  - **Croce Bianca Genovese** (25 righe) — cliente sistemistico
  - **ballabio** (23 righe) — anche in DIRECT

### GET ME DIGITAL — Lavori tramite agenzia GMD
- 39 righe storiche | 186.7h | ~€8.253 fatturato
- Aperte: 7 righe | **€936 da fatturare**
- Tariffa tipica: **€48/h** (agenzia applica markup)
- Clienti: molti clienti one-shot o ricorrenti (rocca, skinius, conipress, enoart, geosystem, susa, ecc.)

---

## Altri fogli

| Foglio | Uso |
|---|---|
| `Lavori pivot` | Vista aggregata per cliente (pivot del foglio Lavori) |
| `Pivot Aperti` | Solo lavori non fatturati, aggregati per cliente |
| `Preventivo kammi` | Preventivo specifico cliente kammi |
| `Preventivo lavori base` | Template preventivi standard (setup web, GA4, ecc.) |
| `2019/2020/2021 GMD` | Storici anni precedenti per canale GMD (struttura diversa) |

---

## Note operative

- Il foglio `Lavori` copre principalmente dal 2022 in poi; gli storici GMD 2019-2021 sono in fogli separati
- Stesso cliente può apparire su canali diversi (es. ballabio su DIRECT e INGENIO)
- I nomi clienti non sono normalizzati al 100% (es. "skinius", "skinius sito", "skinius analisi" = stesso cliente)
- Le ore negative esistono (rettifiche/note credito)
- La fatturazione avviene in batch: molte righe con la stessa data in col I = una sola fattura

---

## Totale aperto attuale (28/05/2026)

| Canale | Righe aperte | Da fatturare |
|---|---|---|
| DIRECT | 13 | €927,50 |
| GET ME DIGITAL | 7 | €936,00 |
| INGENIO | 4 | €450,00 |
| **TOTALE** | **24** | **€2.313,50** |
