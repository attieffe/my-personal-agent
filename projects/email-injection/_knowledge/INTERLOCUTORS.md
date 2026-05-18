# INTERLOCUTORS — Mittenti Abituali

Questo file mantiene la memoria degli interlocutori abituali per facilitare il triage automatico delle email.

**Auto-aggiornamento**: Questo file viene aggiornato automaticamente (con conferma) quando Attilio conferma nuove categorizzazioni.

---

## Mittenti Interni (Gruppo Colzani)

### Attilio Fiumanò
- **Email**: attilio.fiumano@gruppocolzani.it
- **Ruolo**: IT Manager
- **Società**: GRUPPO COLZANI
- **Area pertinenza**: COLZANI (generale)
- **Argomenti tipici**: 
  - Coordinamento team IT (Alessandro, Fabio)
  - Assegnazione task e progetti
  - Comunicazioni con consulenti (Marco Di Stefano AS400)
  - Forward di email clienti/fornitori con istruzioni
- **Pattern comunicazione**: 
  - Spesso inoltra email con istruzioni esplicite nel corpo ("Segna nella mia TODO", "Mia todolist", ecc.)
  - Quando specifica "da discutere con Stefano" → escalation a CTO
- **File TODO associati**: `COLZANI/TEAM/README.md` (Mia todolist Atti/Attilio)
- **Note**: Le sue istruzioni hanno PRIORITÀ su qualsiasi altra informazione nell'email

### Alessandro
- **Email**: (da catalogare)
- **Ruolo**: Sviluppatore
- **Società**: SPORTIT SRL (principalmente)
- **Area pertinenza**: COLZANI/TEAM
- **Argomenti tipici**:
  - Shopify
  - Feed e-commerce (Lotrek)
  - InPost integrazione
  - Fatturazione elettronica
  - Tyre24
  - Weroad
  - Amazon API
- **File TODO associati**: `COLZANI/TEAM/ALessandro_TODO.md`
- **Note**: Developer tecnico, spesso coinvolto in progetti e-commerce

### Fabio
- **Email**: (da catalogare)
- **Ruolo**: Sistemista
- **Società**: GRUPPO COLZANI
- **Area pertinenza**: COLZANI/TEAM
- **Argomenti tipici**:
  - Infrastruttura
  - Hardware
  - Sistemi
  - APC/UPS
  - Barcode scanner
  - Hardware Shopify
- **File TODO associati**: `COLZANI/TEAM/README.md` (sezione Fabio)
- **Note**: Responsabile infrastruttura e sistemi

### Stefano Colzani
- **Email**: (da catalogare)
- **Ruolo**: CTO
- **Società**: GRUPPO COLZANI
- **Area pertinenza**: COLZANI (decisioni strategiche)
- **Argomenti tipici**:
  - Decisioni strategiche
  - Budget e canoni (es. Capgemini NAV-Ls)
  - Approvazioni progetti importanti
- **File TODO associati**: Menzioni in task di Attilio quando serve escalation
- **Note**: Livello decisionale alto, coinvolto in decisioni strategiche

### Marco Colzani
- **Email**: (da catalogare)
- **Ruolo**: (da catalogare)
- **Società**: COLZANI SRL
- **Area pertinenza**: COLZANI
- **Argomenti tipici**:
  - Dashboard carichi magazzino
  - Progetti COLZANI SRL
- **File TODO associati**: `COLZANI/TEAM/README.md` (progetto dashboard con Marco Colzani)
- **Note**: Coinvolto in progetti operativi COLZANI SRL

---

## Consulenti Esterni

### Marco Di Stefano
- **Email**: (da catalogare)
- **Ruolo**: Consulente AS400
- **Società**: Consulente esterno
- **Area pertinenza**: COLZANI/CONSULENTI/AS400
- **Argomenti tipici**:
  - AS400
  - Sistema legacy
  - Manutenzioni e sviluppi AS400
- **File TODO associati**: `COLZANI/CONSULENTI/README.md`, `COLZANI/AS400/`
- **Note**: Consulente specializzato su piattaforma AS400

---

## Fornitori / Partner

### Lotrek
- **Email/Dominio**: (da catalogare)
- **Tipo**: Partner tecnologico
- **Società cliente**: SPORTIT SRL
- **Area pertinenza**: COLZANI (SPORTIT)
- **Argomenti tipici**:
  - Feed e-commerce
  - Integrazioni Meta
  - Segnalazioni anomalie ordini
- **File TODO associati**: Task Alessandro
- **Note**: Partner per feed e-commerce e advertising

### Capgemini
- **Email/Dominio**: (da catalogare)
- **Tipo**: Fornitore software/licenze
- **Società cliente**: GRUPPO COLZANI
- **Area pertinenza**: COLZANI
- **Argomenti tipici**:
  - Canoni NAV-Ls retail
  - Ticket (OP# xxxxx)
  - Rinnovi licenze
- **File TODO associati**: Task Attilio
- **Note**: Sistema ticketing identificato da "OP#" + numero

---

## Domini da Monitorare

- `@gruppocolzani.it` → COLZANI (verificare società specifica e mittente)
- (altri domini verranno aggiunti quando emergono pattern)

---

## Pattern di Matching

### Istruzioni Esplicite (da Attilio)
- "Segna nella mia TODO" → task per Attilio
- "Mia todolist" → task per Attilio
- "da discutere con [NOME]" → task con flag escalation/discussione
- "Assegnato a [NOME]" → task specifico per quella persona

### Keyword Tecniche
- "InPost" → probabile SPORTIT, task Alessandro
- "Shopify" → probabile SPORTIT, task Alessandro o Fabio
- "AS400" → consulente Marco Di Stefano
- "feed", "Lotrek" → SPORTIT, Alessandro
- "GCAT" + "ecommerce" → COLZANI SRL
- "OP#" + numero → ticket Capgemini

### Reference a Progetti Esistenti
- Nomi di progetti menzionati nel TODO vanno matchati con i task esistenti invece di crearne di nuovi

---

## Registro Modifiche

**2026-05-14**: Inizializzazione con mittenti noti da analisi email esistenti (UID 1-7) e struttura team COLZANI

---

## Note per il Sistema

Questo file viene consultato da `imap_check.py` per:
1. Identificare mittente e suo ruolo/contesto
2. Determinare area di pertinenza automatica
3. Identificare pattern e istruzioni esplicite
4. Proporre categorizzazione e azioni

Quando una email arriva da mittente non catalogato:
- Sistema propone aggiunta con richiesta conferma
- Dopo conferma di Attilio, `update_interlocutors.py` aggiorna questo file
