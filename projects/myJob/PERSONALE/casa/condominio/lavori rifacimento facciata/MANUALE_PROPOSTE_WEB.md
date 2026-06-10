# Manuale — Proposte Colorazione Facciata (Web)

## URL Pubblica
`https://attibot.ingeniosolution.it/condominio/proposte_facciate.html`

## File Locali
- **HTML pagina:** `/home/openclaw/attibot/condominio/proposte_facciate.html`
- **Foto/rendering:** `/home/openclaw/attibot/condominio/img/`
- **Proposte (dati):** `[[Colore facciata]]` (stesso progetto)

---

## Sistema di Codifica Proposte

Ogni proposta ha un codice **Famiglia + Numero**: `B1`, `D4`, `E3`, ecc.

| Lettera | Famiglia |
|---|---|
| **A** | Terre e Terracotta |
| **B** | Neutri Caldi |
| **C** | Grigi Contemporanei |
| **D** | Verdi e Naturali |
| **E** | Ocra e Mediterraneo |
| **F** | Contrasto e Rinnovamento |

Proposte escluse (❌ incompatibili con Douglas): A1, A2, A3, F1, F2.
Attualmente in pagina: **25 proposte** (A4–A5, B1–B5, C1–C2–C4–C5, D1–D5, E1–E5, F3–F5).

---

## Come Aggiungere un Rendering

Quando generi un rendering per una proposta (es. B1):

### 1. Salva l'immagine

```
/home/openclaw/attibot/condominio/img/B1_foto1.jpg
```
Naming convention: `<CODICE>_foto<N>.<ext>` — es. `D4_foto1.jpg`

### 2. Sostituisci il placeholder nel HTML

Trova il card con `id="card-B1"` e sostituisci:

```html
<!-- PRIMA (placeholder): -->
<div class="card-photo">
    <div class="ph-icon">🏢</div>
    <span>Rendering non ancora disponibile</span>
</div>

<!-- DOPO (con rendering): -->
<div class="card-photo">
    <img src="img/B1_foto1.jpg" alt="Rendering proposta B1 — Bianco Caldo">
</div>
```

### 3. Aggiorna il contatore nel status-bar

```html
<!-- Trova questa riga e aggiorna N: -->
<span class="status-item">🖼️ Rendering: <strong>N / 25</strong> completati</span>
```

---

## Come Aggiungere una Nuova Proposta

Se si aggiunge una proposta non prevista (es. G1):

1. Crea una nuova sezione `<section class="family-section" id="fam-g">` nel HTML
2. Aggiungi il link nella `<nav class="family-nav">`: `<a href="#fam-g">G · Nome Famiglia</a>`
3. Aggiungi la proposta in `[[Colore facciata]]` con lo stesso codice
4. Aggiorna i contatori (25 → 26 ecc.)

---

## Come Rimuovere una Proposta

1. Elimina il blocco `<div class="card" id="card-XX">...</div>` dal HTML
2. Segna come `~~eliminata~~` in `[[Colore facciata]]`
3. Aggiorna contatori

---

## Note di Stile

- Swatches: 3 bande colore in cima alla card (dominante 60%, secondario 30%, accessori 20%)
- Colori approssimativi in HEX — per il progetto tecnico usare i codici NCS/RAL reali
- `compat-ok` = sfondo verde chiaro; `compat-warn` = sfondo giallo chiaro
- La pagina è **standalone** (nessuna dipendenza esterna, niente CDN)

---

## Avanzamento Rendering

| Proposta | Foto disponibile | Data |
|---|---|---|
| (aggiornare quando si aggiunge rendering) | | |

