# Test API FileMaker - R_FAT_0001 (2026-06-12)

## Stato
❌ **Layout R_FAT_0001 bloccato per INSERT via API**

## Test Eseguiti

### Test 1: Campi minimal
```json
{
  "fieldData": {
    "IDTESTA": "FA10338",
    "DESCRIZIONE": "Test 1",
    "QTA": 1,
    "Prezzo_Netto": 895.00,
    "Codice Iva f": "22R"
  }
}
```
**Risultato**: ❌ HTTP 500 - Code 201 "Field cannot be modified"

### Test 2: Aggiunti TIPOLOGIA_ARTICOLO + UM
```json
{
  "fieldData": {
    "IDTESTA": "FA10338",
    "DESCRIZIONE": "Test 2",
    "QTA": 1,
    "Prezzo_Netto": 895.00,
    "Codice Iva f": "22R",
    "TIPOLOGIA_ARTICOLO": "SER",
    "UM": "Nr"
  }
}
```
**Risultato**: ❌ HTTP 500 - Code 201 "Field cannot be modified"

### Test 3: Aggiunto tutti campi vuoti (riferimento forzato, numero ddt, data ddt, Sc f 1-3)
```json
{
  "fieldData": {
    "IDTESTA": "FA10338",
    "DESCRIZIONE": "Test 3",
    "QTA": 1,
    "Prezzo_Netto": 895.00,
    "Codice Iva f": "22R",
    "TIPOLOGIA_ARTICOLO": "SER",
    "UM": "Nr",
    "riferimento forzato": "",
    "numero ddt": "",
    "data ddt": "",
    "Sc f 1": "",
    "Sc f 2": "",
    "Sc f 3": ""
  }
}
```
**Risultato**: ❌ HTTP 500 - Code 201 "Field cannot be modified"

## Conclusione
Il blocco è **a livello di layout**, non di singoli campi. Tutte le combinazioni falliscono.

## Possibili Soluzioni
1. **Script FileMaker**: Richiamare uno script FM via API che crei le righe
2. **Modifiche protezione**: Disabilitare protezioni sul layout R_FAT_0001 in FileMaker
3. **Diverso endpoint**: Usare un portale per le righe (se disponibile)

---
**Data**: 2026-06-12 00:30
**Utente**: fmrest
**Database**: DADEGEST
