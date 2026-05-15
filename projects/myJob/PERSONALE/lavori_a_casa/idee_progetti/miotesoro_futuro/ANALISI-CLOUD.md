# ANALISI-CLOUD.md — DECISIONS.md vs `mio-tesoro-cloud`

Analisi di applicabilità di tutti gli ADR del DECISIONS.md (redatto per variante `mio-tesoro-paas`)
rispetto alla variante **`mio-tesoro-cloud`** (DB in proprietà del cliente: Turso / Supabase / PocketBase / SQLite su cloud).

**Data analisi:** 2026-05-15
**Revisione:** 2026-05-15 — corretta assunzione architetturale di base

---

## Premessa architetturale

`mio-tesoro-cloud` si distingue da `mio-tesoro-paas` per **dove sta il dato**, non per l'assenza di un server:

| Variante | Server applicativo | DB dati |
|---|---|---|
| `mio-tesoro-paas` | ✅ nostro | ✅ nostro |
| `mio-tesoro-cloud` | ✅ nostro | **dell'utente** |
| `mio-tesoro-file` | ❌ no server | file locale/cloud |

> **Il server c'è, fa tutto quello che fa in PaaS — logica, AI, webhook, WebSocket —
> ma non ospita il DB dati: accede a quello dell'utente con le credenziali delegate.**

L'utente crea il proprio DB (Supabase, Turso, PocketBase, SQLite su cloud),
fornisce le credenziali di accesso al server MioTesoro durante il setup,
e da quel momento il server opera su quel DB esattamente come farebbe sul suo.

Per l'AI: l'utente fornisce la propria API key (BYOK locale nel setup).
Il server la usa per le chiamate — zero costo infrastrutturale AI per il prodotto.

**Conseguenza:** quasi tutto il DECISIONS.md rimane applicabile.
Le differenze sono molto più sottili di quanto sembri a prima vista.

---

## ✅ Applicabile direttamente (zero o minime modifiche)

### Modello dati core — invariato al 100%

Indipendente da chi ospita il DB.

| ADR | Titolo |
|-----|--------|
| ADR-001 | Partita doppia nativa |
| ADR-002 | Struttura tabelle: registrations + movements |
| ADR-003 | Stati del movimento (eseguito / previsto / annullato) |
| ADR-004 | `movements.amount` con segno algebrico diretto |
| ADR-005 | `display_sign` su accounts |
| ADR-006 | Piano dei conti gerarchico (self-referential, 3 livelli, `accounts.type`, `extraordinary`) |
| ADR-007 | Piano dei conti: origini multiple |
| ADR-008 | Template di registrazione: editoriali + utente |
| ADR-010 | Scenari: tipo e cardinalità |
| ADR-012 | Budget: entità separata |
| ADR-013 | Onboarding wizard obbligatorio |
| ADR-015 | ULID come chiave primaria |
| ADR-016 | Soft delete selettivo |
| ADR-026 | Classificazione conti: scheduled vs variable |
| ADR-027 | Cashflow simulato (orizzonte 12 mesi, view calcolata) |
| ADR-034 | Valuta monoscenario (ISO 4217) |
| ADR-050 | `ai_merchant_preferences` |
| ADR-051 | Due livelli di memoria AI |
| ADR-052 | Flag `ai_autosuggest` a livello scenario |
| ADR-053 | Lifecycle delle preferenze merchant |
| ADR-054 | Indicizzazione descrizioni: prefix + semantic_tags |
| ADR-055 | Tracciamento granulare proposte AI |
| ADR-056 | Vocabolario tag come entità gestita |
| ADR-060 | Movimenti pluriennali: `repeat_until_year` + wizard annuale |
| ADR-061 | `accounts.type` semantico + flag `extraordinary` |
| ADR-062 | Prestiti personali: conti `loan` per persona, segno dinamico |
| ADR-063 | `transaction_type` derivato automaticamente |

### Feature prodotto e AI — invariate

| ADR | Titolo |
|-----|--------|
| ADR-029 | AI capabilities: tre funzioni distinte (A/B/C) |
| ADR-046 | Modelli AI default per capability (Haiku / Sonnet) |
| ADR-047 | Speech-to-Text: GPT-4o Mini Transcribe |
| ADR-048 | Pipeline import: chunking + routing + schema |
| ADR-049 | Validazione automatica del parser generato |
| ADR-058 | Layer di astrazione provider AI |

**Nota su ADR-041 (modalità accesso AI):** le modalità diventano **BYOK** (utente fornisce
la propria chiave nel setup, il server la usa) e **MCP** (utente usa il suo AI client).
La modalità "Platform AI" (chiavi della piattaforma, subscription AI) non si applica —
o diventa un add-on opzionale se si vuole offrire chiavi gestite per chi non vuole il BYOK.

### Infrastruttura e workflow — applicabili

| ADR | Titolo |
|-----|--------|
| ADR-017 | API versioning `/api/v1/` |
| ADR-018 | Formato response JSON:API spec |
| ADR-019 | Webhook + WebSocket event-driven |
| ADR-022 | Branch strategy: dev + main |
| ADR-023 | Deploy workflow: GitHub Actions + SSH |
| ADR-024 | Docker Compose su VPS Hetzner (server applicativo, non DB) |
| ADR-030 | Sistema notifiche task/info in-app |

**Nota su ADR-019 (webhook/WebSocket):** il server ha accesso al DB dell'utente →
può rilevare eventi, generare notifiche, fare push via WebSocket esattamente come in PaaS.
Per Supabase il Realtime built-in è un'alternativa naturale al WebSocket custom.

**Nota su ADR-024 (Docker Compose):** il Docker Compose ospita il server applicativo
(backend Laravel + frontend), non il DB. Il DB è fuori dal Compose, nell'account dell'utente.

### Brand, marketing, sviluppo

| ADR | Titolo |
|-----|--------|
| ADR-025 | Architettura multi-agente (per sviluppo prodotto) |
| ADR-032 | Architettura web: sito marketing + app separati |
| ADR-033 | Brand identity da costruire da zero |
| ADR-039 | Nome MioTesoro + domini miotesoro.it / miotesoro.app |
| ADR-059 | Palette colori operativa (viola #3D3B8E + oro #F5C842) |

---

## ⚠️ Applicabile con adattamenti

### ADR-009 — Sistema capability

**Problema:** le capability sono verificate sul DB centrale. In `mio-tesoro-cloud` il DB
dati è dell'utente, ma il server può avere un **DB di metadati proprio** (minimale):
solo `user_id + subscription_status + db_credentials (cifrate) + capabilities`.
Nessun dato finanziario — solo metadati di gestione. La verifica delle capability funziona
esattamente come in PaaS.

**Adattamento richiesto:** separare esplicitamente il "DB metadati piattaforma"
(su server, gestito dal prodotto) dal "DB dati utente" (nell'account dell'utente).
Due database distinti per ruoli distinti.

---

### ADR-011 — Permessi scenario (viewer / editor)

Il server accede al DB dell'utente → può implementare il controllo viewer/editor
a livello applicativo esattamente come in PaaS.

**Differenza operativa:** l'auth degli utenti dello scenario family passa per
il sistema auth del provider DB (Supabase Auth) o per un sistema auth centralizzato
sul server (Laravel Sanctum/Passport come in PaaS).

**Soluzione più pulita con Supabase:** usare Supabase Auth + RLS come layer auth
nativo, e il server opera con il service role key sopra queste policy.

---

### ADR-014 — Audit log

Applicabile. Il log vive nel DB dell'utente — è solo suo, non visibile all'admin
di piattaforma per le operazioni sui dati. L'admin può avere un audit log separato
nel DB metadati per le operazioni di piattaforma (login, cambio subscription, ecc.).

---

### ADR-021 — Security layer

- Rate limiting → ✅ il server lo gestisce (non serve il DB utente)
- HMAC webhook → ✅ il server genera la firma
- Cloudflare proxy → ✅ davanti al server
- Encryption at rest → delegata al provider DB (Supabase e Turso lo fanno di default)
- API key management → ✅ gestione chiavi AI nel DB metadati (cifrate)

---

### ADR-035 — Sicurezza e requisiti non negoziabili

Principi invariati: AI opt-in, zero training, HTTPS, responsive PWA.

**Da ridefinire:** "hosting esclusivamente su VPS Hetzner EU" vale per il server applicativo
e il DB metadati. Per il DB dati dell'utente: la residenza dipende dal provider scelto
dall'utente. Comunicazione da adattare: "i tuoi dati finanziari restano nel tuo account
[Supabase/Turso], in una region EU se scegli quella".

---

### ADR-037 — Pannello amministrativo

**Applicabile parzialmente.** L'admin panel esiste sul DB metadati della piattaforma.

**Funzioni che rimangono:** gestione subscription utenti, capability, metriche di accesso,
audit operazioni piattaforma, impersonation (il server si connette al DB dell'utente
con le credenziali delegate per debug/supporto).

**Funzione che cambia:** l'admin non vede i dati finanziari dell'utente nel suo pannello.
Per impersonation deve usare le credenziali del DB utente, con banner visibile — come da ADR-037,
ma con consapevolezza esplicita che "stai accedendo ai dati sul DB dell'utente".

---

### ADR-040-042 — Capability AI, modalità accesso, configurabilità runtime

**Applicabili con modifica sul modello BYOK:**
- Il "piano AI" diventa: l'utente fornisce la propria API key nel setup (BYOK obbligatorio).
- La configurabilità runtime lato admin (modello AI per capability) rimane nel DB metadati.
- La modalità "Platform AI" (chiavi nostre, subscription AI) è opzionale — può essere
  aggiunta come add-on per chi non vuole gestire la propria chiave.

**ADR-042 (configurabilità runtime):** invariato nel DB metadati.

---

### ADR-043 — Struttura tier pricing

**Da rivedere, non da scartare.** La struttura Free/Pro/AI ha senso ancora,
ma il significato dei tier cambia:

- **Free:** DB tuo, funzionalità core, nessuna AI
- **Pro:** DB tuo, funzionalità avanzate (scenari multipli, family), nessuna AI
- **AI:** DB tuo, + AI capabilities (richiede tua API key, oppure add-on chiavi gestite)

Il vantaggio per il prodotto: nessun costo di storage → margini migliori rispetto a PaaS
a parità di prezzo listino.

---

### ADR-044 — Email transazionale

✅ Applicabile — il server ha un DB metadati con gli indirizzi email degli utenti.
Le email (benvenuto, trial in scadenza, ecc.) vengono generate dal server
esattamente come in PaaS.

---

### ADR-045 / ADR-057 — AI usage log + tabella prezzi modelli

✅ `ai_usage_log` vive nel DB utente (traccia i suoi consumi, utile per lui).
✅ `ai_model_pricing` può vivere nel DB metadati piattaforma (configurata dall'admin).
Il calcolo del costo stimato avviene nel server come da ADR-045/057.

---

## ❌ Non applicabile

| ADR | Motivo |
|-----|--------|
| ADR-028 — recurring_rules (revocata) | Già revocata nel DECISIONS.md originale |
| ADR-036 — BYOK Anthropic (revocata) | Già revocata. Ma il concetto BYOK **ritorna** in `mio-tesoro-cloud` come modello nativo, non come eccezione |
| ADR-038 — Ruoli user/admin (parzialmente) | Il ruolo `admin` esiste nel DB metadati piattaforma, ma non nel DB dati utente. Schema da adattare: due contesti separati |

---

## 🆕 Nuove decisioni richieste per `mio-tesoro-cloud`

### NC-001 — Scelta del provider DB supportati

Quali provider supportare (e in quale ordine di priorità)?

| Provider | Multi-utente | Auth nativa | Query SQL | Setup utente | Costo |
|----------|-------------|-------------|-----------|--------------|-------|
| **Supabase** | ✅ RLS + Auth | ✅ Google/Apple | ✅ PostgreSQL | Medio | Gratis (generoso) |
| **Turso** | ❌ solo token | ❌ | ✅ SQLite | Basso | Gratis (generoso) |
| **PocketBase** | ✅ self-hosted | ✅ | ✅ SQLite | Alto (VPS) | ~5€/mese VPS |
| **SQLite su cloud** | ❌ | ❌ | ✅ in-browser | Bassissimo | Gratis |

**Raccomandazione da valutare:** Supabase come provider primario (supporta tutti i casi d'uso
incluso family), Turso come secondario (single-user, zero friczione). Gli altri fuori scope v1.

---

### NC-002 — Modello di autenticazione

Il server ha bisogno di autenticare gli utenti per sapere a quale DB connettersi.

**Opzione A — Auth server-side classica (Laravel Sanctum)**
Il server gestisce username/password/social login. Le credenziali del DB utente sono
salvate nel DB metadati, cifrate. Al login: il server recupera le credenziali DB dell'utente
e si connette. UX identica a PaaS per l'utente finale.

**Opzione B — Auth delegata al provider DB (es. Supabase Auth)**
Il JWT di Supabase è usato come token di sessione anche sul server MioTesoro.
Più elegante ma vincola l'autenticazione al provider DB scelto.

**Raccomandazione:** Opzione A — più flessibile, indipendente dal provider DB, UX identica a PaaS.

---

### NC-003 — DB metadati piattaforma vs DB dati utente

Definire esplicitamente i due DB:

**DB metadati (server, gestito dal prodotto):**
- `users` (id, email, password hash, created_at)
- `user_db_credentials` (user_id, provider, connection_url, key_encrypted)
- `user_ai_keys` (user_id, provider, key_encrypted)
- `user_capabilities` (come da ADR-009)
- `audit_log` (solo operazioni piattaforma)
- `ai_model_pricing` (come da ADR-057)

**DB dati (account utente, acceduto dal server con credenziali delegate):**
- Tutto il resto del schema del DECISIONS.md (registrations, movements, accounts, ecc.)
- `ai_usage_log` (traccia consumi AI dell'utente, utile a lui)
- `audit_log` (operazioni sui dati, solo sue)

---

### NC-004 — Schema migration su DB utente

Come si aggiorna lo schema quando esce una nuova versione dell'app?

**Opzione A — Migration automatica al primo avvio post-update**
Il server verifica la versione schema nel DB metadati e applica le migration necessarie
sul DB dell'utente al suo primo accesso dopo il deploy.

**Opzione B — Migration con conferma utente**
Il server notifica l'utente ("disponibile un aggiornamento schema") e lui conferma.
Più sicuro ma aggiunge friczione.

**Raccomandazione:** Opzione A per migration non distruttive (add column, add table);
Opzione B per migration potenzialmente distruttive (rename column, change type).

---

### NC-005 — Modello di pricing / monetizzazione

Struttura tier suggerita (da validare con ADR-043 aggiornato):

| | Free | Pro | AI |
|--|------|-----|----|
| Scenari | 1 | 2+ | 2+ |
| Utenti per scenario | 1 | 2+ | 2+ |
| Cashflow previsionale | ✅ | ✅ | ✅ |
| AI capabilities (BYOK) | ❌ | ❌ | ✅ |
| AI capabilities (chiavi gestite, add-on) | ❌ | ❌ | opzionale |
| Prezzo | Gratis | TBD | TBD |

Vantaggio strutturale vs PaaS: nessun costo storage → margini migliori.
Svantaggio: il BYOK crea un punto di attrito per il tier AI (l'utente deve avere una API key).

---

### NC-006 — Onboarding: riduzione friczione setup DB

Il punto di rottura principale. Soluzioni da valutare:

- **Wizard guidato con screenshot** step-by-step per Supabase
- **"Crea per me" via OAuth**: il prodotto crea il progetto Supabase a nome dell'utente
  tramite la Supabase Management API (richiede OAuth con Supabase)
- **Link deep diretto**: pulsante "Crea il tuo DB Supabase" → apre Supabase pre-configurato
- **SQLite su cloud come opzione zero-friction**: nessun account extra, usa Drive/Dropbox già in uso

---

## Riepilogo valutazione (rivisto)

| Categoria | % ADR applicabili | Note |
|-----------|------------------|------|
| Modello dati core | **100%** | Invariato |
| Funzionalità prodotto | **100%** | Invariato |
| AI capabilities | **90%** | BYOK sostituisce Platform AI; tutto il resto uguale |
| Infrastruttura server | **85%** | Docker, CI/CD, VPS: stesso server, DB diverso |
| Webhook / WebSocket / notifiche | **90%** | Server ha accesso al DB utente → funziona come PaaS |
| Gestione utenti / capability | **70%** | DB metadati separato dal DB dati; logica invariata |
| Admin panel | **60%** | Esiste, ma non vede i dati finanziari degli utenti |
| Pricing / subscription | **50%** | Struttura simile, valori da ridefinire, BYOK per AI |
| Brand / marketing | **100%** | Nessuna differenza |

**Investimento riutilizzabile stimato: ~85% del lavoro già fatto nel DECISIONS.md**

La differenza da `mio-tesoro-paas` è molto più sottile del previsto:
il server fa tutto, il DB dati è dell'utente, la logica è identica.
Le uniche aree di vera differenza sono l'onboarding tecnico, il BYOK per l'AI,
e la separazione DB metadati / DB dati.

---

_Documento creato il 2026-05-15 — revisione 2026-05-15_
