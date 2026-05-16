# Meeting Log — Gestione Fiscale Magazzino

---

## 2026-05-16 — Riunione operativa (appunti da call)
**Partecipanti:** Attilio, Cristina Rizzetto (e altri)

### Punti discussi
1. **Stampa NAV libro giornale magazzino**
   - Esistono 2 layout: uno che aggrega per magazzino, uno no
   - Cristina approfondisce quali campi è necessario mostrare
   - → TODO: verificare quale layout va bene e definire con Cristina

2. **Prodotti ".4"**
   - In attesa di capire cosa mettere in questo contenitore
   - Il delta andrà inserito qui a valle dell'attività dei resi (da finire prima)

3. **Resi 2026 anticipati al 2025**
   - Procedura annuale abituale
   - Attilio esegue e manda il totale a Cristina
   - → TODO Attilio: eseguire e comunicare a Cristina

---

## ARCHIVIO APPUNTI 2021–2022

> Trascrizione appunti storici riportati il 16/05/2026.

### Requisiti generali stampa (anno 2022)
- Aggiungere UBICAZIONE descrittiva in alto
- Descrizione su una riga
- Movimenti .4: cambiare "Rettifica positiva" → **Acquisto** e "Rettifica negativa" → **Vendita**
- Fare verifiche a campione su saldi apertura e chiusura dei vari magazzini

---

### Maggio 2022
- Ottimizzare stampa AS400 (FileMarker file NAV)
- Verificare stampa NAV movimento (report **18100537**)
- Fare stampa al 31/12/2019 ad arte [capire se NAV o FM]

**Stampa per articolo:**
- Divisione: ubicazione/articolo, salto pagina in fondo
- Campi: articolo, descrizione, quantità, UM, costo unitario (ricavato come divisione per la quantità), costo totale
- Totale unico finale

---

### 05/06/2022
- Procedere inserendo i carichi nave in AS400 formalmente su **magazzino 5**

---

### 29/05/2022
- Inserire come movimento fittizio AS400 dei movimenti **NEGATIVI al 31/3** dei prodotti con giacenza negativa all'1/1
- Togliere i prodotti NON SPA (quindi prefisso 080 SportIT o altri prefissi non SPA)

---

### 22/05/2021
Modificare report movimenti magazzino:
- Rimuovere campo "utente"
- Rimuovere campo "data di generazione"
- Inserire filtro magazzino
- Stampa AS ad arte

---

### 15/05/2021
- Rimuovere da AS file con movimenti su prefissi non corretti
- Fare 2 stampe: una da AS, una da NAV
- Ricalcolare giacenza iniziale da AS per far quadrare i conti
- La giacenza iniziale su NAV va mantenuta buona (non toccare)
