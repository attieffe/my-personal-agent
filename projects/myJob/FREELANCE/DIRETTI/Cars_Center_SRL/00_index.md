# Cars Center SRL — indice

## Stato
- Stato: cliente attivo — **incident DNS/PEC in corso** (aperto 2026-10-06)
- Ultimo aggiornamento: 2026-10-06

## Anagrafica
- Ragione sociale: Cars Center SRL
- Sede: Cavenago
- Dominio: carscentersrl.it
- Hosting/DNS origin: Aruba

## Dati tecnici — DNS
- **02/08/2026**: terzi hanno impostato Cloudflare sul dominio, nameserver:
  - `joel.ns.cloudflare.com.`
  - `sandy.ns.cloudflare.com.`
- `62.149.189.55` → era l'IP del record `@` (root) su Aruba
- `188.114.97.7` → IP su cui puntava carscentersrl.it durante il periodo Cloudflare
- **06/10/2026**: rimessi i nameserver principali di Aruba (rollback)

## Problemi aperti
- **PEC in entrata**: non arrivano — probabile causa: nameserver di carscentersrl.it su Cloudflare non configurati correttamente
- **PEC in uscita**: non si possono mandare — causa non chiara, non funziona nemmeno da webmail

→ Task attivi in [[TODO_GENERALE]] sezione freelance · diretto · cars center srl

## Aree
- `01_meetings/`
- `02_communications/`
- `03_deliverables/`
- `90_archive/`
