# Analisi Omonimie e Conflitti di Routing nel Workspace

**Data:** 2026-05-16
**Nota:** Generato da scansione automatica workspace.

---

## ALTO RISCHIO

### 1. TODO.md multipli in Colzani + miotesoro

**File coinvolti:**
- [`projects/myJob/COLZANI/TODO.md`](../COLZANI/TODO.md) — TODO Attilio su Colzani (master)
- [`projects/myJob/COLZANI/PROGETTI/dashboard_carichi_web/TODO.md`](../COLZANI/PROGETTI/dashboard_carichi_web/TODO.md)
- [`projects/myJob/COLZANI/PROGETTI/dev4side_adeguamento_sistemistico/TODO.md`](../COLZANI/PROGETTI/dev4side_adeguamento_sistemistico/TODO.md)
- [`projects/myJob/COLZANI/PROGETTI/kit_societa/TODO.md`](../COLZANI/PROGETTI/kit_societa/TODO.md)
- [`projects/miotesoro-sheet-agent/TODO.md`](../../miotesoro-sheet-agent/TODO.md)

**Problema:** Se si dice "aggiungi al TODO" senza specificare il progetto, l'AI può atterrare su qualsiasi di questi 5 file. Particolarmente pericoloso: i 3 TODO dei sottoprogetti Colzani sembrano TODO "di Colzani" ma sono specifici per progetto.

**Raccomandazione:** Rinominare i TODO dei sottoprogetti in `TODO_dashboard_carichi.md`, `TODO_dev4side.md`, `TODO_kit_societa.md` OPPURE aggiungere un H1 inequivocabile in cima a ciascuno. Aggiungere questi file al ROUTING.md.

---

### 2. CONVENTIONS.md vs CONVENZIONI_NAMING.md — stesso posto, scopo sovrapposto

**File coinvolti:**
- [`projects/myJob/CONVENTIONS.md`](CONVENTIONS.md)
- [`projects/myJob/CONVENZIONI_NAMING.md`](CONVENZIONI_NAMING.md)

**Problema:** Due file di convenzioni nella stessa directory root di myJob. L'AI (e l'utente) non sa quale aggiornare quando si parla di "convenzioni". Uno sembra un subset dell'altro o uno è legacy.

**Raccomandazione:** Verificare i contenuti. Se uno è un subset, incorporarlo nell'altro e cancellare il duplicato. Se hanno scopi diversi, rendere inequivocabile il titolo (es. `CONVENZIONI_NAMING.md` → `CONVENZIONI_FILE_E_CARTELLE.md`).

---

### 3. vendor-mapping.md duplicato in miotesoro

**File coinvolti:**
- [`projects/miotesoro-sheet-agent/docs/vendor-mapping.md`](../../miotesoro-sheet-agent/docs/vendor-mapping.md)
- [`projects/miotesoro-sheet-agent/memory/repo/vendor-mapping.md`](../../miotesoro-sheet-agent/memory/repo/vendor-mapping.md)

**Problema:** Due file con nome identico in miotesoro. Quale è la fonte di verità? L'AI può scrivere in quello sbagliato. Rischio: aggiornamenti divergenti.

**Raccomandazione:** Verificare se sono identici o diversi. Uno dei due dovrebbe diventare la fonte canonica; l'altro va cancellato oppure reso esplicitamente un derivato/cache.

---

### 4. CHANGELOG.md duplicato in miotesoro

**File coinvolti:**
- [`projects/miotesoro-sheet-agent/CHANGELOG.md`](../../miotesoro-sheet-agent/CHANGELOG.md)
- [`projects/miotesoro-sheet-agent/docs/CHANGELOG.md`](../../miotesoro-sheet-agent/docs/CHANGELOG.md)

**Problema:** Due CHANGELOG nello stesso progetto. Quale aggiornare? Rischio di versioni divergenti della storia delle modifiche.

**Raccomandazione:** Uno solo dovrebbe sopravvivere. Il root-level è lo standard; il CHANGELOG in `docs/` va eliminato o rinominato (es. `CHANGELOG_LEGACY.md`).

---

## RISCHIO MEDIO

### 5. email-injection: template vs file attivi con nome identico

**Template (NON modificare):**
- [`projects/email-injection/_system/inbox_template/ROUTING_RULES.md`](../../email-injection/_system/inbox_template/ROUTING_RULES.md)
- [`projects/email-injection/_system/inbox_template/TRIAGE_RULES.md`](../../email-injection/_system/inbox_template/TRIAGE_RULES.md)
- [`projects/email-injection/_system/inbox_template/inbox.config.md`](../../email-injection/_system/inbox_template/inbox.config.md)
- [`projects/email-injection/_system/inbox_template/email_threads.md`](../../email-injection/_system/inbox_template/email_threads.md)

**File attivi (usare questi):**
- [`projects/email-injection/inboxes/myjob/ROUTING_RULES.md`](../../email-injection/inboxes/myjob/ROUTING_RULES.md)
- [`projects/email-injection/inboxes/myjob/TRIAGE_RULES.md`](../../email-injection/inboxes/myjob/TRIAGE_RULES.md)
- [`projects/email-injection/inboxes/myjob/inbox.config.md`](../../email-injection/inboxes/myjob/inbox.config.md)
- [`projects/email-injection/inboxes/myjob/email_threads.md`](../../email-injection/inboxes/myjob/email_threads.md)

**Problema:** 4 coppie di file con nomi identici in `_system/inbox_template/` (template) vs `inboxes/myjob/` (attivi). Se si modifica il template pensando di modificare il file attivo, si rompe il meccanismo di creazione nuove inbox.

**Raccomandazione:** Aggiungere frontmatter o H1 esplicito nei template del tipo `# [TEMPLATE - NON MODIFICARE DIRETTAMENTE]`. Le directory sono già ben separate, ma aggiungere un warning testuale nel README.md del template rafforza la protezione.

---

### 6. myOCcall: dati di sessione in `_system/data/` vs `data/`

**File in location anomala:**
- [`projects/myOCcall/_system/data/20260516 0908 teams/META.md`](../../myOCcall/_system/data/20260516%200908%20teams/META.md)
- [`projects/myOCcall/_system/data/20260516 0921 teams/META.md`](../../myOCcall/_system/data/20260516%200921%20teams/META.md)

**File nella location canonica:**
- [`projects/myOCcall/data/`](../../myOCcall/data/) — sessioni con `META.md` e `SINTESI.md`

**Problema:** Due sessioni di call sono finite in `_system/data/` invece che in `data/`. Potrebbero essere dati reali finiti nel posto sbagliato durante un test, o una feature intenzionale. Se sono dati reali di call, non vengono trovati dai flussi normali.

**Raccomandazione:** Verificare se le due sessioni in `_system/data/` sono dati reali o test. Se reali, spostarli in `data/` (path canonica). Se test, aggiungere un `README.md` nella cartella `_system/data/` che spieghi lo scopo.

---

### 7. INDEX.md vs 00_index.md — naming convention incoerente

**File con `INDEX.md` (uppercase, senza numero):**
- [`projects/myJob/PERSONALE/lavori_a_casa/idee_progetti/INDEX.md`](../PERSONALE/lavori_a_casa/idee_progetti/INDEX.md)

**File con `00_index.md` (lowercase, prefisso numerico) — esempi:**
- [`projects/myJob/COLZANI/PROGETTI/kit_societa/00_index.md`](../COLZANI/PROGETTI/kit_societa/00_index.md)
- `projects/myJob/FREELANCE/DIRETTI/*/00_index.md` (molti)
- [`projects/myJob/INGENIO_SOLUTION/00_index.md`](../INGENIO_SOLUTION/00_index.md)
- [`projects/myJob/PERSONALE/00_index.md`](../PERSONALE/00_index.md)
- [`projects/myJob/PERSONALE/istruzione/00_index.md`](../PERSONALE/istruzione/00_index.md)

**Problema:** Quando si dice "apri l'indice di idee_progetti" l'AI potrebbe cercare `00_index.md` e non trovarlo, o viceversa.

**Raccomandazione:** Rinominare `INDEX.md` in `00_index.md` per uniformità con il resto del workspace.

---

### 8. README.md usato come TODO/backlog nei clienti FREELANCE

**File coinvolti:**
- [`projects/myJob/FREELANCE/DIRETTI/Ballabio_Cucine/README.md`](../FREELANCE/DIRETTI/Ballabio_Cucine/README.md)
- [`projects/myJob/FREELANCE/DIRETTI/Croce_Bianca_Genovese/README.md`](../FREELANCE/DIRETTI/Croce_Bianca_Genovese/README.md)
- [`projects/myJob/FREELANCE/DIRETTI/Davide_Rizzi/README.md`](../FREELANCE/DIRETTI/Davide_Rizzi/README.md)
- [`projects/myJob/FREELANCE/DIRETTI/Silvia_Migliaccio/README.md`](../FREELANCE/DIRETTI/Silvia_Migliaccio/README.md)
- [`projects/myJob/FREELANCE/DIRETTI/Studio_Legale_Condello/README.md`](../FREELANCE/DIRETTI/Studio_Legale_Condello/README.md)
- [`projects/myJob/FREELANCE/DIRETTI/Studio_Paladini/README.md`](../FREELANCE/DIRETTI/Studio_Paladini/README.md)
- [`projects/myJob/FREELANCE/DIRETTI/Unioncucine/README.md`](../FREELANCE/DIRETTI/Unioncucine/README.md)
- `projects/myJob/FREELANCE/SINAPPS/PROGETTI/*/README.md`
- [`projects/myJob/FREELANCE/GET_ME_DIGITAL/PROGETTI/PROJ-GetMeDigital-ceam-20260513/README.md`](../FREELANCE/GET_ME_DIGITAL/PROGETTI/PROJ-GetMeDigital-ceam-20260513/README.md)

**Problema:** Il README.md di ogni cliente viene usato anche come backlog/TODO. Non è ovvio per l'AI (né per l'utente) che il README contiene task. Se si dice "aggiungi task per Ballabio Cucine" l'AI deve sapere che va nel README, non in un TODO.md dedicato.

**Raccomandazione:** Aggiungere in ROUTING.md la regola esplicita: "per task su cliente FREELANCE DIRETTO o progetto SINAPPS/GMD → README.md del cliente/progetto". Oppure creare TODO.md separati nei clienti dove la lista task diventa lunga.

---

## BASSO RISCHIO (strutturali, non critici)

### 9. APPUNTI.md in due progetti distinti

**File coinvolti:**
- [`projects/miotesoro-sheet-agent/APPUNTI.md`](../../miotesoro-sheet-agent/APPUNTI.md)
- [`projects/myOCcall/APPUNTI.md`](../../myOCcall/APPUNTI.md)

**Problema:** Rischio basso perché i due progetti sono chiaramente separati per directory. Ma se si dice "nota in appunti" senza contesto di progetto, l'AI deve inferire quale dei due.

**Raccomandazione:** Assicurarsi che il contesto di progetto sia sempre esplicitato nelle istruzioni all'AI quando si vuole annotare qualcosa.

---

### 10. SINTESI.md in myOCcall in tre posti

**File coinvolti:**
- [`projects/myOCcall/_system/SINTESI.md`](../../myOCcall/_system/SINTESI.md) — documentazione di sistema
- `projects/myOCcall/data/<data-sessione>/SINTESI.md` — output di sessione singola (più file)
- [`projects/miotesoro-sheet-agent/SINTESI.md`](../../miotesoro-sheet-agent/SINTESI.md) — documentazione progetto

**Problema:** Rischio basso perché le SINTESI di sessione sono in directory con nome data univoca. Ma il `_system/SINTESI.md` potrebbe essere confuso con quello di miotesoro in un contesto ambiguo.

**Raccomandazione:** Nessuna azione urgente. Eventualmente rinominare `_system/SINTESI.md` in `_system/SINTESI_SISTEMA.md` per differenziarlo.

---

### 11. META.md in due location in myOCcall

**File coinvolti:**
- `projects/myOCcall/_system/data/*/META.md` — vedi punto 6
- `projects/myOCcall/data/*/META.md`

**Problema:** Pattern già coperto dal punto 6. Vale menzionare separatamente: il `META.md` è un file ricorrente nelle sessioni di call, e la sua presenza in `_system/data/` è anomala per le stesse ragioni.

**Raccomandazione:** Risolvere insieme al punto 6 (spostare le sessioni nella path canonica o documentare l'eccezione).

---

## Riepilogo Azioni Raccomandate

Checklist ordinata per priorità:

**Priorità ALTA**

- [ ] **[1]** Rinominare i TODO dei sottoprogetti Colzani (`TODO_dashboard_carichi.md`, `TODO_dev4side.md`, `TODO_kit_societa.md`) OPPURE aggiungere H1 inequivocabile in cima a ciascuno; aggiornare ROUTING.md
- [ ] **[2]** Confrontare `CONVENTIONS.md` e `CONVENZIONI_NAMING.md`; unificare o rinominare per chiarire lo scopo distinto
- [ ] **[3]** Verificare `vendor-mapping.md` in miotesoro (`docs/` vs `memory/repo/`): stabilire la fonte canonica ed eliminare o marcare il duplicato
- [ ] **[4]** Verificare `CHANGELOG.md` in miotesoro (`root` vs `docs/`): tenere solo quello root-level; rinominare o eliminare `docs/CHANGELOG.md`

**Priorità MEDIA**

- [ ] **[5]** Aggiungere header `# [TEMPLATE - NON MODIFICARE DIRETTAMENTE]` ai file in `email-injection/_system/inbox_template/`; aggiungere warning nel README del template
- [ ] **[6]** Verificare le sessioni in `myOCcall/_system/data/` (20260516 0908, 20260516 0921): se dati reali, spostarli in `myOCcall/data/`; se test, aggiungere README esplicativo
- [ ] **[7]** Rinominare `PERSONALE/lavori_a_casa/idee_progetti/INDEX.md` → `00_index.md`
- [ ] **[8]** Aggiungere in `ROUTING.md` la regola: "task su cliente FREELANCE DIRETTO o progetto SINAPPS/GMD → README.md del cliente/progetto"

**Priorità BASSA**

- [ ] **[9]** Nessuna azione urgente per `APPUNTI.md`; assicurarsi che il contesto progetto sia sempre esplicitato
- [ ] **[10]** Valutare rinomina `myOCcall/_system/SINTESI.md` → `SINTESI_SISTEMA.md`
- [ ] **[11]** Risolto insieme al punto 6

---

*Questo file può essere archiviato dopo che tutte le azioni sono state completate.*
