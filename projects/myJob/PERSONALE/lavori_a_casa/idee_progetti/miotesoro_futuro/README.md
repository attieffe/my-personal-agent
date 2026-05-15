# MioTesoro — Idee evoluzione futura

Brainstorming sul futuro del progetto MioTesoro come prodotto distribuibile.

**Nota:** L'implementazione operativa attuale è in [[projects/miotesoro-sheet-agent]] (Google Sheet + agente AI).
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

## Le opzioni di distribuzione

### Opzione A: Web App completa (massimi servizi)
→ variante canonica: `mio-tesoro-paas`

App web con tutte le funzionalità. Dato su database esterno (server del prodotto).

**Pro:** UX fluida, multi-device nativo, condivisione familiare, piena potenza tecnologica.

**Contro:** dato finanziario su server altrui — possibile blocco psicologico/reale per alcuni utenti.

---

### Opzione B: Massima privacy (dato solo dell'utente)
→ variante canonica: `mio-tesoro-file`

Nessun server esterno. Dato in mano all'utente tramite storage personale (Dropbox, Google Drive, iCloud). Il file (JSON/CSV/SQLite) viene caricato intero nella webapp a runtime, tutto gira in memoria sul browser.

**Pro:** privacy totale, nessun dato terzi, il file è apribile/modificabile fuori dalla app (Excel, Numbers, qualsiasi editor).

**Contro:** multi-device complicato, condivisione familiare complicata, nessuna query server-side (filtri/aggregazioni fatti in JS).

---

### Opzione C: Via di mezzo (web app su Google Sheets dell'utente)
→ variante canonica: `mio-tesoro-sheet`

Web app che si collega al Google Sheet dell'utente tramite API. Il dato resta nel Google dell'utente, ma l'interfaccia è una vera app.

**Pro:** privacy accettabile (dato su Google dell'utente, già fidato), multi-device e condivisione familiare già risolti da Google.

**Contro:** performance limitate, vincoli tecnologici di Google Sheets come backend, evolvibilità ridotta nel tempo.

---

### Opzione D: DB in proprietà del cliente (ibrida avanzata)
→ variante canonica: `mio-tesoro-mydata`

**Idea emersa il 2026-05-15.**

L'utente porta il proprio DB — o ne crea uno gratuito a suo nome — e lo collega alla webapp. Il dato resta nell'account del cliente, non sul server del prodotto. La webapp usa SQL vero: query filtrate, indici, aggregazioni lato server.

È la via di mezzo tra `mio-tesoro-paas` (tutto nostro) e `mio-tesoro-file` (tutto suo, ma solo file): qui il cliente ha un vero database, con query efficienti, ma ne è il proprietario/amministratore.

#### Opzioni DB praticabili

**Turso** (SQLite edge)
- DB SQLite distribuito su edge, gratuito fino a ~500 MB e limiti generosi
- Il cliente crea il proprio account Turso, fornisce URL + token
- Query SQL complete, indici, JOIN
- Latenza bassa ovunque (CDN globale)
- Non modificabile "a mano" senza client dedicato
- Ideale se si vuole SQLite senza gestire infrastruttura

**Supabase** (PostgreSQL managed)
- PostgreSQL completo, account gratuito per progetti personali
- Il cliente crea il proprio progetto Supabase, fornisce URL + API key
- Tutto il potere di Postgres: query avanzate, indici, funzioni, RLS (row level security)
- Dashboard web per vedere/modificare i dati direttamente
- Ottimo se si prevede crescita o complessità (es. multi-utente familiare con permessi)
- Più "pesante" da configurare rispetto a Turso

**PocketBase** (self-hosted)
- Un singolo binario Go che gira su un server/VPS del cliente
- Database SQLite embedded, admin UI inclusa
- Il cliente deve avere un server (anche un Raspberry Pi, un VPS a 5€/mese)
- Massima autonomia, zero costi ricorrenti se ha già il server
- Setup più tecnico, non adatto a utenti non smanettoni

**SQLite come file su cloud** (ibrido Opzione B/D)
- File `.db` SQLite salvato su Google Drive / Dropbox / iCloud
- La webapp lo scarica, lo apre con `sql.js` (SQLite in WebAssembly), esegue query in locale
- Ha SQL vero ma tutto gira nel browser — nessun server
- Rischio concorrenza (due tab aperte = conflitti), ma per uso personale va benissimo
- Nessun account extra da creare, usa storage già in uso dall'utente

#### Confronto rapido

| Soluzione | Query SQL | Multi-device | Setup | Costo cliente | Dato dove |
|---|---|---|---|---|---|
| Turso | ✅ server-side | ✅ | Basso | Gratis (entro limiti) | Cloud Turso (account suo) |
| Supabase | ✅ server-side | ✅ | Medio | Gratis (entro limiti) | Cloud Supabase (account suo) |
| PocketBase | ✅ server-side | ✅ | Alto | VPS ~5€/mese | Server suo |
| SQLite su cloud | ✅ in-browser | ✅ con sync file | Basso | Gratis | Drive/Dropbox/iCloud |

#### Pro e contro della variante

**Pro:**
- Il dato è nell'account del cliente, non nostro — privacy forte come `mio-tesoro-file`
- Query SQL vere, efficienti anche con anni di storico
- Multi-device e condivisione familiare possibili
- Gratis o quasi per l'utente finale

**Contro:**
- Onboarding più tecnico: il cliente deve creare un account DB e incollare credenziali
- Dipendenza da un servizio terzo (Turso/Supabase) anche se "intestato" al cliente
- Aggiornamenti schema (migrazioni) più complessi da gestire
- Se l'utente perde le credenziali, rischia di perdere i dati

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
