# Dev4Side — Adeguamento Sistemistico Domini Aziendali

## Riferimento offerta

| Campo | Valore |
|---|---|
| N. offerta | IT-D4S/1472 |
| Data | 30/04/2026 |
| Fornitore | Dev4Side Software S.r.l. |
| Referente Dev4Side | Miro Radenovic |
| Importo | 1.740,00 € + IVA |
| Modalità | 3 giornate Time & Material |
| Scadenza offerta | 30/05/2026 |
| Scadenza pagamento | 30 gg data fattura (all'accettazione) |

---

## Attività previste (da offerta)

### 1. Fix blocco join dominio — PRIMARIO ✅ COMPLETATO
Diagnosi e risoluzione del problema bloccante che impediva il join al dominio di qualsiasi macchina client o server sull'infrastruttura Active Directory basata su Windows Server 2012.

**Risolto:** Il DC si annunciava con un locator errato (`nav-dc` invece di `nav-dc.<suffisso>`). Aggiunto nome alternativo con suffisso di dominio e reso primario → i client ora risolvono correttamente i record SRV.
Report dettagliato in arrivo da Dev4Side.

### 2. Upgrade Domain Controller WS2012 → WS2025 — ⏳ DA FARE
Approccio **swing migration**:
1. Promozione di un nuovo DC (Windows Server 2025)
2. Trasferimento ruoli FSMO
3. Decommission dei DC esistenti (WS2012)

> Attività condizionata ai tempi residui delle 3 giornate T&M.

### 3. Assessment infrastruttura — 🔄 IN CORSO
Raccogliere le informazioni necessarie per definire una **roadmap di modernizzazione infrastrutturale**, oggetto di una proposta dedicata successiva all'intervento.

---

## Decisioni architetturali emerse (chat Teams)

### Entra ID — Strategia di integrazione
A seguito del fix AD, il consulente Dev4Side ha delineato il percorso per connettere il dominio AD a Entra ID (Microsoft 365):

**Opzione A — Hybrid Join** (consigliata se PC già joinati AD)
- Indolore per gli utenti, tutto via GPO in silenzio
- Richiede Entra Cloud Sync (supportato su WS2012) o Entra Connect (richiede WS2016+)

**Opzione B — Direct Entra ID Join**
- Richiede verifica che gli utenti abbiano autorizzazione al join delle macchine
- Potrebbe richiedere migrazione del profilo utente (tool già usato in precedenza dal consulente)

### Stato attuale delle identità
- Utenti AD e utenti cloud (Microsoft 365) sono **completamente scollegati**
- Credenziali AD e credenziali cloud sono **diverse**
- Durante il sync, le credenziali cloud verranno **sovrascritte** con quelle AD

> ⚠️ **RISCHIO CRITICO**: se il sync parte senza un piano fasato, tutta l'azienda potrebbe perdere accesso a email e Teams in un colpo solo.

### Mapping UPN (User Principal Name)
Il dominio locale (`colzani-nav.cloud`) verrà rimappato su quello cloud (`gruppocolzani.it`) tramite regole di traduzione in fase di sync.
Esempio: `attilio.fiumano@colzani-nav.cloud` → `attilio.fiumano@gruppocolzani.it`

### Sequenza tecnica concordata con Dev4Side
1. Setup **Entra Cloud Sync** (agente su WS2012) per sincronizzare le utenze e fare matching 1:1 con quelle cloud
2. Attivare **registrazione dispositivi** su Entra ID tramite Entra CS/Connect
3. Attivare **GPO** per Hybrid Join dei device della flotta

---

## Riferimenti

- [[TODO|TODO operativo]] — task aperti e prossimi step
- Taccuino: [[../TACCUINI/Stefano_Colzani|Stefano Colzani]]
