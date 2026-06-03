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

### AUTO
**Cos'è:** Documenti relativi ai veicoli di Atti (denunce, assicurazioni, libretti, bolli, ecc.).

**Destinazione aggiuntiva:**
```
gdrive:Atti/Documenti/AUTO/{targa} {modello}/{YYYYMMDD} {titolo}.{ext}
```

Veicoli noti:
- BMW X1 SDrive 18i → targa `GA258HL` → cartella `GA258HL BMW X1`

**Segnali:** targa GA258HL, "BMW X1", denuncia sinistro/danno auto, assicurazione veicolo

---

### SCUOLA_BAMBINI
**Cos'è:** Fatture di scuole/asili per i figli Alessandro e Alice Fiumanò — detraibili IRPEF.

**Destinazione aggiuntiva:**
```
gdrive:Atti/Documenti/DICHIARAZIONE DEI REDDITI/{anno_dichiarazione}x{anno_dichiarato}/Bambini/{nome_figlio}/{YYYYMMDD} {titolo}.{ext}
```
- `nome_figlio` = estratto dal documento o dal nome file (Alessandro / Alice)
- `anno_dichiarato` = anno della fattura
- `anno_dichiarazione` = anno_dichiarato + 1

Esempio: fattura 2026 per Alessandro → `2027x2026/Bambini/Alessandro/`

**Segnali:** "asilo", "scuola materna", "scuola paritaria", "retta scolastica", nome figlio nel documento

---

## Regole ancora da definire

Sezioni da aggiungere in futuro (da discutere con Atti):
- BOLLETTE (luce, gas, acqua, internet)
- BANCA (estratti conto, comunicazioni)
- ASSICURAZIONI
- IMMOBILIARE (casa, affitto, condominio)
- FISCALE_PERSONALE (F24, IMU, ecc.)

---

## Regole operative sul naming

### Priorità nome file
1. **Se il nome file di Atti è già descrittivo** → usarlo invariato come nome destinazione (non proporne uno nuovo)
2. **Se il nome file non è descrittivo** (es. "scan001.pdf", "2024.pdf") → proporre nome AI
3. Regola: "non modificare il titolo se Atti l'ha già assegnato ed è testuale"

### Priorità data
1. **Se il nome file contiene una data YYYYMMDD** → usare quella data (non l'AI-extracted)
2. **Se il nome file ha solo l'anno** (es. "2024 Contratto...") → usare AI-extracted o chiedere
3. **Se nessuna data** → usare "00000000" e segnalare

### Ricette mediche senza importo
Una ricetta medica (prescrizione) senza importo pagato **non è SPESE_MEDICHE** (non è detraibile).
→ Categoria: `ALTRO` → va solo in `Archiviazione ottica/{anno}/`
NON va in `DICHIARAZIONE DEI REDDITI/`

---

## Note operative

- In caso di dubbio sulla categoria → proporre `ALTRO` e chiedere conferma
- Un documento può avere più categorie (es. fattura medica Ingenio)
- La data nel nome è SEMPRE quella del documento, non di archiviazione
- Conferma di Atti obbligatoria prima di eseguire qualsiasi copia
