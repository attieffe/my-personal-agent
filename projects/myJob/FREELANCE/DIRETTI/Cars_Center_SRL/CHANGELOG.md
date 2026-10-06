# CHANGELOG — Cars Center SRL

## 2026-10-06
- Creazione dossier cliente
- **Incident DNS/PEC** su carscentersrl.it:
  - 02/08/2026 (ricostruzione): terzi impostano Cloudflare (`joel.ns.cloudflare.com` / `sandy.ns.cloudflare.com`)
  - IP storici: `62.149.189.55` (record @ su Aruba), `188.114.97.7` (dominio durante periodo Cloudflare)
  - Oggi: rollback nameserver ai principali di Aruba
- TODO aperti: PEC in entrata non arrivano · PEC in uscita bloccate (anche da webmail)
- 16:22 verifiche DNS: zona Aruba integra (MX pec. → mx.pec.aruba.it già presente); DNS pubblico ancora su Cloudflare, attesa propagazione 24-48h. Nessun record da aggiungere.
