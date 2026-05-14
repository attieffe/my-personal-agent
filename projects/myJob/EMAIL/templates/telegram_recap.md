# Template Recap Email per Telegram

Questo template definisce il formato dei messaggi che il sistema invia su Telegram dopo il check email.

## Regole Fondamentali

❌ **NO tecnicismi**:
- NO UID, JSON, nomi file Python (imap_check.py, pending_actions.json, ecc.)
- NO riferimenti a file di log o strutture interne
- NO terminologia da sviluppatore

✅ **Linguaggio naturale**:
- Persone, non file
- Azioni, non operazioni tecniche
- Contesto chiaro e immediato

---

## Template Messaggio Iniziale

```
📬 **Check email completato**

{N} nuove email ricevute
{M} email in attesa di tua conferma da check precedenti
```

---

## Template per Singola Email

```
📧 **Email da {MITTENTE_NOME} ({CONTESTO})**

**Oggetto**: {SUBJECT}

**Area/Società**: {AREA} {SOCIETA_SE_PRESENTE}

**Cosa dice**: 
{SINTESI_2_3_RIGHE}

**Azione che propongo**:
{AZIONE_DETTAGLIATA}

---
```

### Variabili Template

#### {MITTENTE_NOME}
Nome e cognome della persona (NON l'indirizzo email).

Esempi:
- ✅ "Alessandro"
- ✅ "Marco Di Stefano"
- ✅ "Attilio"
- ❌ "attilio.fiumano@gruppocolzani.it"

#### {CONTESTO}
Ruolo o relazione della persona con il lavoro.

Esempi:
- "team interno SPORTIT"
- "consulente AS400"
- "partner Lotrek"
- "fornitore Capgemini"
- "cliente Ballabio Cucine"

#### {SUBJECT}
Oggetto email pulito (senza "Re:", "I:", "Fwd:").

#### {AREA}
Area di pertinenza principale.

Valori possibili:
- COLZANI
- GET_ME_DIGITAL
- SINAPPS  
- DIRETTI
- EMAIL (generica)

#### {SOCIETA_SE_PRESENTE}
Se area è COLZANI, specificare società del gruppo.

Esempi:
- "SPORTIT SRL"
- "COLZANI SRL"
- "GRUPPO COLZANI"
- (vuoto se non applicabile)

Formato: `COLZANI - SPORTIT SRL`

#### {SINTESI_2_3_RIGHE}
Sintesi del contenuto in linguaggio naturale, 2-3 righe max.

Focus su:
- Cosa chiede/comunica il mittente
- Eventuali istruzioni esplicite (se da Attilio)
- Informazioni rilevanti per decidere l'azione

Esempi:
- ✅ "Alessandro ha risposto sulla questione InPost e conferma che sta verificando il mapping del numero di telefono nel feed per Meta. Dice che serve ancora tempo per completare i controlli."
- ✅ "Attilio chiede di segnare nella sua TODO personale, in una sottosezione da discutere con Stefano Colzani, il canone NAV-Ls retail Capgemini per il 2026-2027 (ticket OP# 02698455)."
- ❌ "Email contiene informazioni su ticket Capgemini e richiesta di update JSON file pending_actions."

#### {AZIONE_DETTAGLIATA}
Azione proposta con dettagli operativi.

**Se aggiornamento task esistente**:
Specificare il task e cosa aggiungere.

Esempio:
```
Aggiornare il task di Alessandro "InPost: mappatura meta → numero telefono" 
aggiungendo nota che sta ancora verificando e servono controlli addizionali.
```

**Se nuovo task**:
Specificare dove crearlo e cosa scrivere.

Esempio:
```
Creare nuovo task nella tua TODO personale (sezione "da discutere con Stefano"):
"Canone NAV-Ls retail Capgemini 2026-2027 - OP# 02698455"
```

**Se serve chiarimento**:
Spiegare cosa non è chiaro e cosa serve sapere.

Esempio:
```
Non sono riuscito a identificare se questa email si riferisce a un progetto esistente.
Ti serve sapere: è correlata a qualche task in corso oppure è una richiesta nuova?
```

**NO riferimenti tecnici**:
- ❌ "Aggiornare ALessandro_TODO.md riga 42"
- ✅ "Aggiornare il task di Alessandro su InPost"

- ❌ "Creare entry in COLZANI/TEAM/README.md"
- ✅ "Aggiungere alla tua TODO personale"

---

## Esempio Completo

```
📬 **Check email completato**

2 nuove email ricevute
1 email in attesa di tua conferma da check precedente

━━━━━━━━━━━━━━━━━━━━━━

📧 **Email da Alessandro (team interno SPORTIT)**

**Oggetto**: InPost e numero di telefono

**Area/Società**: COLZANI - SPORTIT SRL

**Cosa dice**: 
Alessandro ha risposto sulla questione InPost. Conferma che sta verificando il mapping del numero di telefono nel feed per Meta. Dice che serve ancora tempo per completare i controlli e che ti aggiornerà quando avrà finito.

**Azione che propongo**:
Aggiornare il task di Alessandro "InPost: mappatura meta → numero telefono" aggiungendo nota che la verifica è in corso e che serve ancora tempo.

━━━━━━━━━━━━━━━━━━━━━━

📧 **Email da Attilio (IT Manager)**

**Oggetto**: Capgemini - OP# 02698455 - Canone NAV-Ls retail

**Area/Società**: COLZANI - GRUPPO COLZANI

**Cosa dice**:
Attilio ha ricevuto comunicazione da Capgemini sul canone NAV-Ls retail per il 2026-2027 (ticket OP# 02698455). Nel testo specifica: "Segna nella mia TODO personale ma in una sottosezione da discutere con STEFANO COLZANI".

**Azione che propongo**:
Creare nuovo task nella tua TODO personale, in una nuova sottosezione "Da discutere con Stefano":
"Canone NAV-Ls retail Capgemini 2026-2027 - OP# 02698455"

━━━━━━━━━━━━━━━━━━━━━━

Cosa vuoi che faccia?
```

---

## Quick Actions (opzionali)

Se il sistema supporta quick-reply buttons:

- ✅ Conferma tutto
- 📝 Conferma parziale  
- ❌ Ignora
- 💬 Serve chiarimento

---

## Note Implementazione

Questo template viene usato da:
- Script che genera output Telegram dopo check email
- Sistema di formatting per mantenere consistenza

NON usare questo template per:
- Log interni (quelli possono avere dettagli tecnici)
- Comunicazioni tra script (usare JSON)
- Debug/sviluppo

**Obiettivo**: Attilio deve capire immediatamente cosa è successo e cosa deve decidere, senza dover interpretare tecnicismi.
