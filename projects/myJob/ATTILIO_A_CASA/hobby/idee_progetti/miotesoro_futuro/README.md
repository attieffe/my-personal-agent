# MioTesoro — Idee evoluzione futura

Brainstorming sul futuro del progetto MioTesoro come prodotto distribuibile.

**Nota:** L'implementazione operativa attuale è in [[projects/miotesoro]] (Google Sheet + agente AI).
Questo file è il brainstorming sulle idee di *evoluzione e distribuzione*.

**Aggiunto:** 2026-05-14

---

## Stato attuale

MioTesoro è **già operativo per uso personale**:
- Collegato a Google Sheet (PERSONALE e CASA)
- Alimentato tramite messaggi all'agente
- Funziona bene per Atti

---

## Visione futura: distribuire il progetto

L'idea è portare MioTesoro ad altri utenti. Esistono tre direzioni principali.

---

### Opzione A: Web App

Creare una vera web app per la gestione delle finanze personali.

**Vantaggio:** esperienza utente fluida, multi-device nativo, condivisione familiare facile.

**Dubbio critico — Privacy:**
Le persone sono disposte a mettere i dati delle proprie finanze (tutti i movimenti, tutti i conti) su un servizio terzo?
- Dati sensibili per definizione
- Anche se crittografati, il dato "passa" da un server altrui
- Potrebbe essere un blocco psicologico/reale per molti utenti

---

### Opzione B: Dato in mano all'utente (Local/Own Cloud)

Lasciare il dato completamente in controllo dell'utente, usando il suo storage personale (Dropbox, Google Drive, iCloud, ecc.).

**Vantaggio:** massima privacy, nessun dato a terzi.

**Svantaggi:**
- Multi-device difficile da gestire
- Condivisione con familiare (es. moglie/marito) complicata
- Setup più complesso per l'utente medio

---

### Opzione C: Agente preskillato su Google Sheet

Invece di una web app, dare all'utente un **agente AI già configurato** che lavora direttamente sul suo Google Sheet personale.

**Vantaggio:**
- Il dato resta nel Google Sheet dell'utente (già conosciuto, già fidato)
- Multi-device via Google (già risolto)
- Condivisione familiare via Google (già risolta)
- Nessuna infrastruttura da mantenere lato prodotto

**Sfida:**
- Come "distribuire" l'agente? Setup guidato? Template?
- Personalizzazione per diversi piani dei conti
- Supporto e aggiornamenti

---

## Domande aperte

1. Qual è il vero blocco: privacy, complessità di setup, o costo?
2. C'è un mercato per un agente AI finanziario su Google Sheet?
3. Opzione A e C sono mutuamente esclusive o complementari (freemium: Sheet gratis, web app pro)?
4. Esistono già competitor simili?

---

## Prossimi passi

- [ ] Raccogliere più appunti/documenti già esistenti su queste idee
- [ ] Valutare se fare un piccolo sondaggio su disponibilità a condividere dati finanziari
- [ ] Esplorare modelli di distribuzione agenti AI (OpenClaw e non)
