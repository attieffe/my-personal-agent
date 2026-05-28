# Struttura Foglio "Lavori attilio"

**Spreadsheet ID:** `1PdJYvqA-23CiucnjwkJvQLXT1tQhQhPeuruUwlUP5fk`
**Account:** `ralf00@gmail.com` (account Google personale di Atti)
**Accesso verificato:** 2026-05-28

---

## Fogli presenti

### 1. `Lavori` (ID: 1133533652) — Foglio principale operativo
Il registro corrente delle attività lavorative fatturabili.

Colonne:
| Colonna | Campo | Esempio |
|---|---|---|
| A | canale | INGENIO, DIRECT |
| B | data attività | 26/5/2026 |
| C | Cliente | tproject, rizzi |
| D | Contratto | blancone, fibermap |
| E | tariffa oraria | € 30,00 |
| F | ore | 2,0 |
| G | tot | € 60,00 (calcolato) |
| H | Note | descrizione attività |
| I | fatturate | flag |
| J | ricorrente | flag |

**Uso:** Inserimento ore lavorate per cliente/contratto, con tariffa e totale.

---

### 2. `Lavori pivot` (ID: 1941028825) — Pivot per cliente
Vista aggregata delle attività per cliente, con somma ore e totale.
Colonne: Cliente, data attività, Note, tariffa oraria, SUM ore, SUM tot.

---

### 3. `Preventivo kammi` (ID: 2063635788) — Preventivo specifico
Preventivo dettagliato per cliente "kammi" con ore presunte, moltiplicatori, tariffario.

---

### 4. `Preventivo lavori base` (ID: 1688502706) — Template preventivo
Template standard per preventivi web: setup server, go live, GA4, feed Google Shopping, ecc.

---

### 5. `Pivot Aperti` (ID: 1119411996) — Lavori non fatturati
Pivot delle attività ancora aperte (non fatturate), per cliente.
Colonne: Cliente, data, Note, SUM ore, SUM tot.

---

### 6-8. Storici per anno + canale GMD
- `2021 GMD` (ID: 2134801358) — Attività 2021 per canale GMD
- `2020 GMD` (ID: 1880671793) — Attività 2020 per canale GMD
- `2019 GMD` (ID: 1234679654) — Attività 2019 (intestata Ingenio Solution S.a.s.)

Struttura storica: mese, Cliente, Codice Contratto, vendita unitario, costo unitario, ore, tot, Note, fatturate.

---

## Note operative

- Il foglio **principale operativo è `Lavori`** — qui si inseriscono le nuove registrazioni
- Canali usati: `INGENIO` (tramite società), `DIRECT` (clienti diretti)
- La colonna `tot` sembra calcolata automaticamente (formula)
- `Pivot Aperti` mostra i lavori da fatturare
- Il token OAuth usa l'account `ralf00@gmail.com` (stesso di miotesoro)
