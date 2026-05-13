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

---

## Progetti attivi

### miotesoro (myMoney)
**Cartella:** `projects/miotesoro/`
**Cos'è:** Copilot AI per la gestione finanziaria personale di Atti. Registra entrate e uscite su due fogli Google Sheets (PERSONALE e CASA) con validazione automatica, controllo duplicati e integrità partita doppia. L'agente categorizza i movimenti automaticamente e non registra nulla senza conferma o senza esito positivo del revisore.

---

### myOCcall
**Cartella:** `projects/myOCcall/`
**Cos'è:** Sistema per entrare automaticamente in videochiamate (Google Meet, Zoom, Teams) come partecipante silenzioso, catturare l'audio via PulseAudio null sink, trascriverlo con Whisper (OpenAI) e produrre un riassunto strutturato da inviare ad Atti via Telegram. Attualmente in sviluppo — infrastruttura audio completata, pipeline end-to-end da completare.

---

### myJob
**Cartella:** `projects/myJob/`
**Cos'è:** Progetto di gestione miei task lavorativi e non. Quindi quando si parta di TODO list generiche, Clienti, azioni legate alla famiglia, a lavori, o attività non meglio specificate tendenzialmente finiscono qui

---
