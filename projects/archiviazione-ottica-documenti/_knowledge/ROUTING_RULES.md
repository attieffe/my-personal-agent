# Regole di Archiviazione

Ogni documento va SEMPRE nella destinazione primaria.
Le categorie qui sotto aggiungono destinazioni extra.

---

## Destinazione Primaria (sempre)

```
gdrive:Atti/Documenti/Archiviazione ottica/{ANNO}/{YYYYMMDD} {titolo}.{ext}
```

Dove `{ANNO}` = anno estratto dalla data del documento.

---

## Regole per categoria

### SPESE_MEDICHE
**Cos'è:** Scontrini farmacia, fatture medici/specialisti, ticket SSN — documenti con importo detraibile.

**Destinazione aggiuntiva:**
```
gdrive:Atti/Documenti/DICHIARAZIONE DEI REDDITI/{anno_dichiarazione}x{anno_dichiarato}/{YYYYMMDD} {titolo}.{ext}
```
- `anno_dichiarato` = anno della spesa (estratto dal documento)
- `anno_dichiarazione` = anno_dichiarato + 1 (dichiarazione si fa l'anno successivo)
- Esempio: spesa del 2025 → cartella `2026x2025`

**Segnali:** "farmacia", "dott.", "dottore", "specialista", "medico", "visita", "ticket", "SSN", "ASL", presenza di importi + codice fiscale paziente

---

### CERTIFICATI_SANITARI
**Cos'è:** Certificati medici, referti, esami — documenti senza importo o con importo irrilevante.

**Destinazione alternativa** (sostituisce la primaria):
```
gdrive:Atti/Documenti/Sanità/{YYYYMMDD} {titolo}.{ext}
```
Nota: nessuna sottocartella per anno in Sanità.

**Segnali:** "referto", "certificato", "esame", "diagnosi", "ospedale", "laboratorio" — senza importi rilevanti

---

### INGENIO_SOLUTION
**Cos'è:** Fatture, ricevute, spese legate all'azienda Ingenio Solution Srl.

**Destinazione aggiuntiva:**
```
gdrive:Ingenio/DOCUMENTI FISCALI/{ANNO}/{YYYYMMDD} {titolo}.{ext}
```

**Segnali:** "Ingenio Solution", "P.IVA 03491200131", fattura intestata a Ingenio, spese aziendali

---

## Regole ancora da definire

Sezioni da aggiungere in futuro (da discutere con Atti):
- BOLLETTE (luce, gas, acqua, internet)
- BANCA (estratti conto, comunicazioni)
- ASSICURAZIONI
- IMMOBILIARE (casa, affitto, condominio)
- FISCALE_PERSONALE (F24, IMU, ecc.)

---

## Note operative

- In caso di dubbio sulla categoria → proporre `ALTRO` e chiedere conferma
- Un documento può avere più categorie (es. fattura medica Ingenio)
- La data nel nome è SEMPRE quella del documento, non di archiviazione
- Conferma di Atti obbligatoria prima di eseguire qualsiasi copia
