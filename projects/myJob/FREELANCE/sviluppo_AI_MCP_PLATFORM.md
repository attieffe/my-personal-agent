# SVILUPPO AI MCP PLATFORM

[[SVILUPPI_BUSINESS|← Torna a Sviluppi Business]]

## Stato
- **Stato:** ideazione / ricerca
- **Ultimo aggiornamento:** 2026-08-27
- **Priorità:** alta

---

## 💡 Concept

**Idea core:** Piattaforma per portare AI in azienda step-by-step tramite **MCP Knowledge Platform**

### Cosa offre
- **Second brain aziendale**: knowledge base interrogabile via AI
- **MCP-native**: integrabile con qualsiasi AI (Claude, GPT, altri) → no vendor lock-in
- **Ruoli e permessi**: basato su secret/API keys degli utenti
- **MCP in scrittura**: creare/aggiornare knowledge
- **MCP in lettura**: interrogare documentazione, procedure, know-how
- **Automazioni**: integrazione tra processi aziendali
- **Piattaforma rivendibile**: modello SaaS/white-label

### Target
PMI che vogliono adottare AI ma:
- Non sanno da dove iniziare
- Hanno paura della complessità
- Non vogliono vendor lock-in
- Cercano consulenza personalizzata, non videocorsi

---

## 🔍 Ricerca Mercato

### Claude Platform (Business)
**Riferimento:** [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview)

- **Claude Managed Agents** (beta 2026): agenti stateful, sessioni persistenti server-side
- **Claude Enterprise**: sicurezza avanzata, compliance, controlli admin
- **Agent SDK**: Files API, Skills API, Computer Use (browser automation)
- **Focus strategico:** "agent control plane" come vantaggio enterprise

### MCP Ecosystem
**Riferimento:** [MCP Ecosystem 2026](https://chatforest.com/guides/mcp-ecosystem-2026-state-of-the-standard/)

**Scoperta chiave:** MCP **non ha concorrenti diretti** per agent-to-tool protocol. È diventato lo **standard de facto**.

**Piattaforme complementari:**
- **Vertex AI Agent Builder** (Google): managed infrastructure + MCP integrato
- **Teradata Enterprise AgentStack**: piattaforma enterprise con Enterprise MCP component
- **Protocollo A2A**: agent-to-agent communication (orizzontale vs MCP verticale)

**Implicazione:** MCP è il protocollo vincente → puntare su MCP-native è strategicamente corretto.

---

## 🛠️ Stack Tecnologico

### Deployment Platform: Railway

**Riferimenti:**
- [Railway.com](https://railway.com)
- [Railway + Claude Code](https://railway.com/agents/claude)
- [Railway AI Docs](https://docs.railway.com/ai)

**Cos'è Railway:**
- **PaaS semplificato** per deployment cloud (simile a Heroku, Vercel, Render)
- Focus: "push code → app running" (astrae infrastruttura)
- **100M$ Series B (2026)**, 3M utenti, 100k signup/settimana
- Supporta DB managed (Postgres, MySQL, MongoDB, Redis)
- Scaling, monitoring, networking automatici

**Railway vs cloud provider:**
- **NON è** Azure/AWS/GCP (non vende IaaS raw)
- **È** deployment platform che usa cloud sotto (AWS, GCP, Metal)
- Target: developer/startup, semplicità vs controllo totale

**Railway + AI Agents:**
- **Integrazione nativa** Claude Code, Cursor, Codex
- Deploy automatico via AI agents
- [Railway Skills](https://agentskill.work/en/skills/railwayapp/railway-skills) per Claude Code

**Per questo progetto:**
- Railway = **infra/hosting** della piattaforma MCP
- NON competitor di Claude Platform (sono complementari)
- Stack: Railway (deploy) + MCP Platform (logica) + Claude/GPT (AI)

**Competitors Railway:**
- Heroku, Vercel, Render, Fly.io (NON Azure/AWS/GCP)

### Linguaggi di sviluppo

Railway è **language-agnostic** → supporta qualsiasi linguaggio via auto-detection o Docker.

**Opzione 1: TypeScript/Node.js** (consigliata per MVP)
- ✅ **SDK MCP ufficiale** Anthropic è in TypeScript
- ✅ Ecosistema ricco (Express, Fastify, tRPC)
- ✅ Veloce per prototipi
- ✅ Community MCP attiva
- ❌ Meno performante per ML pesante

**Opzione 2: Python** (ottima per AI-heavy)
- ✅ Eccellente per AI/ML (LangChain, embeddings, vector DB)
- ✅ FastAPI per API veloci
- ✅ Integrazioni AI mature
- ❌ MCP SDK Python meno maturo di TS

**Opzione 3: Stack misto** (consigliata per scalabilità)
- **Backend MCP server:** TypeScript (MCP native)
- **AI processing:** Python microservizi (embedding, ML)
- **Database:** Postgres (vector search con pgvector)
- Railway supporta multi-servizi nello stesso progetto

**Suggerimento stack iniziale:**
```
- Frontend: TypeScript/React (landing + dashboard)
- Backend MCP: TypeScript (MCP server/client)
- AI processing: Python/FastAPI (embedding, search)
- Database: Railway Postgres + pgvector
- Deploy: Railway (auto-deploy da GitHub)
```

---

## 🎯 Posizionamento Unico

### Asset differenzianti

#### 1. "So quando l'AI NON serve"
- Mercato pieno di venditori che spingono AI a prescindere
- Messaggio: "evitala quando non serve" = credibilità istantanea
- Cliente capisce: "questo non mi vende fumo"

#### 2. Background tecnico ingegneristico
- Competenza reale su cosa c'è sotto il cofano
- Non un reseller che impacchetta API altrui
- Parlo la lingua di CTO e responsabili IT

#### 3. Clienti reali, non videocorsi
- Esperienza hands-on, problemi veri
- Non scalabilità a tutti i costi = qualità garantita
- "Non accetto clienti delusi" = standard alto

#### 4. Relazione consulenziale personalizzata
- Consulenza customizzata sui requisiti reali
- Approccio "pull" (strategia + tecnica) vs "push" (vendita progetti)
- Presa per mano del cliente step-by-step

---

## 💬 Messaging & Comunicazione

### Tagline (opzioni)
1. "AI in azienda senza fumo: ti dico quando serve e quando evitarla"
2. "Ingegnere informatico che porta AI dove serve davvero"
3. "Consulenza AI hands-on: strategia, implementazione, risultati"

### Messaggio chiave
> "Non vendo videocorsi. Porto l'AI nella tua azienda step-by-step, con consulenza personalizzata basata sui tuoi requisiti reali. E ti dico chiaramente quando l'AI non è la soluzione giusta."

### Value proposition
- **Problema:** Knowledge silos aziendali, paura AI, complessità percepita
- **Soluzione:** MCP Knowledge Platform + consulenza personalizzata
- **Beneficio:** Second brain interrogabile, no vendor lock-in, automazioni pronte
- **Differenza:** Ingegnere vero, non venditore; consulenza, non corso

---

## 📄 Landing Page Strategy

### Obiettivo
**Lead generation + validazione interesse** (non subito vendita)

### Focus messaggi
1. **Step-by-step onboarding AI** → ridurre paura/complessità
2. **MCP come vantaggio** → no vendor lock-in, funziona con qualsiasi AI
3. **Use cases concreti** → procedure, documentazione, knowledge interrogabile
4. **Automazioni già pronte** → integrazione processi esistenti

### Struttura proposta
- **Hero:** tagline + CTA "Scopri come portare AI nella tua azienda"
- **Problema:** knowledge silos, AI incomprensibile, paura vendor lock-in
- **Soluzione:** MCP Platform + consulenza personalizzata
- **Differenziatori:** "So quando NON usare AI", ingegnere vero, clienti reali
- **Use cases:** 2-3 esempi concreti (es: interrogare procedure qualità, automazione report)
- **CTA:** "Richiedi analisi gratuita" o "Prenota chiamata strategica"

---

## 🔬 Approfondimenti da Fare

### Tecnici
- [ ] Approfondire Claude Managed Agents (beta access?)
- [ ] Studiare implementazione MCP server/client (TypeScript SDK)
- [ ] Testare Railway: creare account, deploy hello-world TypeScript
- [ ] Analizzare Vertex AI Agent Builder (Google) come benchmark
- [ ] Valutare protocollo A2A per agent-to-agent
- [ ] POC MCP server: TypeScript + Postgres + pgvector
- [ ] Testare Railway multi-service (TS backend + Python AI worker)
- [ ] Definire architettura permessi (ruoli + API keys)

### Business
- [ ] Identificare 3-5 use cases specifici per PMI
- [ ] Definire pricing model (consulenza + SaaS? white-label?)
- [ ] Preparare demo/POC rapida (esempio knowledge base + query MCP)
- [ ] Creare pitch deck (problema, soluzione, differenziatori, roadmap)

### Marketing
- [ ] Creare bozza landing page (wireframe o HTML semplice)
- [ ] Scrivere 3-4 post LinkedIn per testare messaging
- [ ] Identificare target audience specifico (settori PMI interessanti)
- [ ] Preparare lead magnet (es: "Guida: quando l'AI serve davvero nella tua azienda")

### Partnership
- [ ] Incontrare Alessio Rajo (feedback su incontro pendente)
- [ ] Capire dinamiche vendita progetti AI dal suo network
- [ ] Valutare possibile collaborazione (learn mode, poi eventuale split)

---

## 📚 Fonti & Riferimenti

### Documentazione tecnica
- [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview)
- [Claude Enterprise Plan](https://claude.com/solutions/enterprise)
- [The MCP Ecosystem in 2026](https://chatforest.com/guides/mcp-ecosystem-2026-state-of-the-standard/)
- [Railway Documentation](https://docs.railway.com)
- [Railway AI Docs](https://docs.railway.com/ai)
- [Railway + Claude Code](https://railway.com/agents/claude)

### Competitive analysis
- [MCP Alternatives & Competitors](https://www.merge.dev/blog/model-context-protocol-alternatives)
- [Top Cloud AI Platforms 2026](https://agent.nexus/blog/top-10-cloud-ai-platforms)
- [Railway vs Alternatives](https://northflank.com/blog/railway-alternatives)

### Deployment & Infrastructure
- [Railway Summer Update 2026](https://blog.railway.com/p/railway-summer-update-2026)
- [Railway Raises $100M Series B](https://www.axios.com/pro/enterprise-software-deals/2026/01/22/software-deployment-railway-100-million)
- [Railway Skills for Claude](https://agentskill.work/en/skills/railwayapp/railway-skills)

---

## 📝 Note & Decisioni

**2026-08-27** - Ideazione iniziale
- Identificato MCP come standard de facto (no concorrenti diretti)
- Definito posizionamento unico basato su competenza tecnica + consulenza personalizzata
- Tagline chiave: "So quando l'AI NON serve" come differenziatore forte
- Alessio Rajo identificato come partnership per imparare dinamiche vendita
