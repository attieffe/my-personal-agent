# Dev4Side Adeguamento Sistemistico — TODO

## ✅ Completati

- [x] Fix blocco join dominio AD — locator SRV corretto (DC annunciato con suffisso dominio)
- [x] Test join su PC vergine — dominio OK

---

## 🔴 Critici / Alta priorità

- [ ] **Meeting lunedì 18/05 ore 11:00** con Dev4Side — allineamento strategia Entra ID sync e implicazioni credenziali
- [ ] **Definire piano fasato per sync credenziali** — AD sovrascrive cloud → rischio blackout email/Teams per tutta l'azienda; onboarding utente per utente o per gruppo

---

## 🟡 In corso / Prossimo

- [ ] Ricevere **report azioni** da Dev4Side (promised dal consulente dopo fix)
- [ ] Setup **Entra Cloud Sync** su WS2012 — installare agente, configurare da portale cloud
  - ⚠️ Entra Connect richiede WS2016+; Cloud Sync supportato su WS2012
- [ ] **Mapping utenti AD ↔ Entra ID** — definire regole UPN (`colzani-nav.cloud` → `gruppocolzani.it`), verificare utenti esistenti su cloud, evitare duplicati
- [ ] **Registrazione dispositivi** su Entra ID via Entra Cloud Sync/Connect
- [ ] **GPO Hybrid Join** — pushare policy su PC già joinati AD (silenzioso per utenti)
  - Alternativa: Direct Entra ID Join (verificare autorizzazioni utenti)

---

## 🔵 Da pianificare

- [ ] **DC Upgrade WS2012 → WS2025** — swing migration (nuovo DC, FSMO transfer, decommission vecchi DC) — rientra nelle 3 giornate T&M se i tempi lo consentono
- [ ] **Assessment infrastruttura** completo — raccogliere dati per roadmap modernizzazione (proposta dedicata futura da Dev4Side)
- [ ] Test **VPN** — bassa priorità, indipendente, gestibile in autonomia

---

## ℹ️ Note operative

- Attività monitorate su: https://activities.dev4side.com (credenziali fornite da Dev4Side all'accettazione offerta)
- Dev4Side invia email mensile con dettaglio giornate eseguite; contestazioni entro 5 gg dalla ricezione
