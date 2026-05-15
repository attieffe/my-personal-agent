# DECISIONS.md — MioTesoro
Log delle decisioni architetturali prese nel progetto.
Ogni decisione riporta data, contesto e motivazione.
Documento condiviso tra tutti gli agenti specializzati.

---

## Product Vision

### Job-to-be-done principale
**"Non so dove vanno i miei soldi, e non so dove andranno."**
MioTesoro risolve entrambi i problemi: contabilità del passato e proiezione del futuro, in un unico strumento che non richiede conoscenze contabili.

### Tre profili utente e il loro problema specifico

| Profilo | Problema core | Differenziatore MioTesoro |
|---------|--------------|--------------------------|
| **Individuo** | Non traccia le spese in modo sistematico | Data entry facile (voce, AI), cashflow futuro |
| **Famiglia / Coppia** | Gestione condivisa caotica, strumenti troppo complessi | Scenario condiviso, UX semplice, visibilità reciproca |
| **Freelance / Piccola attività** | Non sa cosa incasserà/spenderà nei prossimi mesi | Cashflow simulato su orizzonte lungo, budget variabile vs programmato |

### Differenziatori tecnici vs competitor (YNAB, Spendee, Toshl)
1. **Partita doppia con UX completamente astratta** — vantaggio strutturale, non copiabile senza riscrittura core
2. **Cashflow simulato futuro** con distinzione scheduled/variable — nessun competitor consumer lo fa
3. **Multi-scenario first-class** (personale + familiare + aziendale) nello stesso prodotto
4. **Parser estratti conto AI per-utente** — generazione automatica del parser sul profilo bancario dell'utente
5. **MCP server esposto** — posiziona il prodotto come infrastruttura aperta, non app chiusa

---

## Sessione 1 — 2026-05-01
### Focus: Modello dati core, piano dei conti, scenari, infrastruttura base, architettura multi-agente

---

### ADR-001 — Modello dati: partita doppia nativa
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
Il modello dati core è basato sulla partita doppia classica. Ogni registrazione è composta da N movimenti (minimo 2) la cui somma algebrica è zero.

**Motivazione:**
15 anni di uso personale dimostrano che è l'unico modello che garantisce la correttezza dei dati. È il differenziatore tecnico rispetto ai competitor (YNAB, Spendee) che usano modelli piatti.

**Implicazione:**
L'UX deve astrarre completamente il meccanismo per l'utente non contabile. I template di registrazione sono lo strumento principale per questa astrazione.

---

### ADR-002 — Struttura tabelle core: registrations + movements
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
- `registrations` — testata (data, descrizione, scenario)
- `movements` — righe (conto, importo, stato, data valuta)

---

### ADR-003 — Stati del movimento
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
`movements.stato`: `eseguito` | `previsto` | `annullato`

**Nota:** Lo stato `previsto` è il mattone fondamentale del cashflow simulato futuro. I movimenti `previsto` possono estendersi su orizzonti pluriennali (es: tutte le rate di un mutuo). Sono generati da regole ricorrenti — vedi ADR-028.

---

### ADR-004 — `movements.amount`: segno algebrico diretto
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
`amount` contiene il segno algebrico direttamente. La query del cashflow è una semplice `SUM(amount)`. Necessario anche per i giroconti (patrimoniale → patrimoniale).

---

### ADR-005 — `display_sign` su accounts per la reportistica
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
Colonna `display_sign` (`1` | `-1`) su `accounts`. Usata esclusivamente nel layer di reportistica. Il dato grezzo non si tocca mai.

---

### ADR-006 — Piano dei conti: struttura gerarchica self-referential
**Data:** 2026-05-01
**Stato:** ✅ Deciso (esteso in Sessione 8: aggiunti `accounts.type` semantico e flag `extraordinary`)

**Decisione:**
Self-referential con `parent_id` e colonna `path` per query efficienti. Limite di 3 livelli imposto a livello applicativo.

**Tassonomia semantica (originale Sessione 1):**
- `account_type`: `patrimonial` | `economic`
- `account_role`: `real` | `transit` | `opening_balance`
- `display_sign`: `1` | `-1`
- `semantic_tag`: tag controllato da noi per aggancio template
- `account_cost_type`: `scheduled` | `variable` | `null` — vedi ADR-026

**Estensione Sessione 8 — `accounts.type` semantico (vedi ADR-061):**
Aggiunta colonna `accounts.type` che esprime la natura semantica del conto in termini comprensibili all'utente:
- `portfolio` — soldi tuoi (conti, contanti, carte di credito)
- `income` — entrate
- `expense` — spese
- `loan` — crediti/debiti personali (segno dinamico)

Obbligatoria sui conti root (`parent_id IS NULL`), ereditata dai figli. Coerente con `account_type` e `display_sign`. Dettaglio completo in ADR-061.

**Estensione Sessione 8 — flag `extraordinary` (vedi ADR-061):**
Aggiunta colonna `accounts.extraordinary boolean default false`. Indica che il conto traccia movimenti straordinari da escludere dalle statistiche di gestione corrente per default. Ereditato sul movimento, sovrascrivibile per singola riga.

---

### ADR-007 — Piano dei conti: origini multiple
**Data:** 2026-05-01
**Stato:** ✅ Deciso (esteso in Sessione 8: struttura del template predefinito)

**Decisione:**
1. Template predefinito da noi (sempre disponibile)
2. Generazione AI-assistita (capability)
3. Import da schema JSON esterno (capability)

**Estensione Sessione 8 — struttura del template predefinito:**

Il piano predefinito deve includere conti root pre-classificati con `accounts.type` (ADR-061). Canovaccio iniziale (la struttura editoriale di dettaglio è lavoro separato):

```
Portafoglio (type=portfolio)
├── Conti correnti
├── Contanti
└── Carte di credito

Entrate (type=income)
├── Stipendio
├── Rimborsi
└── Altri proventi

Spese (type=expense)
├── Casa
│   ├── Affitto/Mutuo
│   ├── Utenze
│   └── Manutenzione
├── Alimentari
├── Trasporti
├── Salute
├── Tempo libero
└── Altro

Prestiti (type=loan)
└── [vuoto: l'utente aggiunge i conti per persona]
```

Il ramo `Prestiti` parte vuoto perché i conti foglia sono per persona/entità specifica (vedi ADR-062). L'utente può rinominare etichette ma il `type` resta vincolante per le dashboard.

---

### ADR-008 — Template di registrazione: doppia origine
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
- Predefiniti da noi (contenuto editoriale)
- Creati e salvati dall'utente (capability)

I template si agganciano ai conti tramite `semantic_tag`, non per nome specifico.

---

### ADR-009 — Sistema a capability, non a piani rigidi
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
Ogni feature è un flag atomico. I piani commerciali sono bundle di capability. Il modello dati non conosce il concetto di "piano".

**Schema:**
- `capabilities` — definizione capability disponibili
- `user_capabilities` — assegnazione utente con scadenza opzionale e `granted_by`

---

### ADR-010 — Scenari: tipo e cardinalità
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
`scenario.type`: `personal` | `family` | `business`. Usato solo nel wizard. Gli scenari sono illimitati per natura — i limiti sono capability.

**Nota sul tipo `family`:**
Lo scenario family è progettato attorno alla coppia come unità minima. Il requisito UX primario è la semplicità: chi non ha competenze finanziarie deve poter usare il prodotto senza frizione. La cooperatività (visibilità condivisa, inserimento da più utenti) è il valore principale, non la granularità dei permessi.

---

### ADR-011 — Permessi: a livello di scenario
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
`scenario_users.role`: `viewer` | `editor`. Nessuna granularità a livello di conto.

**Motivazione family:** La cooperazione familiare è realizzata tramite scenario condiviso con più utenti `editor`. Non serve granularità maggiore — aggiunge complessità senza valore reale per il target.

---

### ADR-012 — Budget: entità separata
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
`budget_allocations (scenario_id, account_id, period, amount, status)`. Residuo calcolato on-the-fly. `status`: `active` | `closed`.

**Nota:** Il budget si applica esclusivamente ai conti `variable` (vedi ADR-026). I conti `scheduled` non hanno budget: le loro spese future sono già rappresentate come movimenti `previsto` con importo e data certi.

---

### ADR-013 — Onboarding wizard obbligatorio
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
Feature core, obbligatorio al primo accesso, richiamabile in futuro. Genera automaticamente la registrazione di apertura con i saldi iniziali.

---

### ADR-014 — Audit log: tabella separata + colonne sintetiche on-entity
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
- Colonne sintetiche su ogni entità: `created_at`, `updated_at`, `created_by`
- Tabella `audit_log` separata: `entity_type`, `entity_id`, `action`, `payload_before`, `payload_after`, `user_id`, `timestamp`
- Scrittura asincrona tramite Observer Laravel
- Retention policy da definire (decisione aperta)

---

### ADR-015 — ULID come chiave primaria
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
ULID su tutte le entità (`char(26)`). Libreria: `robinvdvleuten/ulid`.

---

### ADR-016 — Soft delete selettivo
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
- Soft delete: `users`, `scenarios`, `accounts`, `budget_allocations`, `capabilities`, `recurring_rules`
- No soft delete: `registrations`, `movements` — si rettificano contabilmente

---

### ADR-017 — API versioning da subito
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
Prefisso `/api/v1/` su tutti gli endpoint dal primo commit.

---

### ADR-018 — Formato response: JSON:API spec
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
JSON:API spec come formato response. Libreria da valutare in sessione Backend Architect.

---

### ADR-019 — Sistema webhook + WebSocket event-driven
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
Architettura event-driven nativa Laravel. Due delivery mechanism:
- Webhook HTTP — consegna agli endpoint utente configurati
- WebSocket — push real-time al frontend PWA (incluse notifiche in-app)

Accesso tramite capability. Infrastruttura predisposta subito, implementazione rimandata.

**Schema da predisporre:**
- `webhook_subscriptions (user_id, event, endpoint_url, secret, active)`
- `webhook_deliveries (subscription_id, payload, status, attempts, last_attempt_at)`

WebSocket: Reverb vs Soketi — decisione aperta, assegnata a Backend Architect.

---

### ADR-020 — MCP server esposto agli utenti
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
MioTesoro espone un MCP server per integrare qualsiasi AI client. Layer separato sopra le API REST. Accesso tramite capability.

---

### ADR-021 — Security layer
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
- Rate limiting per endpoint (Laravel throttle middleware)
- API key management per accesso programmatico
- HMAC per verifica payload webhook
- Cloudflare come proxy layer — decisione aperta, assegnata a Security & Infra

---

### ADR-022 — Branch strategy: dev + main
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
- `dev` → deploy automatico su staging
- `main` → produzione, solo da merge esplicito
- Nessun push diretto a main

---

### ADR-023 — Deploy workflow: GitHub Actions + SSH
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
GitHub Actions con script bash via SSH. Zero costi aggiuntivi.

---

### ADR-024 — Infrastruttura: Docker Compose su VPS Hetzner
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
Due stack Docker separati sullo stesso VPS:
- `docker-compose.prod.yml` — produzione (branch main)
- `docker-compose.staging.yml` — staging (branch dev)

Ogni stack: 3 container separati (backend, frontend, database). DB isolati.

---

### ADR-025 — Architettura multi-agente
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
7 Project Claude specializzati + 1 orchestratore (questo) + Claude Code per implementazione.

**Fase 1 — bloccante (parallela):**
- MioTesoro — DB Architect → schema SQL completo
- MioTesoro — Backend Architect → struttura Laravel + API contract

**Fase 2 — dopo schema DB:**
- MioTesoro — Frontend → PWA React + component tree
- MioTesoro — AI & Integrations → Claude API, MCP, webhook
- MioTesoro — QA & Testing (Fase 1) → strategia test, QA_STRATEGY.md per Claude Code

**Fase 3 — quando il prodotto è definito:**
- MioTesoro — Security & Infra → Docker, CI/CD, Cloudflare
- MioTesoro — Product, Brand & Comms → pricing, brand identity, sito web, lancio
- MioTesoro — Legal & Compliance → documenti legali, flussi consenso, checklist GDPR
- MioTesoro — QA & Testing (Fase 2) → esecuzione test su codice implementato, bug report

**Track parallelo da subito:**
- MioTesoro — Product, Brand & Comms → payoff, palette, profilo target (non aspetta lo sviluppo)

**Claude Code** — implementazione finale alimentata dai documenti dei Project specializzati.

**DECISIONS.md** è il documento di sincronizzazione che attraversa tutti i livelli.

---

## Sessione 2 — 2026-05-01
### Focus: Product vision, cashflow simulato, conti scheduled/variable, ricorrenze, AI capabilities, notifiche

---

### ADR-026 — Classificazione conti economici: scheduled vs variable
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
Colonna `account_cost_type` su `accounts`, applicabile solo ai conti `account_type = economic`:
- `scheduled` — spese con data e importo certi (mutuo, rate assicurazione, abbonamenti fissi). Generano movimenti `previsto` espliciti. Nel cashflow pesano per il loro importo esatto.
- `variable` — spese non predeterminabili (alimentari, carburante, svago). Coperti da budget mensile aggregato. Nel cashflow pesano come `MAX(budget_mese - già_speso_mese, 0)`.
- `null` — conti patrimoniali o conti economici di entrata (non si applica).

**Motivazione:**
La distinzione è stabile al 99% dei casi: le spese programmate finiscono sempre in conti dedicati. Imporre la classificazione a livello di conto semplifica il modello e rende le query di cashflow deterministiche.

---

### ADR-027 — Cashflow simulato: logica di calcolo
**Data:** 2026-05-01
**Stato:** ✅ Deciso (aggiornato in Sessione 7: orizzonte rivisto da illimitato a 12 mesi)

**Decisione:**
Il cashflow simulato è una **view calcolata**, non un'entità persistita. Aggrega tre layer:

1. Movimenti `eseguito` — passato certo
2. Movimenti `previsto` — futuro certo (importo e data espliciti, inseriti dall'utente o generati dal wizard annuale — vedi ADR-060)
3. Budget residuo da conti `variable` — futuro stimato: `MAX(budget_mese - speso_mese, 0)`, si azzera se sforato

Il contributo del budget variabile non può mai essere negativo: lo sforamento è già nei movimenti `eseguito`.

**Orizzonte temporale:** massimo 12 mesi (anno solare corrente). Conseguenza diretta del modello "wizard annuale" introdotto da ADR-060: i movimenti `previsto` esistono solo per l'anno in corso. A gennaio l'utente vede 12 mesi avanti, a novembre ne vede 1–2. Il wizard di dicembre estende la visibilità all'anno successivo.

**Storia:**
La sessione 2 aveva stabilito orizzonte illimitato in avanti (dipendente da `recurring_rules` + task schedulato). La revoca di ADR-028 in sessione 7 e l'introduzione del modello wizard annuale (ADR-060) limitano l'orizzonte a 12 mesi.

---

### ADR-028 — Movimenti ricorrenti: recurring_rules + generazione schedulata
**Data:** 2026-05-01
**Stato:** ❌ **Revocata in Sessione 7 (2026-05-05)**

**Motivazione della revoca:**
Il modello a `recurring_rules` + task schedulato è stato sostituito da un modello più semplice e centrato sull'utente: movimenti pluriennali con campo `repeat_until_year` + wizard annuale guidato. Vedi ADR-060.

**Cosa cambia concretamente:**
- Nessuna entità "regola ricorrente" separata
- I movimenti `previsto` non vengono mai generati automaticamente
- L'utente è sempre nel loop: inserisce i movimenti del primo anno singolarmente, poi a dicembre conferma il rollover all'anno successivo
- Cashflow orizzonte 12 mesi (vedi ADR-027 aggiornata)

**Decisione originale (mantenuta come storico):**

Tabella `recurring_rules` + task Laravel schedulato che genera movimenti `previsto` sull'orizzonte configurato.

**Schema `recurring_rules`:**
```
recurring_rules (
  id ulid PK,
  scenario_id ulid FK,
  account_id ulid FK,
  description text,
  amount decimal,
  frequency enum('daily','weekly','monthly','quarterly','yearly'),
  start_date date,
  end_date date nullable,
  next_generation_date date,
  generation_horizon_months int default 13,
  created_at, updated_at, created_by, deleted_at
)
```

**Comportamento originale:**
- Task schedulato mensile (+ trigger manuale da UI)
- Genera movimenti `previsto` fino a `now + generation_horizon_months`
- Modifica regola → ricalcolo movimenti futuri non ancora `eseguito`
- Movimenti già `eseguito` non vengono mai toccati
- Soft delete su `recurring_rules`

**Implicazioni della revoca:**
- Decisione aperta #13 (generation horizon) → chiusa, concetto non si applica più
- Decisione aperta #14 (soglia notifica orizzonte) → ridefinita come "data apparizione notifica wizard annuale" (vedi ADR-060)
- Lo schema `recurring_rules` non viene implementato

---

### ADR-029 — AI capabilities: tre funzioni distinte
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
Le capability AI sono tre funzioni architetturalmente separate:

**A — Voice input per data entry**
- Messaggio vocale → trascrizione → pre-compilazione registrazione
- Implementazione: Claude API con tool use
- 🔶 Provider speech-to-text da valutare (Whisper vs browser nativo) — decisione aperta AI & Integrations

**B — Auto-categorizzazione per pattern e abitudini**
- Il sistema impara le abitudini utente (descrizione → conto di default)
- Suggerisce conto/template al momento del data entry
- 🔶 Strategia (embedding vs few-shot) — decisione aperta AI & Integrations

**C — Parser estratti conto per-utente (differenziatore competitivo)**
- Utente carica estratto conto (PDF, CSV, XLS)
- Claude genera parser personalizzato per quel formato bancario
- Il parser viene salvato e riutilizzato automaticamente per lo stesso istituto
- Nessun competitor lo fa in modo user-friendly

Tutte e tre accesso tramite capability.

---

### ADR-030 — Sistema notifiche e task in-app
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
Entità `notifications` persistita su DB con due tipi di comportamento:

- `task` — persiste fino ad azione completata. Non chiudibile con sola lettura. Riappare finché l'utente non esegue l'azione collegata o la ignora esplicitamente.
- `info` — chiusa con marcatura come letta.

Le notifiche possono avere un'azione strutturata collegata (endpoint + payload) oppure essere solo informative.

**Generazione:** esclusivamente dal sistema. Notifiche create dall'utente — out of scope, in Sviluppi Futuri.

**Delivery:** WebSocket in-app (ADR-019) + persistenza DB.

**Schema:**
```
notifications (
  id ulid PK,
  user_id ulid FK,
  scenario_id ulid FK nullable,
  type enum('task','info'),
  title text,
  body text,
  action_endpoint text nullable,
  action_payload jsonb nullable,
  read_at timestamp nullable,
  completed_at timestamp nullable,
  expires_at timestamp nullable,
  created_at
)
```

**Primo caso d'uso:** rigenerazione movimenti ricorrenti quando l'orizzonte pianificato si riduce sotto soglia.

---

### ADR-031 — Sequenza di esecuzione: prossimi step
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Track A — Sviluppo (sequenziale):**

| Fase | Agente | Output atteso | Dipendenze |
|------|--------|--------------|------------|
| 1 | DB Architect | Schema SQL completo, migration order, indici | Nessuna |
| 1 | Backend Architect | Struttura Laravel, service layer, API contract | Nessuna |
| 2 | Frontend | PWA React + TypeScript, component tree, routing | Schema DB + API contract |
| 2 | AI & Integrations | Claude API, MCP server, parser estratti conto, voice input | Schema DB + API contract |
| 2 | QA — Fase 1 | QA_STRATEGY.md: framework, convenzioni, aree critiche, E2E scenari | API contract + schema DB |
| 3 | Security & Infra | Docker Compose definitivo, CI/CD, Cloudflare | Architettura completa |
| 3 | Legal & Compliance | Bozze documenti legali, flussi consenso in-app, checklist GDPR operativa | Funzioni AI + architettura definite |
| 3 | QA — Fase 2 | Esecuzione test, bug report prioritizzato (critical/major/minor) | Codice implementato da Claude Code |

**Track B — Brand & Go-to-market (parallelo da subito):**

| Priorità | Agente | Output atteso | Note |
|----------|--------|--------------|------|
| Immediata | Product, Brand & Comms | Payoff, palette colori, logo brief | Nome già deciso: MioTesoro |
| Immediata | Product, Brand & Comms | Profilo target primario, struttura free tier, pricing draft | Orienta le priorità di sviluppo |
| Breve termine | Product, Brand & Comms | Coming soon / lista d'attesa online, canali social attivi | Prima che l'app sia pronta |
| Medio termine | Product, Brand & Comms | Strategia lancio completa, piano contenuti | Prima del rilascio |

**Claude Code** — implementazione finale, alimentato dai documenti di tutti gli specialisti.

---

### ADR-032 — Architettura web: sito marketing separato dall'app
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
Due domini separati con ruoli distinti:
- `miotesoro.it` → sito marketing (WordPress o statico) — SEO, pricing, blog, conversione, strategia di lancio
- `miotesoro.app` → PWA Laravel/React — l'applicazione

**Motivazione della struttura domini:**
- `.it` è il dominio principale per il mercato italiano: più autorevole per SEO locale, segnala chiaramente le radici italiane del prodotto
- `.app` è il TLD più coerente per una PWA: HTTPS-only per policy del registry, comunica immediatamente "questo è un'applicazione", trattato bene da Google
- `.com` (miotesoro.com — non acquisito, seller a 2500 USD — non prioritario): se disponibile in futuro, redirect su .it, protezione brand

**Autenticazione:** vive esclusivamente su `miotesoro.app`. Il sito marketing non gestisce utenti. Il CTA "Inizia gratis" / "Accedi" reindirizza su `miotesoro.app`. Nessuna area riservata sul sito marketing.

**Social login:** supportato sull'app tramite Laravel Socialite.
- Google → priorità assoluta
- Apple → da supportare (obbligatorio per futura app iOS nativa)
- Facebook → escluso inizialmente

**Stack sito marketing:** WordPress vs alternativa statica — decisione aperta, assegnata a Product & Comms.

**Strategia di lancio:** da costruire con anticipo rispetto al rilascio dell'app. Include: sito vetrina / coming soon, lista d'attesa, canali social, eventuale beta chiusa. Assegnata a Product & Comms come priorità immediata.

---

### ADR-033 — Brand identity: da costruire da zero
**Data:** 2026-05-01
**Stato:** ✅ Deciso (perimetro), 🔶 Ipotesi (contenuto)

**Decisione:**
Il progetto parte con il nome definitivo **MioTesoro** (vedi ADR-039). Rimane da costruire:
- **Payoff** — da definire, deve comunicare il differenziatore core (controllo finanziario senza complessità)
- **Palette colori** — da definire, uso su app + sito marketing + social
- **Logo** — da produrre dopo palette. 🔶 Modalità di produzione da decidere (vedi decisione aperta #19)
- **Tono di voce** — da definire, coerente con il target (professionale ma accessibile, non bancario)

**Assegnato a:** Product, Brand & Comms — priorità immediata, non aspetta lo sviluppo.

**Implicazioni tecniche:**
- Il Frontend riceve la palette prima di iniziare la UI
- Il sito marketing non può partire senza colori e payoff
- Il social può partire subito con il nome MioTesoro

---

## Sessione 3 — 2026-05-01
### Focus: Nome definitivo, struttura domini

---

### ADR-039 — Nome definitivo e struttura domini
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
- **Nome prodotto:** MioTesoro
- **Scrittura brand:** MioTesoro (camelCase, M e T maiuscole)
- **Dominio sito marketing:** miotesoro.it ✅ registrato
- **Dominio app:** miotesoro.app ✅ registrato
- **Dominio protezione:** miotesoro.com 🔶 non acquisito (seller a 2500 USD, non prioritario)

**Motivazione del nome:**
"MioTesoro" è una parola composta italiana con possessivo postposto — costruzione naturale e affettuosa in italiano ("amore mio", "tesoro mio"). Evoca ricchezza personale, protezione e cura. La scrittura camelCase rende immediatamente leggibili le due parole senza spazio, come WordPress o LinkedIn. Nessun conflitto trademark in classe 36 su EUIPO/TMView per Italia e UE. Nessun competitor fintech con questo nome.

**Verifica trademark eseguita:**
- TMView (database EUIPO): nessun marchio "mio tesoro" o "miotesoro" registrato in classe 36 in ambito EU. Unici risultati sono marchi giapponesi (JPO) — irrilevanti per il mercato italiano/europeo.
- **Prossimo step:** deposito marchio in classe 36 (+ classe 42 SaaS) su EUIPO — ~900€, copertura 27 paesi per 10 anni. Da eseguire prima del lancio pubblico.

**Chiude:** decisioni aperte #9 (Nome definitivo) e #16 (Dominio definitivo).

---

## Sessione 4 — 2026-05-02
### Focus: Pricing AI, modalità di accesso, configurabilità runtime, struttura tier, email transazionale, tracciamento consumo AI

---

### ADR-040 — Capability AI: tre funzioni distinte con modelli di costo separati
**Data:** 2026-05-02
**Stato:** ✅ Deciso

**Decisione:**
Le tre capability AI sono architetturalmente e commercialmente distinte:

- **A — Registrazione singola assistita** (`registration`): input testo o audio, output un movimento pre-compilato. Costo per chiamata basso e prevedibile. Candidata a piano flat.
- **B — Import massivo** (`import`): input qualsiasi (testo strutturato, copia-incolla caotico, screenshot, immagini), output batch di movimenti da confermare. Costo variabile e potenzialmente alto. Candidata a cap mensile o pay-per-use.
- **C — Parser persistente** (`parser`): chiamata AI una tantum che genera un template riutilizzabile per quel formato bancario. Gli import successivi non consumano AI. Modello di costo fondamentalmente diverso dagli altri due.

🔶 Tutto il blocco AI è sperimentale sul pricing. Si lancia, si misura il costo reale per chiamata, si aggiusta nel tempo.

**Nota:** il modello AI usato per ogni capability è configurabile dall'admin panel (vedi ADR-042). Non tutte le capability richiedono il modello top di gamma — la scelta per-capability è una leva di ottimizzazione dei costi.

---

### ADR-041 — Modalità di accesso AI: tre canali distinti
**Data:** 2026-05-02
**Stato:** ✅ Deciso (aggiornato in Sessione 5: rimossa modalità BYOK)

**Decisione:**
Tre modalità di accesso coesistono e sono complementari, non alternative:

| Modalità | AI provider | Costo AI | Accesso |
|----------|-------------|----------|---------|
| Platform AI | MioTesoro | Incluso nel piano AI | Piano AI |
| MCP | Utente (suo AI client esterno) | Sul suo account AI | Accesso MCP |
| No AI | Nessuno | Zero | Free o Pro |

**Modalità Platform AI:**
MioTesoro chiama provider AI configurati dall'admin (Anthropic, OpenAI, eventualmente altri) usando chiavi di piattaforma. Il modello e il provider per ogni capability sono configurabili a runtime senza deploy (ADR-042 esteso).

**Modalità MCP:**
L'utente usa il suo AI client esterno (Claude Desktop, altri). MioTesoro è puro dato e infrastruttura, non fa chiamate AI. Pricing dell'accesso MCP da definire indipendentemente (decisione aperta #24).

**Modalità No AI:**
Il prodotto funziona completamente senza AI. Vincolo non negoziabile (ADR-035).

**Storia:**
La sessione 4 aveva incluso una quarta modalità BYOK (chiavi Anthropic dell'utente). Revocata in sessione 5 con il passaggio a multi-provider — vedi ADR-036 revocato.

---

### ADR-042 — Configurabilità runtime: requisito implementativo non negoziabile
**Data:** 2026-05-02
**Stato:** ✅ Deciso (esteso in Sessione 4 e Sessione 5)

**Decisione:**
Tutto ciò che definisce il comportamento dei piani — capability incluse, limiti quantitativi, associazioni capability-piano, eccezioni per singolo utente — deve essere configurabile a runtime dall'admin senza modificare il codice.

**Estensione sessione 4 — configurabilità per-capability AI:**
Ogni capability AI deve avere nel pannello admin:
- **Modello configurabile** (es. `claude-haiku-4-5` vs `claude-sonnet-4-6`) — leva di ottimizzazione costi
- **Stato attivabile/disattivabile** — kill switch per singola capability senza deploy
- ~~Compatibilità BYOK: sì/no~~ — rimosso in sessione 5 con la revoca del BYOK (ADR-036)

**Estensione sessione 5 — multi-provider:**
La configurabilità per-capability AI include il **provider**, non solo il nome del modello. L'admin può scegliere per ogni capability:
- **Provider** (Anthropic, OpenAI, eventualmente altri)
- **Modello** all'interno del provider scelto

Questo abilita strategie come: capability A su Haiku Anthropic, STT su GPT-4o Mini OpenAI, capability C su Sonnet Anthropic. La scelta è una leva di ottimizzazione costi e qualità per-funzione.

**Implicazione architetturale:**
Il backend deve avere un layer di astrazione provider che esponga un'API uniforme verso il codice di business, mantenendo la possibilità di switchare provider senza riscrittura. Vedi ADR-058 (sessione 5) per il dettaglio architetturale del layer provider.

**Configurabilità admin-only:** la scelta del provider e del modello è esclusivamente dell'admin di piattaforma. L'utente che vuole controllare il modello ha il suo escape hatch: MCP (fa da sé con il suo client). Il BYOK è stato revocato proprio perché il multi-provider lo rendeva incompatibile.

**Esempi concreti di cosa deve essere configurabile senza toccare codice:**
- Numero massimo di movimenti nel piano Free
- Durata del trial in giorni
- Numero massimo di interazioni AI nel trial
- Quali capability sono incluse in quale piano
- Eccezioni per singolo utente (estendere trial, sbloccare capability)
- Soglie che triggerano notifiche
- Provider AI per ogni capability
- Modello AI per ogni capability (all'interno del provider scelto)
- Stato attivo/inattivo per ogni capability AI
- Prezzi listino per provider/modello (ADR-057)

---

### ADR-043 — Struttura tier pricing
**Data:** 2026-05-02
**Stato:** ✏️ **Da rivedere in Sessione 5** — la revoca del BYOK (ADR-036) impatta la differenziazione del piano Pro. Decisione tier rimandata esplicitamente, da riprendere dopo consolidamento del funzionamento dell'app.

**Decisione originale (mantenuta come baseline):**

| | Free | Pro | AI |
|--|------|-----|----|
| Scenari inclusi | 1 | 2 | 2 |
| Utenti per scenario | 1 | 2 | 2 |
| Cashflow previsionale | ✅ | ✅ | ✅ |
| Movimenti | Limitati (TBD) | Illimitati | Illimitati |
| AI registrazione singola (A) | ❌ | ❌ | ✅ |
| AI import massivo (B) | ❌ | ❌ | ✅ (cap mensile TBD) |
| AI parser persistente (C) | ❌ | ❌ | ✅ |
| ~~BYOK~~ | ~~❌~~ | ~~✅~~ | ~~alternativa al piano AI~~ |
| Add-on scenario aggiuntivo | ❌ | ✅ | ✅ |

**Cosa è cambiato in sessione 5:**
La riga BYOK è cancellata. Il piano Pro perde un benefit, e la sua differenziazione dal Free si riduce a scenari/utenti/movimenti. Tre direzioni possibili identificate ma non ancora scelte:
1. Pro resta così com'è — distinzione su scenari/utenti/movimenti basta
2. Pro include una quota AI base — un certo numero di interazioni/mese inclusi
3. Si fonde Pro e AI in un unico piano premium

**Trial:** accesso completo a tutto, AI inclusa con interazioni limitate, uno scenario, 2 utenti. Durata e limiti esatti da tarare dopo stime costi AI (✅ ora disponibili — vedi ADR-046).

**Logica tier scenari:** Free è il piano da provare senza pensarci. Pro a 2 scenari copre già il caso coppia/familiare (personale + condiviso) senza add-on immediato. L'add-on scenario serve chi scala ulteriormente (freelance + personale + famiglia).

**Pricing MCP:** accesso power user/developer, da prezzare indipendentemente dai piani AI platform. Decisione aperta #24.

🔶 I numeri — prezzi, limite movimenti Free, durata trial, limiti AI in trial, cap mensile import — restano da definire. Le stime di costo AI ora sono disponibili (ADR-046) ma serve prima consolidare il funzionamento dell'app.

**Naming dei tier:** lavoro di copywriting separato, assegnato a Product, Brand & Comms.

---

### ADR-044 — Email transazionale: SMTP configurabile da admin panel
**Data:** 2026-05-02
**Stato:** ✅ Deciso

**Decisione:**
Il sistema email è configurabile dall'admin panel senza toccare codice: host SMTP, porta, credenziali, mittente, nome mittente. Il pannello include una funzione "invia email di test" a indirizzo configurabile per verificare la configurazione.

**Fase iniziale:** SMTP locale/self-hosted. Sufficiente per volumi bassi delle prime fasi.

**Migrazione futura:** sostituzione con provider esterno (Postmark, Resend, SES) senza modifiche al codice — solo riconfigurazione da admin panel.

**Lifecycle email minimo da implementare:** benvenuto, avviso scadenza trial imminente, avviso limite movimenti raggiunto, riattivazione utenti inattivi. Va integrato con il sistema notifiche (ADR-030). È funnel di conversione, non nice-to-have.

**Assegnato a:** Backend Architect.

---

### ADR-045 — Tracciamento consumo AI: tabella ai_usage_log
**Data:** 2026-05-02
**Stato:** ✅ Deciso (esteso in Sessione 5: aggiunta colonna `provider`, rimosso `byok` da `mode`)

**Decisione:**
Tabella dedicata per il tracciamento granulare del consumo AI. Infrastruttura analitica obbligatoria — senza questo dato non è possibile prezzare correttamente né ottimizzare i costi nel tempo.

**Schema (aggiornato sessione 5):**
```
ai_usage_log (
  id ulid PK,
  user_id ulid FK,
  scenario_id ulid FK nullable,
  capability enum('registration','import','parser','stt'),
  provider varchar,         -- es. 'anthropic', 'openai'
  model varchar,            -- es. 'claude-haiku-4-5', 'gpt-4o-mini-transcribe'
  tokens_input int,
  tokens_output int,
  cost_estimated decimal,
  mode enum('platform','mcp'),  -- rimosso 'byok' in sessione 5
  created_at timestamp
)
```

**Note:**
- Le chiamate MCP non generano righe in questa tabella perché MioTesoro non fa chiamate AI in quella modalità
- Il valore `byok` è stato rimosso dal campo `mode` con la revoca dell'ADR-036
- La capability `stt` traccia le chiamate Speech-to-Text (ADR-047)
- Il calcolo di `cost_estimated` legge da `ai_model_pricing` (ADR-057) per supportare cambi prezzo storicizzati

**Assegnato a:** DB Architect.

---

## Sessione 5 — 2026-05-02
### Focus: AI & Integrations — costi, modelli, STT, memoria AI, pipeline import, multi-provider

**Contesto:** La sessione con AI & Integrations ha prodotto 11 ADR (046–056). Durante il merge in orchestrazione sono emerse due decisioni architetturali aggiuntive: la revoca del BYOK (ADR-036) per incompatibilità con il multi-provider, e la formalizzazione del multi-provider stesso con prezzi listino configurabili (ADR-057, ADR-058).

**Decisioni aperte chiuse in questa sessione:** #11 (STT provider), #12 (auto-categorizzazione), #20 (costi AI), #21 (selezione modello).

**Modifiche a ADR esistenti:**
- ADR-036 → ❌ Revocata (BYOK eliminato)
- ADR-041 → 4 modalità → 3 modalità (rimossa BYOK)
- ADR-042 → Estesa con dimensione provider (multi-provider configurabile)
- ADR-043 → ✏️ Da rivedere (impatto revoca BYOK su tier Pro)
- ADR-045 → Schema esteso (`provider`, capability `stt`, rimosso `byok` da `mode`)

---

### ADR-046 — Modelli AI default per capability
**Data:** 2026-05-02
**Stato:** ✅ Deciso

**Decisione:**

| Capability | Modello default | Costo tipico/chiamata |
|------------|----------------|----------------------|
| A — Registrazione singola | `claude-haiku-4-5` | $0.001 (con caching) |
| B — Import testo | `claude-haiku-4-5` | $0.020 (30 righe) |
| B — Import vision (immagini) | `claude-sonnet-4-6` | $0.055 (1 pagina) |
| C — Parser persistente | `claude-sonnet-4-6` | $0.096 (una tantum) |

**Routing automatico testo/immagine** in capability B: il sistema rileva il MIME type dell'input e seleziona il modello appropriato. Questa scelta è la leva di ottimizzazione costi più significativa: testi su Sonnet costerebbero il triplo senza beneficio qualitativo.

**Configurabilità runtime (ADR-042 esteso):** questi sono default iniziali. L'admin può modificare provider e modello per ogni capability senza deploy.

**Proiezione costi piano AI tipico** (30 registrazioni/mese + 1 import testo + 0.3 import vision): ~$0.10/utente/mese. A $5/mese di prezzo del piano AI, costo AI = 2% del ricavo.

**Chiude:** decisioni aperte #20 e #21.

---

### ADR-047 — Speech-to-Text: GPT-4o Mini Transcribe (OpenAI)
**Data:** 2026-05-02
**Stato:** ✅ Deciso

**Decisione:**
Layer di preprocessing audio separato dalle capability AI di MioTesoro. Provider: OpenAI GPT-4o Mini Transcribe a $0.003/min.

**Motivazione:**
- Costo per registrazione singola (10–30s audio): ~$0.001 — trascurabile
- Qualità eccellente per italiano, copertura 99+ lingue
- API standardizzata: migrazione futura a Whisper self-hosted o altro provider fattibile senza riscrittura
- Web Speech API rifiutata: qualità incoerente tra browser, Safari mobile limitato, rischio reputazionale per un prodotto che ha la qualità AI come differenziatore
- Whisper self-hosted rifiutato in v1: VPS Hetzner attuale senza GPU, latenza CPU inaccettabile per UX real-time

**Validazione vincolo "solo Anthropic":**
La sessione 5 ha confermato che il vincolo nasceva da una scelta commerciale sul BYOK, non da una policy generale. Con il passaggio a multi-provider (ADR-042 esteso) e la revoca del BYOK (ADR-036), l'uso di OpenAI per lo STT è il caso normale, non un'eccezione.

**Costo combinato A+STT per registrazione singola:** ~$0.002 totali.

**Chiude:** decisione aperta #11.

---

### ADR-048 — Pipeline import: chunking + routing + schema output ottimizzato
**Data:** 2026-05-02
**Stato:** ✅ Deciso

**Decisione:**
La capability B (import) è una pipeline multi-fase, non una chiamata singola.

**Fasi:**
1. **Column detection** (solo se parser assente per quella banca) — chiamata leggera Haiku, ~$0.001
2. **Categorizzazione in chunk** — input spezzato in chunk da 40–50 righe massimo, chiamate parallele
3. **Validazione utente** — review delle proposte, nessuna chiamata AI
4. **Raffinamento iterativo** — solo righe ancora incerte dopo le correzioni utente, con few-shot dalle correzioni

**Vincoli implementativi:**
- Chunking obbligatorio lato server: max 50 righe per chunk Claude
- Limite per import: max 100 righe in singolo upload (configurabile, dipendente da decisioni #22–23)
- Routing automatico testo/immagine basato su MIME type
- Schema output compatto: chiavi corte (`a`, `v`, `d`, `n`, `c`) — risparmio 60–70% token output vs schema verboso

**Costo totale per import 100 righe banca nota:** ~$0.041
**Costo totale per import 200 righe banca nota:** ~$0.079

---

### ADR-049 — Validazione automatica del parser generato (capability C)
**Data:** 2026-05-02
**Stato:** ✅ Deciso

**Decisione:**
Pipeline di validazione obbligatoria post-generazione: il parser appena generato viene eseguito sull'estratto conto campione fornito dall'utente, l'output viene verificato (numero movimenti attesi, campi popolati correttamente, tipi corretti). Il parser viene salvato solo se la validazione passa.

**Motivazione:**
Generare codice PHP funzionante da un campione di estratto conto dipende dalla rappresentatività del campione. Un parser malfunzionante salvato silenziosamente comprometterebbe tutti gli import futuri di quella banca per quell'utente.

**Eventuale chiamata di retry:** se la validazione fallisce, una seconda chiamata Sonnet con il feedback dell'errore. Max 2 retry, poi escalation all'utente con messaggio "non riusciamo a generare automaticamente un parser per questo formato".

---

### ADR-050 — Preferenze merchant: ai_merchant_preferences a livello di scenario
**Data:** 2026-05-02
**Stato:** ✅ Deciso

**Schema:**
```sql
ai_merchant_preferences (
  id                ulid PK,
  scenario_id       ulid FK → scenarios,
  created_by        ulid FK → users,
  updated_by        ulid FK → users nullable,

  merchant_pattern  varchar(200),    -- description_prefix normalizzato
  account_id        ulid FK → accounts,
  note              text nullable,   -- linguaggio naturale, letto da Claude
  semantic_tags     text[],          -- estratti da nota + descrizione

  confirmed_count   int default 0,

  created_at        timestamp,
  updated_at        timestamp,
  deleted_at        timestamp nullable,  -- soft delete

  UNIQUE (scenario_id, merchant_pattern)
)
```

**Ambito:** scenario, non utente. Una coppia che gestisce uno scenario family condiviso vede e modifica le stesse preferenze.

**Comportamento:**
- L'esistenza di una riga = decisione esplicita di ricordare
- La nota libera è interpretata da Claude a runtime, non valutata in codice
- L'assenza di una riga = nessuna preferenza, sistema usa solo storico (Livello 2)
- Soft delete coerente con ADR-016

---

### ADR-051 — Due livelli di memoria AI
**Data:** 2026-05-02
**Stato:** ✅ Deciso

**Decisione:**
La categorizzazione AI usa due fonti di contesto distinte e complementari.

**Livello 1 — Regole esplicite**
- Fonte: tabella `ai_merchant_preferences` (ADR-050)
- Attivazione: l'utente sceglie esplicitamente di salvare un'associazione
- Peso nel prompt: contesto forte, applicato direttamente
- Bypass AI: SI se la preferenza non ha nota libera (match meccanico); NO se ha nota (Claude deve interpretarla)

**Livello 2 — Storico inferito**
- Fonte: query aggregata su `movements.description_prefix` e `movements.semantic_tags`
- Attivazione: automatica
- Peso nel prompt: contesto suggestivo
- Bypass AI: NO, sempre necessaria chiamata

**Livello 3 — Categorizzazione live**
Quando i primi due non producono match: Claude ragiona puramente da descrizione + piano dei conti.

**Pipeline per ogni riga di un import:**
```
1. Match Livello 1 (preferenza esplicita)?
   → Senza nota: applica direttamente, no AI
   → Con nota: includi in prompt, chiama AI
2. Storico Livello 2 disponibile?
   → Sì: includi nel prompt come contesto
3. Chiama AI per ragionamento finale (se non bypassata)
```

---

### ADR-052 — Flag autosuggest a livello scenario
**Data:** 2026-05-02
**Stato:** ✅ Deciso

**Decisione:**
- Colonna `scenarios.ai_autosuggest boolean default true`
- Override per singolo import come parametro della richiesta HTTP, non persistito
- Quando OFF: il sistema non inietta le preferenze esplicite nel prompt — Claude ragiona solo da descrizione + storico

**Motivazione:**
Permette all'utente di ottenere una "second opinion" dal sistema su un import specifico, senza essere influenzato dalle proprie scelte passate. Caso d'uso: revisione periodica delle proprie categorizzazioni.

**Chiude:** decisione aperta #12.

---

### ADR-053 — Lifecycle delle preferenze
**Data:** 2026-05-02
**Stato:** ✅ Deciso

**Modifica preferenza** (es. cambio `account_id` o nota):
- I movimenti storici NON vengono toccati — restano con la categorizzazione precedente
- `confirmed_count` viene resettato a zero (le conferme precedenti riguardavano una regola diversa)
- `updated_at` e `updated_by` aggiornati

**Cancellazione preferenza:**
- Soft delete (`deleted_at`)
- I movimenti storici NON vengono toccati
- Le prossime importazioni tornano a usare solo Livello 2 (storico)

**Conflitti su scenario family** (più editor):
- Last-write-wins
- Notifica `info` (ADR-030) all'utente che aveva creato la preferenza, informandolo del cambio
- `created_by` rimane invariato, `updated_by` riflette l'ultimo modificatore

---

### ADR-054 — Indicizzazione descrizioni: prefix + tag
**Data:** 2026-05-02
**Stato:** ✅ Deciso

**Decisione:**
Su `movements` due colonne complementari per matching efficiente:

```sql
movements.description_prefix    varchar(50)   -- deterministico, calcolato in PHP
movements.semantic_tags         text[]        -- estratti da Claude
movements.tags_user_validated   boolean default false

CREATE INDEX idx_mov_prefix ON movements (scenario_id, description_prefix);
CREATE INDEX idx_mov_tags   ON movements USING GIN (semantic_tags);
```

**`description_prefix`** — primi N caratteri della descrizione raw dopo strip dei prefissi noti (`PAGAMENTO POS`, `ADDEBITO SEPA`, `BONIFICO`, ecc.). Calcolato in PHP, deterministico, zero costo AI. Lunghezza N e lista prefissi da tarare empiricamente sui formati delle banche italiane principali (Intesa, UniCredit, BancoPosta, ING) prima del lancio — decisione aperta #27.

**`semantic_tags`** — array di tag estratti da Claude come campo dell'output JSON di import. Costo aggiuntivo trascurabile (~$0.004 su 100 righe). Esempi: `["esselunga","supermercato"]`, `["condominio","spese-casa","sepa"]`.

**Estensioni PostgreSQL da abilitare:** `pg_trgm` per fuzzy matching su `description_prefix` (mitigazione varianza normalizzazione).

**Nota di rischio:** la normalizzazione tramite Claude non è 100% deterministica. Mitigazioni: regole rigide nel system prompt + `description_prefix` deterministico in PHP + fuzzy matching con `pg_trgm`. Da validare empiricamente sui primi mesi di dati reali.

---

### ADR-055 — Tracciamento granulare proposte AI
**Data:** 2026-05-02
**Stato:** ✅ Deciso

**Decisione:**
Tabella `ai_proposal_feedback` registra per ogni proposta AI tre stati temporali distinti: cosa ha proposto l'AI, cosa ha giudicato l'utente, cosa è stato effettivamente registrato.

```sql
ai_proposal_feedback (
  id                      ulid PK,
  scenario_id             ulid FK → scenarios,
  user_id                 ulid FK → users,

  -- contesto della proposta
  capability              enum('registration','import'),
  model_used              varchar,
  prompt_version          varchar,

  -- origine della proposta
  source_description      text,
  description_prefix      varchar(50),
  semantic_tags           text[],

  -- 1. COSA HA PROPOSTO L'AI
  proposed_account_id     ulid FK → accounts,
  proposed_confidence     decimal,
  proposed_at             timestamp,

  -- 2. COSA HA GIUDICATO L'UTENTE
  explicit_feedback       enum('correct','neutral','wrong') nullable,
  judged_at               timestamp nullable,

  -- 3. COSA È STATO EFFETTIVAMENTE REGISTRATO
  final_account_id        ulid FK → accounts nullable,
  final_at                timestamp nullable,
  movement_id             ulid FK → movements nullable,

  -- contesto utilizzato
  used_explicit_preference  boolean,
  used_historical_context   boolean,

  created_at              timestamp
)
```

**Feedback a quattro stati:**
- `correct` — 👍 esplicitamente confermata
- `neutral` — 😐 corretta ma non adatta
- `wrong` — 👎 esplicitamente sbagliata
- `null` — nessun feedback esplicito (segnale solo da accept/correct)

**Retention:** 24 mesi rolling, allineabile con audit log (decisione aperta #3).

**Uso:**
- Operativo: identificare merchant problematici, A/B test modelli (ADR-042), tarare prompt
- NON per training di modelli custom (vincolo ADR-035)

---

### ADR-056 — Vocabolario tag come entità gestita + correzione granulare
**Data:** 2026-05-02
**Stato:** ✅ Deciso

**Schema:**
```sql
ai_tags (
  id              ulid PK,
  scenario_id     ulid FK → scenarios,

  tag             varchar(50),
  status          enum('active','disabled') default 'active',
  source          enum('ai_generated','user_created') default 'ai_generated',

  occurrences     int default 0,
  first_seen_at   timestamp,
  last_seen_at    timestamp,

  disabled_at     timestamp nullable,
  disabled_by     ulid FK → users nullable,

  created_at      timestamp,
  updated_at      timestamp,
  deleted_at      timestamp nullable,

  UNIQUE (scenario_id, tag)
)
```

**Due livelli di intervento utente:**

**Livello A — Correzione granulare su singolo movimento**
- Rimozione di un tag specifico da `movements.semantic_tags`
- Decremento di `occurrences` in `ai_tags` per quel tag
- Effetto: la riga corretta non contribuisce più a quel pattern nel Livello 2
- Il tag continua a esistere ed essere attivo nel vocabolario

**Livello B — Disabilitazione tag dal vocabolario**
- `ai_tags.status = 'disabled'`
- Non viene più suggerito a Claude né accettato in nuovi movimenti
- Movimenti storici non vengono toccati

**Comportamento del prompt:**
Il system prompt include i tag attivi dello scenario come whitelist preferenziale. Tag `disabled` non vengono passati. Soft delete coerente con ADR-016.

---

### ADR-057 — Tabella prezzi modelli configurabile da admin
**Data:** 2026-05-02
**Stato:** ✅ Deciso

**Decisione:**
I prezzi listino dei modelli AI sono configurabili da admin panel, con storicizzazione per validità temporale. Necessario perché:
- I provider cambiano i prezzi nel tempo
- Ogni provider ha il suo listino
- I costi storici devono restare corretti anche quando i prezzi cambiano

**Schema:**
```sql
ai_model_pricing (
  id                          ulid PK,
  provider                    varchar,    -- es. 'anthropic', 'openai'
  model                       varchar,    -- es. 'claude-haiku-4-5', 'gpt-4o-mini-transcribe'

  input_price_per_mtok        decimal,    -- $/M token input
  output_price_per_mtok       decimal,    -- $/M token output
  cache_hit_price_per_mtok    decimal nullable,  -- $/M token su cache hit (Anthropic)
  audio_price_per_minute      decimal nullable,  -- $/min audio (STT)

  valid_from                  timestamp,
  valid_to                    timestamp nullable,  -- null = vigente

  created_at                  timestamp,
  updated_at                  timestamp,
  created_by                  ulid FK → users,

  UNIQUE (provider, model, valid_from)
)
```

**Calcolo `cost_estimated` in `ai_usage_log`:**
Al momento della scrittura della riga, lookup su `ai_model_pricing` per `(provider, model)` con `valid_from <= now < valid_to OR valid_to IS NULL`. Il costo calcolato viene cristallizzato nella riga di log — non si ricalcola retroattivamente.

**Aggiornamento prezzi:** quando un provider cambia listino, l'admin chiude la riga corrente (set `valid_to = now`) e ne crea una nuova con `valid_from = now`. Le righe storiche di `ai_usage_log` mantengono il costo originale.

**Assegnato a:** DB Architect per schema, Backend Architect per logica di lookup e cristallizzazione costo.

---

### ADR-058 — Layer di astrazione provider AI
**Data:** 2026-05-02
**Stato:** ✅ Deciso

**Decisione:**
Il backend deve esporre un layer di astrazione provider che mascheri al codice di business la differenza tra provider AI diversi. Il codice di business chiama il layer con parametri di alto livello (capability, input, parametri opzionali), il layer:
1. Legge la configurazione corrente per quella capability (provider + modello scelti dall'admin)
2. Costruisce la chiamata nel formato del provider scelto
3. Esegue la chiamata
4. Normalizza la risposta in un formato uniforme
5. Scrive `ai_usage_log` con `provider`, `model`, costo cristallizzato da `ai_model_pricing`

**Provider supportati in v1:**
- `anthropic` — capability A, B (testo e vision), C
- `openai` — capability `stt`

**Estendibilità:** aggiungere un provider in futuro (es. provider open-source self-hosted, altro provider commerciale) deve richiedere solo l'implementazione di un'interfaccia provider e una riga di configurazione, senza modifiche al codice di business.

**Vincoli architetturali:**
- Nessun riferimento diretto a SDK provider-specifici nel codice di business
- Tutte le chiamate AI passano per il layer — nessuna eccezione, nemmeno per testing manuale
- Il layer è il punto unico in cui avviene il logging su `ai_usage_log` (ADR-045)

**Assegnato a:** Backend Architect per design dell'interfaccia provider e implementazione concreta.

---

## Sessione 6 — 2026-05-05
### Focus: Product, Brand & Comms — palette operativa, chiusura sessione brand

**Contesto:** Sessione con Product, Brand & Comms chiusa. La maggior parte dei deliverable (payoff, sito marketing, social, logo definitivo) è sospesa esplicitamente, non bloccante per lo sviluppo. L'unico output cristallizzato è la palette operativa, necessaria per sbloccare il Frontend in Fase 2.

**Conferme da sessione precedente:** ADR-041 a 3 modalità (BYOK abbandonato) — già recepito in Sessione 5, qui solo ribadito come stato corrente del progetto.

**Decisioni rimandate esplicitamente:**
- Pricing e tier — si riprendono dopo il primo funzionamento dell'app (decisioni aperte #8, #30)
- Payoff, sito marketing, canali social, strategia di lancio, logo definitivo — sospesi (decisioni aperte #15, #17, #18, #19)

---

### ADR-059 — Palette colori operativa
**Data:** 2026-05-05
**Stato:** ✅ Deciso (palette operativa) / 🔶 Scala estesa, varianti, accessibilità — sospesi

**Decisione:**

| Ruolo | Hex | Note |
|-------|-----|------|
| Viola primario | `#3D3B8E` | Brand color principale, usato per testo primario e elementi strutturali |
| Oro primario | `#F5C842` | Accento, usato per highlights, CTA secondarie, elementi decorativi |

**Logo bozza:** disponibile come asset SVG nel progetto (`logo-miotesoro-bozza.svg`). Composizione: tre monete d'oro accatastate + wordmark "MioTesoro" con "Mio" in viola e "Tesoro" in oro. Versione **non definitiva** — il logo definitivo è sospeso insieme al resto del lavoro brand.

**Cosa è incluso in questa decisione:**
- I due hex code primari, vincolanti per il Frontend
- La logica brand: viola = solidità/fiducia, oro = valore/tesoro (richiamo diretto al nome)
- Il logo bozza come riferimento operativo per Frontend, non come asset finale di lancio

**Cosa NON è incluso (sospeso):**
- Scala estesa della palette (varianti tonali, neutri, stati hover/active/disabled)
- Dark mode — palette dedicata da progettare
- Validazione contrasti WCAG AA/AAA su accoppiamenti viola/oro su fondi diversi
- Logo definitivo (versioni quadrata/orizzontale, favicon, monocromatica, white-on-dark)
- Tipografia di brand
- Iconografia di sistema

**Impatto operativo:**
- ✅ Frontend è sbloccato per partire in Fase 2 con la palette primaria
- 🔶 Frontend dovrà definire varianti tonali e contrasti tecnici come scelte tecniche temporanee, da rivalidare quando il lavoro brand riprende
- 🔶 Logo bozza utilizzabile in dev/staging — non utilizzabile per comunicazione pubblica

**Chiude:** parte del perimetro di ADR-033 (brand identity). Il resto resta aperto.

**Nuova decisione aperta introdotta:** #31 — Scala estesa palette + accessibilità + logo definitivo.

---

## Sessione 7 — 2026-05-05
### Focus: Modello movimenti pluriennali — sostituzione di ADR-028

**Contesto:** Discussione sull'orizzonte del cashflow simulato e sul meccanismo di generazione dei movimenti `previsto`. Il modello originale a `recurring_rules` + task schedulato (ADR-028) viene sostituito da un modello centrato sull'utente: movimenti singoli con campo `repeat_until_year` + wizard annuale guidato.

**Modifiche a ADR esistenti:**
- ADR-027 → orizzonte cashflow rivisto da illimitato a 12 mesi
- ADR-028 → ❌ Revocata

**Decisioni aperte chiuse / ridefinite:**
- #13 (generation horizon recurring_rules) → ✅ Chiusa, concetto non si applica
- #14 (soglia notifica orizzonte) → ridefinita come "data apparizione notifica wizard annuale", confermata 1 dicembre

---

### ADR-060 — Movimenti pluriennali: campo `repeat_until_year` + wizard annuale
**Data:** 2026-05-05
**Stato:** ✅ Deciso

**Decisione:**
Sostituisce ADR-028 in toto. Nessuna entità "regola ricorrente" separata. I movimenti pluriennali sono modellati come movimenti singoli con un campo `repeat_until_year` che indica l'ultimo anno fino al quale vanno propagati. La propagazione avviene esclusivamente tramite un wizard annuale guidato, mai automaticamente.

**Schema:**

Aggiunta su `movements`:
```sql
movements.repeat_until_year smallint nullable
-- valore: l'anno (es. 2049) fino al quale questo movimento deve essere
-- riproposto dal wizard annuale. NULL = movimento una tantum.
```

**Modello operativo:**

1. **Inserimento iniziale (primo anno)**
   - L'utente inserisce ogni movimento `previsto` singolarmente per l'anno in corso
   - Per il mutuo: inserisce 12 movimenti (uno per mese)
   - Su ognuno specifica `repeat_until_year` se il movimento si ripeterà negli anni successivi (es. 2049 per un mutuo che scade nel 2049)
   - I 12 movimenti del mutuo sono **autonomi e scollegati** tra loro (nessun `recurrence_group_id`)
   - UX: template di registrazione "dinamico" facilita l'inserimento sequenziale, ma ogni inserimento produce una registrazione separata. Decisione aperta sulla UX dettagliata del template (vedi #32)

2. **Wizard annuale (rollover)**
   - **Trigger:** notifica `task` (ADR-030) creata il **1 dicembre** di ogni anno
   - **Persistenza notifica:** la notifica resta visibile finché non viene processata, anche oltre il 31 dicembre — coerente con ADR-030 (task persiste fino ad azione completata)
   - **Comportamento del wizard:**
     - Il sistema seleziona tutti i movimenti dell'anno corrente con `repeat_until_year >= anno_corrente_+_1` per quello scenario
     - Li propone in blocco come candidati per la duplicazione all'anno successivo (stessa descrizione, stesso conto, stesso importo, stesso giorno/mese, anno +1, stesso `repeat_until_year`)
     - Default: tutti selezionati come "conferma"
     - L'utente può: deselezionare singoli movimenti (esclusione), modificare importi/date/conti prima di confermare, ignorare l'intero wizard
     - **Conferma** → il sistema crea le nuove righe in `movements` con stato `previsto`
     - **Ignora** → nessun movimento generato; la notifica resta visibile, l'utente "vedrà" il cashflow svuotarsi e potrà processare il wizard quando vuole

3. **Modifica di un movimento esistente**
   - Modificare un singolo movimento (es. importo) NON tocca gli altri della stessa serie
   - Le serie sono scollegate per design — un cambio di rata mutuo a metà anno richiede modifica delle singole rate residue, una per una

**Cashflow simulato:**
- Orizzonte massimo: 12 mesi (anno solare corrente, vedi ADR-027 aggiornata)
- A gennaio si vedono 12 mesi avanti, a novembre 1–2
- Il wizard di dicembre estende la visibilità all'anno successivo

**Cosa NON è in scope:**
- Inserimento agevolato come template "dinamico" — esiste come UX desiderata, ma il dettaglio di implementazione (form ripetitivo, copia da movimento esistente, ecc.) è una decisione aperta a Frontend + DB Architect
- Collegamento DB tra movimenti della stessa serie pluriennale — esplicitamente escluso. Se in futuro emerge il bisogno (es. "modifica tutte le rate del mutuo in blocco"), si introdurrà allora come campo aggiuntivo
- Generazione automatica di movimenti senza intervento utente — esclusa per principio

**Motivazione del modello:**
- Coerente con il principio "l'utente è sempre nel loop" che traversa tutto il prodotto
- Niente sorprese: il cashflow contiene esattamente quello che l'utente ha confermato
- Niente debito di task schedulati che possono fallire silenziosamente
- Lo sforzo iniziale di inserire 12 movimenti del primo anno è una tantum; il wizard annuale è una "Conferma" in blocco

**Trade-off accettati:**
- L'utente con 50 movimenti pluriennali vede a dicembre un wizard con 50 righe da scorrere; mitigato dal default "tutti confermati" e dal fatto che la fatica è bassa (deseleziona ciò che non serve, conferma)
- Il cashflow ha stagionalità naturale (12 mesi a gennaio, 1 a novembre); accettato come comportamento naturale del modello

**Nuove decisioni aperte introdotte:**
- #32 — UX template dinamico per inserimento agevolato di movimenti seriali (Frontend + DB Architect)

**Chiude:** decisione aperta #13. Ridefinisce #14.

---

## Sessione 8 — 2026-05-05
### Focus: Piano dei conti — tipologia semantica, prestiti personali, transaction_type derivato, flag extraordinary

**Contesto:** Discussione sulla struttura semantica del piano dei conti dal punto di vista dell'utente. Il modello DB esistente (ADR-006: `account_type` patrimonial/economic, `account_role`, `display_sign`) è contabilmente solido ma non sufficiente per costruire dashboard significative senza una classificazione di alto livello che l'utente comprenda. La sessione introduce `accounts.type` come strato semantico utente, modella i crediti/debiti personali come `loan` con segno dinamico, sposta la classificazione delle transazioni su un campo `transaction_type` derivato, e formalizza il flag `extraordinary` per statistiche di gestione corrente.

**Modifiche a ADR esistenti:**
- ADR-006 → estesa con `accounts.type` e flag `extraordinary`
- ADR-007 → estesa con struttura del template predefinito

---

### ADR-061 — Tipologia semantica dei conti (`accounts.type`) e flag `extraordinary`
**Data:** 2026-05-05
**Stato:** ✅ Deciso

**Problema:**
Il modello DB esistente (`account_type` patrimonial/economic, `display_sign`, `account_role`) è corretto contabilmente ma non basta per le dashboard: il sistema non sa distinguere "questo conto è un'entrata" da "questo conto è una spesa" — entrambi sono `economic`, si differenziano solo per `display_sign`. Manca una classificazione di alto livello, comprensibile all'utente, che alimenti le statistiche di base.

**Decisione:**

**1. Colonna `accounts.type` con valori semantici hardcoded:**

```sql
accounts.type enum('portfolio','income','expense','loan')
```

| Valore | Significato | Esempi |
|--------|-------------|--------|
| `portfolio` | Strumento di pagamento o riserva di valore — "dove tieni i soldi" | Conto corrente, contanti, carta di credito |
| `income` | Categoria di entrate | Stipendio, rimborsi, proventi vari |
| `expense` | Categoria di spese | Affitto, alimentari, trasporti |
| `loan` | Crediti/debiti personali verso persone fisiche o entità non finanziarie | Prestiti a/da familiari, amici, anticipi |

**2. Obbligatorietà ed ereditarietà:**
- Obbligatoria sui conti root (`parent_id IS NULL`)
- I conti figli ereditano dal padre, non si specifica
- Una gerarchia ha sempre un solo `type` (i sotto-rami non possono cambiare tipo)

**3. Coerenza con il modello contabile esistente:**

| `accounts.type` | `account_type` (ADR-006) | `display_sign` (ADR-005) |
|-----------------|--------------------------|--------------------------|
| `portfolio` | `patrimonial` | `+1` |
| `loan` | `patrimonial` | `+1` |
| `income` | `economic` | `+1` |
| `expense` | `economic` | `-1` |

I tre campi sono coerenti per costruzione. Il sistema deriva `account_type` e `display_sign` da `accounts.type` alla creazione/modifica. L'utente vede e gestisce solo `type`.

**4. Modificabilità:**
Il `type` di un conto è modificabile anche con movimenti esistenti, ma il cambio aggiorna automaticamente `account_type` e `display_sign`. Operazione che ha senso solo in casi rari e per correzione errori. Il sistema permette l'operazione e ricalcola gli aggregati.

**5. Carte di credito → `type=portfolio`:**
Le carte di credito sono conti `portfolio` con saldo che diventa negativo quando si spende. L'addebito mensile è un giroconto da un altro `portfolio` (conto corrente) alla carta. Niente entità separata "carta di credito" — vedi ADR-006 sull'uso di `account_role: transit` per gestione tecnica eventuale.

**6. Mutui / finanziamenti bancari con piano di ammortamento:**
**Fuori scope v0.1** (vedi Sviluppi Futuri). Il modello attuale gestisce solo le rate come `expense`, eventualmente affiancate da un conto `portfolio` negativo "Debito mutuo" aggiornato manualmente dall'utente. La gestione completa (suddivisione capitale/interessi, piano di ammortamento, tasso variabile) è una feature dedicata futura.

---

**Flag `extraordinary`:**

```sql
accounts.extraordinary boolean default false
movements.extraordinary boolean nullable
```

**Comportamento:**
- Sul conto: indica che il conto traccia movimenti straordinari da escludere dalle statistiche di gestione corrente per default
- Sul movimento: se NULL eredita dal conto; se valorizzato esplicitamente (true/false) sovrascrive l'eredità per quella singola riga
- Le dashboard "default" filtrano `WHERE movements.extraordinary IS NOT TRUE` (considerando l'ereditarietà)
- L'utente può sempre chiedere statistiche "complete" (incluse extraordinary)

**Esempio d'uso:**
Conto `Spese / Manutenzione straordinaria casa` con `extraordinary=true`. Una manutenzione da 15.000€ (es. serramenti) finisce qui di default e non inquina la statistica "spese mensili medie". Se un singolo movimento minore (es. 200€) deve invece rientrare nelle statistiche correnti, l'utente lo marca `extraordinary=false` sul singolo movimento.

**Vincoli e indici:**
- Indice su `(scenario_id, type)` per query dashboard
- Indice su `(scenario_id, extraordinary)` se richiesto da analisi statistiche

**Assegnato a:** DB Architect per schema definitivo, vincoli, indici, migration.

---

### ADR-062 — Prestiti personali: modello unico per credito e debito
**Data:** 2026-05-05
**Stato:** ✅ Deciso

**Decisione:**
I crediti e debiti personali verso persone fisiche o entità non finanziarie (familiari, amici, colleghi) sono modellati come **conti `type=loan` dedicati per persona/entità**. Un unico conto per persona, indipendentemente dal fatto che ci siano crediti o debiti in essere — il segno del saldo determina la natura corrente del rapporto.

**Regola:**
- Saldo positivo del conto → la persona ti deve qualcosa (credito per te)
- Saldo negativo → tu devi qualcosa alla persona (debito per te)
- Saldo zero → siete pari
- Il saldo è dinamico: una stessa persona può oscillare tra credito e debito nel tempo

**Esempio:**
- Conto `Prestiti / Mario`, saldo iniziale 0
- Anticipi a Mario 15€ → saldo +15€ (Mario ti deve)
- Mario poi anticipa a te 20€ → saldo -5€ (tu devi a Mario)
- Gli paghi 5€ → saldo 0

Un solo conto, una sola storia, segno dinamico.

**Struttura nel piano dei conti:**

```
Prestiti (type=loan)
├── Mario Rossi
├── Anna Bianchi
├── Mamma
└── Papà
```

Il ramo `Prestiti` è incluso nel template predefinito (ADR-007 esteso) ma parte vuoto: i conti foglia per persona sono creati dall'utente man mano che le occorrenze si presentano.

**Template di registrazione dedicati:**

Per non richiedere all'utente conoscenza di partita doppia, sono previsti template editoriali (ADR-008) per i casi d'uso comuni:
- "Anticipo per qualcuno" → chiede totale, quota tua, persona; compila la registrazione
- "Restituzione credito" → chiede persona, importo, conto di destinazione
- "Prestito ricevuto da..." e "Restituzione prestito a..."
- "Nuova persona prestito" → aggiunge un conto foglia sotto Prestiti senza dover andare in Setup

Sono contenuto editoriale, non richiedono nuove entità DB.

**Cosa NON è in scope:**
- Crediti/debiti verso istituzioni finanziarie (mutui, prestiti bancari, leasing): Sviluppi Futuri
- Calcolo automatico di scadenze previste delle restituzioni
- Notifiche di sollecito o promemoria sui prestiti aperti

**Assegnato a:** DB Architect (vincoli del piano dei conti predefinito). Templating editoriale → contenuto.

---

### ADR-063 — `transaction_type` derivato automaticamente sulla registrazione
**Data:** 2026-05-05
**Stato:** ✅ Deciso

**Problema:**
Le statistiche di gestione (es. "spese del mese") devono distinguere transazioni di natura diversa anche quando muovono lo stesso conto. Esempio classico: una cena al ristorante per 30€ di cui 15€ sono di un amico è contabilmente una **spesa parziale + un prestito**, non una "spesa di 30€". La sola classificazione del conto (`accounts.type`) non basta perché non descrive la natura della transazione nel suo complesso.

**Decisione:**

Aggiunta colonna `registrations.transaction_type` derivata automaticamente dalla composizione dei movimenti della registrazione. Persistita per query veloci, non modificabile dall'utente.

**Schema:**
```sql
registrations.transaction_type enum(
  'expense','income','transfer','loan',
  'loan_restructure','mixed','opening_balance','other'
)
```

**Regole di derivazione (pattern-based):**

| Composizione movimenti (escluse contropartite tecniche) | `transaction_type` |
|---------------------------------------------------------|-------------------|
| 1 conto `portfolio` + 1 conto `expense` | `expense` |
| 1 conto `portfolio` + 1 conto `income` | `income` |
| 2 conti `portfolio` (segni opposti) | `transfer` |
| 1 conto `portfolio` + 1 conto `loan` | `loan` |
| 2 conti `loan` (es. consolidamento debiti tra persone) | `loan_restructure` |
| 1 conto `opening_balance` + N conti | `opening_balance` |
| Mix di 3+ conti di tipi diversi (es. cena con amico) | `mixed` |
| Altro / non classificabile | `other` |

**Esempio "cena con Mario":**
- Movimento 1: `Portafoglio/Carta` -30€
- Movimento 2: `Spese/Ristoranti` +15€
- Movimento 3: `Prestiti/Mario` +15€
- `transaction_type` derivato: `mixed`

**Quando si calcola:**
- Alla creazione della registrazione
- Alla modifica (se la composizione dei movimenti cambia)
- Persistito su `registrations.transaction_type`
- Non modificabile dall'utente: è valore derivato

**Uso operativo:**
- Statistiche granulari: "spese pure del mese" = `SUM movements ON registrations WHERE transaction_type='expense'`
- Filtri di ricerca per natura della transazione
- Coerenza garantita dal sistema, l'utente non può sbagliare classificazione

**Cosa è e cosa non è:**
- È un **valore derivato denormalizzato** — pattern standard per query veloci
- Non sostituisce `accounts.type` (la dimensione del conto) — è ortogonale
- Le statistiche complete combinano entrambe le dimensioni

**Attenzione al "secchio" `mixed`:**
Se nel tempo l'analisi rivela che molte registrazioni cadono in `mixed`, è segnale che servono pattern di derivazione più ricchi. Monitoraggio operativo previsto.

**Vincoli e indici:**
- Indice su `(scenario_id, transaction_type)` per dashboard
- Indice composito su `(scenario_id, date, transaction_type)` se richiesto da query temporali

**Assegnato a:** DB Architect (schema, indici), Backend Architect (logica di derivazione e ricalcolo su modifica registrazione).

---

## Sviluppi Futuri
*Idee valide, deliberatamente fuori scope per ora. Da rivalutare quando il core è stabile.*

- Notifiche create manualmente dall'utente (reminder personalizzati)
- Wizard di registrazione movimenti con template e preview in-platform (UX da progettare in sessione dedicata con Frontend + DB Architect)
- Anagrafica contatti clienti/fornitori collegata ai movimenti
- Multi-valuta per conto all'interno di uno scenario (valuta di reporting scenario + conversione, tabella exchange_rates) — ADR-034
- App mobile nativa (oggi PWA)
- Wizard obiettivi utente iniziale (impostazione obiettivi con scadenza al primo accesso, notifiche automatiche fino a completamento/ignore esplicito)
- Gestione completa di mutui e finanziamenti bancari con piano di ammortamento: suddivisione automatica capitale/interessi su ogni rata, gestione tasso variabile, import del piano di ammortamento da PDF banca, conto "Debito" che si riduce automaticamente in base alla quota capitale. In v0.1 le rate si registrano come `expense` semplice, eventualmente affiancate da un conto `portfolio` negativo aggiornato manualmente — ADR-061
- RBAC granulare sul pannello admin (oggi: `role = admin` → accesso completo). **Nota architetturale per Backend Architect:** i check di autorizzazione admin non devono essere hardcodati come `if role = admin → tutto permesso`, ma devono passare per un layer di permission sostituibile in futuro senza riscrittura. Oggi il layer ritorna sempre true per gli admin.

---

## Decisioni aperte

| # | Tema | Assegnato a |
|---|------|-------------|
| 1 | WebSocket: Reverb vs Soketi | Backend Architect |
| 2 | Lista eventi webhook con payload | Backend Architect |
| 3 | Retention policy audit log | DB Architect |
| 4 | Template di registrazione: schema completo | DB Architect |
| 5 | Spatie Laravel Data come layer DTO | Backend Architect |
| 6 | JSON:API: libreria Laravel da adottare | Backend Architect |
| 7 | Cloudflare come proxy layer | Security & Infra |
| 8 | Pricing definitivo (prezzi, nomi tier) — **ora include rivalutazione struttura tier dopo revoca BYOK** | Product & Comms (rimandata, da riprendere dopo consolidamento app) |
| ~~9~~ | ~~Nome definitivo~~ | ✅ Chiuso — MioTesoro (ADR-039) |
| 10 | Anagrafica contatti clienti/fornitori | Sviluppi Futuri |
| ~~11~~ | ~~Speech-to-text provider~~ | ✅ Chiuso — GPT-4o Mini Transcribe (ADR-047) |
| ~~12~~ | ~~Strategia auto-categorizzazione~~ | ✅ Chiuso — due livelli memoria + flag autosuggest (ADR-051, ADR-052) |
| ~~13~~ | ~~Generation horizon default per recurring_rules~~ | ✅ Chiuso — concetto non si applica più (ADR-028 revocata, ADR-060) |
| 14 | ~~Soglia orizzonte pianificato per trigger notifica ricorrenti~~ → **Ridefinita:** data apparizione notifica wizard annuale | ✅ Confermato 1 dicembre (ADR-060) — formalmente chiuso |
| 15 | Stack sito marketing: WordPress vs statico (Astro/Hugo) | Product, Brand & Comms |
| ~~16~~ | ~~Dominio definitivo~~ | ✅ Chiuso — miotesoro.it + miotesoro.app (ADR-039) |
| 17 | Canali social da attivare e profilo target primario per lancio | Product, Brand & Comms |
| 18 | Strategia di lancio: coming soon, lista d'attesa, beta chiusa | Product, Brand & Comms |
| 19 | Tool AI specifico per generazione logo (Midjourney, Ideogram, altro) | Product, Brand & Comms |
| ~~20~~ | ~~Stima costo per chiamata per capability A, B, C~~ | ✅ Chiuso — tabella costi (ADR-046) |
| ~~21~~ | ~~Selezione modello per capability~~ | ✅ Chiuso — Haiku 4.5 / Sonnet 4.6 default (ADR-046) |
| 22 | Limite movimenti piano Free — costi AI ora disponibili, da fissare in fase di scoping v0.1/v1 | Orchestratore |
| 23 | Cap mensile AI import massivo (capability B) — costi AI ora disponibili, da fissare in fase di scoping v0.1/v1 | Orchestratore |
| 24 | Pricing accesso MCP (tier power user/developer) | Product & Comms + Backend Architect |
| 25 | Provider email transazionale esterno per quando si scala (Postmark, Resend, SES) | Backend Architect |
| ~~26~~ | ~~Vincolo "solo Anthropic" applicabile a STT~~ | ✅ Chiuso — multi-provider adottato, vincolo non si applica (ADR-042 esteso, ADR-047) |
| 27 | Lunghezza ottimale `description_prefix` e lista prefissi bancari noti da strippare | AI & Integrations (validazione empirica pre-lancio) |
| 28 | Lista capability con UI di feedback esplicito (👍😐👎) — solo B/A o anche altre? | Frontend + AI & Integrations |
| 29 | Soglia `confirmed_count` per promuovere uno storico Livello 2 frequente a suggerimento di regola esplicita | AI & Integrations + UX |
| 30 | Struttura tier pricing dopo revoca BYOK (Pro così com'è / Pro con quota AI base / fusione Pro+AI) | Product & Comms (rimandata, da riprendere dopo consolidamento app) |
| 31 | Scala estesa palette (varianti tonali, dark mode, contrasti WCAG) + logo definitivo + tipografia di brand + iconografia | Product, Brand & Comms (sospeso) — Frontend userà scelte tecniche temporanee fino al ripristino |
| 32 | UX template dinamico per inserimento agevolato di movimenti seriali (es. 12 rate mutuo in fila) — copia da movimento esistente, form ripetitivo, ecc. | Frontend + DB Architect |

---

### ADR-034 — Valuta: a livello di scenario, monovaluta
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
Ogni scenario ha una valuta unica definita alla creazione. Tutti i conti e movimenti di quello scenario sono nella stessa valuta. Nessuna conversione, nessuna tabella tassi di cambio.

**Colonna da aggiungere:** `scenarios.currency` — codice ISO 4217 (`char(3)`), es. `EUR`, `USD`. Default `EUR` per il mercato italiano.

**Motivazione:**
Copre il 95%+ del target italiano. Aggiunge zero complessità al modello dati e alle query di cashflow. Chi ha conti esteri può aprire uno scenario separato nella valuta corrispondente.

**Sviluppo futuro:** supporto multi-valuta per conto — deliberatamente rimandato. Il modello dati attuale non lo preclude.

---

### ADR-035 — Sicurezza, fiducia e requisiti non negoziabili
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisioni tecniche:**
- Hosting esclusivamente su VPS Hetzner EU — dato europeo in Europa, GDPR nativo
- Encryption at rest sul database PostgreSQL
- HTTPS obbligatorio su tutti i domini, nessuna eccezione
- Nessuna cessione di dati utente a terze parti
- I dati inviati a Claude API non vengono usati per training — garantito contrattualmente da Anthropic
- End-to-end encryption lato client: **esclusa** — incompatibile con cashflow server-side, AI, report aggregati

**Principi AI — non negoziabili:**
- **AI è opt-in:** il software funziona completamente senza AI. Ogni funzione AI è una scelta esplicita dell'utente.
- **Zero training:** i dati inviati a Claude API non vengono usati per addestrare modelli AI.
- Entrambi i principi vanno comunicati in modo prominente — non nelle FAQ, non nel footer.

**Requisito UX non negoziabile — responsive:**
La PWA deve funzionare perfettamente su smartphone, tablet e desktop. Requisito di lancio, non miglioramento futuro.

**Assegnazioni:**
- Implementazione tecnica → Security & Infra
- Comunicazione trust e privacy policy → Product, Brand & Comms
- Responsive UI → Frontend

---

### ADR-036 — BYOK (Bring Your Own Key): solo chiavi Anthropic, fase iniziale
**Data:** 2026-05-01
**Stato:** ❌ **Revocata in Sessione 5 (2026-05-02)**

**Motivazione della revoca:**
La decisione di adottare un'architettura multi-provider configurabile (ADR-042 esteso, sessione 5) rende il BYOK strutturalmente incompatibile con la piattaforma. Se ogni capability può usare un modello di un provider diverso (Anthropic, OpenAI, eventualmente altri), una singola chiave Anthropic dell'utente non basta più, e richiedere all'utente di gestire N chiavi per N provider produrrebbe un'UX inaccettabile.

**Cosa sostituisce il BYOK come alternativa al piano AI a pagamento:**
- **MCP** — l'utente porta il suo AI client esterno, MioTesoro fa solo da infrastruttura dati (ADR-020)
- **No AI** — il prodotto funziona completamente senza AI, principio non negoziabile (ADR-035)

**Decisione originale (mantenuta per storico):**
L'utente avrebbe potuto inserire una propria API key Anthropic per usare le funzioni AI senza sottoscrivere un piano AI a pagamento. Il costo delle chiamate sarebbe andato sul suo account Anthropic.

**Implicazioni:**
- Nessuna implementazione BYOK in v1
- Schema `ai_usage_log` perde il valore `byok` dal campo `mode` (vedi ADR-045 esteso in Sessione 5)
- Il piano Pro perde "BYOK" come benefit — i tier sono da rivedere, decisione rimandata

---

### ADR-037 — Pannello amministrativo
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
Backend amministrativo separato dall'app utente. Accessibile solo a utenti con ruolo `admin`.

**Funzioni core:** gestione utenti, capability, subscriptions, metriche operative, BYOK, audit log globale.

**Impersonation:** l'admin può entrare nello scenario di un utente per supporto/debug. Ogni sessione loggata in `audit_log` con `action: impersonation_start/end`. Banner visibile durante l'impersonation. No azioni distruttive in impersonation.

**Stack:** Laravel Filament — candidato naturale. Decisione aperta assegnata a Backend Architect.

---

### ADR-038 — Ruoli di sistema: user vs admin
**Data:** 2026-05-01
**Stato:** ✅ Deciso

**Decisione:**
Colonna `role` su `users`: `user` | `admin`. Separata dai ruoli scenario (ADR-011).
Il ruolo `admin` non è assegnabile dall'app utente — solo da DB o da altro admin.
