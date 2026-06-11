# Progetti

Registro di tutti i progetti attivi. Ogni progetto ha la sua cartella in `projects/nomeprogetto/`.

---

## Convenzione progetti

Ogni nuovo progetto:
1. Ottiene una cartella di lavoro in `projects/nomeprogetto/`
2. Riceve una riga in questo file con nome e sintesi
3. Deve contenere obbligatoriamente questi file:
   - `CHANGELOG.md` — storico versioni e modifiche
   - `TODO.md` — attività in corso e backlog
   - `TECNICO.md` — architettura, stack, flussi tecnici
   - `SINTESI.md` — cos'è, cosa fa, come si usa (non tecnico)
   - `APPUNTI.md` — note operative, workaround, decisioni

### Quando creare un nuovo progetto

Crea un nuovo progetto solo quando:
- **Ambito distinto** dai progetti esistenti (non è una sotto-area di un progetto attivo)
- **Configurazione dedicata** necessaria (agent, prompt, tool specifici)
- **Ciclo di vita autonomo** (può essere sviluppato, testato, manutenuto separatamente)

**Non creare** un nuovo progetto se:
- È una feature/estensione di un progetto esistente (aggiungi in `TODO.md` del progetto)
- È un task temporaneo o one-off (usa `myJob` o progetto pertinente)
- Condivide >70% del contesto con un progetto esistente (estendi quello esistente)

---

## Progetti attivi

### miotesoro-sheet-agent (myMoney)
**Cartella:** `projects/miotesoro-sheet-agent/`
**Documentazione:** [[projects/miotesoro-sheet-agent/SINTESI|Sintesi]] | [[projects/miotesoro-sheet-agent/TECNICO|Tecnico]] | [[projects/miotesoro-sheet-agent/TODO|TODO]] | [[projects/miotesoro-sheet-agent/APPUNTI|Appunti]]
**Cos'è:** Copilot AI per la gestione finanziaria personale di Atti. Registra entrate e uscite su due fogli Google Sheets (PERSONALE e CASA) con validazione automatica, controllo duplicati e integrità partita doppia. L'agente categorizza i movimenti automaticamente e non registra nulla senza conferma o senza esito positivo del revisore.

---

### myOCcall
**Cartella:** `projects/myOCcall/`
**Documentazione:** [[projects/myOCcall/README|README]] | [[projects/myOCcall/SINTESI|Sintesi]] | [[projects/myOCcall/TECNICO|Tecnico]] | [[projects/myOCcall/TODO|TODO]]
**Cos'è:** Sistema per entrare automaticamente in videochiamate (Google Meet, Zoom, Teams) come partecipante silenzioso, catturare l'audio via PulseAudio null sink, trascriverlo con Whisper (OpenAI) e produrre un riassunto strutturato da inviare ad Atti via Telegram. Attualmente in sviluppo — infrastruttura audio completata, pipeline end-to-end da completare.

---

### myAgenda
**Cartella:** `projects/myAgenda/`
**Documentazione:** [[projects/myAgenda/README|README]]
**Cos'è:** Utility di schedulazione personale. Legge i calendari reali di Atti (file .ics da più fonti) e le sue preferenze personali (vincoli temporali, priorità, orari figli) e propone slot ottimali quando chiesto. Agente: `myagenda.agent.md`. Calendari e preferenze da completare con Atti.

---

### myJob
**Cartella:** `projects/myJob/`
**Specifiche:** [[projects/myJob/README|README]]
**Cos'è:** Progetto di gestione miei task lavorativi e non. Quindi quando si parta di TODO list generiche, Clienti, azioni legate alla famiglia, a lavori, o attività non meglio specificate tendenzialmente finiscono qui

---

### condominio-mazzini-3
**Cartella:** `projects/condominio-mazzini-3/`
**Documentazione:** [[projects/condominio-mazzini-3/SINTESI|Sintesi]] | [[projects/condominio-mazzini-3/TECNICO|Tecnico]] | [[projects/condominio-mazzini-3/TODO|TODO]] | [[projects/condominio-mazzini-3/APPUNTI|Appunti]]
**Cos'è:** Pipeline per i rendering cromatici del Condominio Mazzini 3: coda proposte, generazione immagini Gemini o fallback PIL, pubblicazione web e tracking dello stato dei rendering.

---

### archiviazione-ottica-documenti
**Cartella:** `projects/archiviazione-ottica-documenti/`
**Documentazione:** [[projects/archiviazione-ottica-documenti/SINTESI|Sintesi]] | [[projects/archiviazione-ottica-documenti/TECNICO|Tecnico]] | [[projects/archiviazione-ottica-documenti/TODO|TODO]]
**Cos'è:** Sistema AI per archiviare documenti fisici (scansioni/foto di posta ordinaria). Riceve documenti da topic Telegram, AttiBot upload o cartella input/, analizza il contenuto via vision AI, propone nome e categoria, e — dopo conferma di Atti — copia su Google Drive nelle destinazioni corrette. Non cancella mai i file originali. Tiene un log in `history.md`.

---
