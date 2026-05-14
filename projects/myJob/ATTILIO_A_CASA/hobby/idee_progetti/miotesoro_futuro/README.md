# MioTesoro — Idee evoluzione futura

Brainstorming sul futuro del progetto MioTesoro come prodotto distribuibile.

**Nota:** L'implementazione operativa attuale è in [[projects/miotesoro]] (Google Sheet + agente AI).
Questo file raccoglie le idee di *evoluzione e distribuzione*. Esiste già un'analisi approfondita in una sessione Claude separata — da integrare qui.

**Aggiunto:** 2026-05-14

---

## Stato attuale

MioTesoro è **già operativo per uso personale di Atti**:
- Collegato a Google Sheet (fogli PERSONALE e CASA)
- Alimentato tramite messaggi all'agente AI
- Include una **componente previsionale**: permette di censire entrate e uscite future (tasse incluse) per rispondere a domande tipo "posso permettermi le vacanze ad agosto?"
- Il Google Sheet è una soluzione funzionante ma con limiti tecnici — considerata "palliativa" rispetto a una vera web app

---

## Target ipotizzato

| Segmento | Bisogno principale |
|---|---|
| **Famiglie con figli** | Capire chi ha speso cosa tra conti diversi (cointestato, personale, partner) |
| **Freelance / P.IVA** | Cash flow alto ma irregolare, tasse future da anticipare |
| **Persone con forte controllo** | Amano monitorare, tracciare, avere il quadro completo |

**Caratteristica comune:** muovono una quantità significativa di denaro e vogliono averlo sotto controllo.

**Escluso by design:** utenti con redditi non dichiarati — non è un target, è un rischio.

---

## Differenziatore chiave

La **componente previsionale** è il vero vantaggio competitivo rispetto alle app di tracking standard (Spendee, Money Manager, YNAB):
- Non solo "quanto ho speso" ma "quanto spenderò"
- Pre-censimento tasse future
- Risposta a domande decisionali concrete ("posso permettermi X?")

---

## Le tre opzioni di distribuzione

### Opzione A: Web App completa (massimi servizi)

App web con tutte le funzionalità. Dato su database esterno (server del prodotto).

**Pro:** UX fluida, multi-device nativo, condivisione familiare, piena potenza tecnologica.

**Contro:** dato finanziario su server altrui — possibile blocco psicologico/reale per alcuni utenti.

---

### Opzione B: Massima privacy (dato solo dell'utente)

Nessun server esterno. Dato in mano all'utente tramite storage personale (Dropbox, Google Drive, iCloud).

**Pro:** privacy totale, nessun dato terzi.

**Contro:** multi-device complicato, condivisione familiare complicata, setup tecnico elevato.

---

### Opzione C: Via di mezzo (web app su Google Sheets dell'utente)

Web app che si collega al Google Sheet dell'utente tramite API. Il dato resta nel Google dell'utente, ma l'interfaccia è una vera app.

**Pro:** privacy accettabile (dato su Google dell'utente, già fidato), multi-device e condivisione familiare già risolti da Google.

**Contro:** performance limitate, vincoli tecnologici di Google Sheets come backend, evolvibilità ridotta nel tempo.

---

## Ostacolo critico identificato: onboarding

Indipendentemente dall'opzione scelta, il **setup iniziale** è il punto di rottura principale:
- Censire il piano dei conti
- Collegare i conti
- Inserire le uscite fiscali previste
- Capire la logica previsionale

Chi non lo supera, abbandona. Da progettare con attenzione.

---

## Prossimi passi

- [ ] Integrare l'analisi già fatta nella sessione Claude separata
- [ ] **Somministrare il questionario di validazione** → vedi [[questionario_validazione]]
- [ ] Valutare competitor con componente previsionale
- [ ] Decidere quale opzione perseguire sulla base dei feedback raccolti

## Costruzione del questionario

- Questionario breve, anonimo, ~5 minuti
- 5 sezioni: profilo, bisogno, disciplina, privacy/tecnologia, domanda libera
- Domande chiave segnate con ⭐ per separare interesse reale da curiosità generica
- Opzioni finali allineate alle quattro varianti canoniche:
  - `mio-tesoro-file`
  - `mio-tesoro-paas`
  - `mio-tesoro-cloud`
  - `mio-tesoro-sheet`
