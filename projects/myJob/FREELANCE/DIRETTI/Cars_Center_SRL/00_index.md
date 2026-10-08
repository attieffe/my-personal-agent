# Cars Center SRL — indice

## Stato
- Stato: cliente attivo — **incident DNS/PEC: fase DNS RISOLTA** (aperto 2026-10-06 · DNS ok 2026-10-08 · resta test PEC funzionale)
- Ultimo aggiornamento: 2026-10-08

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

## Verifiche DNS 06/10 ore 16:22
- DNS pubblico (@8.8.8.8): NS **ancora su Cloudflare** (joel/sandy) → propagazione rollback in corso (attese 24-48h)
- Zona Aruba autoritativa (@dns.technorail.com) — **integra**:
  - NS: dns.technorail.com, dns2.technorail.com, dns3.arubadns.net, dns4.arubadns.cz
  - MX `pec.carscentersrl.it` → **10 mx.pec.aruba.it** ✓ (già presente, NON serve aggiungere record)
  - MX `carscentersrl.it` → 10 mx.carscentersrl.it ✓
- Zona Cloudflare invece: MX `pec.` **assente** → causa confermata PEC in entrata bloccate dal 02/08
- MX Cloudflare `_dc-mx.a83a23e1a862` risolve su 62.149.128.x (cluster mail Aruba)
- PEC in uscita da webmail ancora KO: ipotesi controlli DNS del servizio PEC o problema servizio — ritestare a propagazione completata

## Verifiche A/www/FTP 06/10 ore 16:30
- **Zona Cloudflare (attualmente pubblicata):** @, www, ftp → tutti proxied su IP Cloudflare 188.114.96.3 / 188.114.97.3 (+ IPv6 2a06:98c1:3120/3121::3). Origine nascosta dal proxy; FTP di fatto rotto (proxy Cloudflare = solo HTTP/HTTPS)
- **Zona Aruba (post-propagazione):** @ → **62.149.189.55** (IP originario confermato ✓) · www → CNAME carscentersrl.it · ftp → CNAME www.carscentersrl.it → 62.149.189.55
- ⚠️ Record A `188.114.97.7` su @ nella zona Aruba: inserito **manualmente da Atti** come ponte verso Cloudflare. Tecnicamente funziona solo finché la zona resta attiva su CF (routing per Host header su IP anycast condivisi); crea round-robin doppio binario (metà traffico proxy CF, metà diretto Aruba) e non copre FTP/mail/PEC. Da eliminare a propagazione completata se si resta su Aruba

## Verifiche 08/10 ore 09:03 — propagazione COMPLETATA ✅
- NS pubblici (default, 8.8.8.8, 1.1.1.1): **tutti su Aruba** (dns/dns2.technorail.com, dns3.arubadns.net, dns4.arubadns.cz) — Cloudflare joel/sandy spariti dalla vista pubblica
- `@` → **62.149.189.55** su tutti i resolver E sulla zona autoritativa ✓
- **Record sporco 188.114.97.7 NON più presente** nella zona Aruba (rimosso) ✓ — nessuna azione residua
- `www` → CNAME → 62.149.189.55 ✓ · `ftp` → CNAME → www ✓ (FTP tornato funzionante in routing)
- MX `pec.` → **10 mx.pec.aruba.it** visibile pubblicamente ✓ → causa PEC in entrata perse (02/08) eliminata a livello DNS
- MX principale → 10 mx.carscentersrl.it ✓
- **Sito attivo**: http/https 200 — il .it fa 301 → **carscentersrl.com** (.com su hosting WordPress.com, 192.0.78.x) → titolo corretto. Quindi il dominio vero del sito è il **.com**; il .it su Aruba fa solo redirect (comportamento pre-esistente, non un problema)

**Rimane da fare (lato utente):**
1. Test PEC in entrata (farsi mandare una PEC e verificare l'arrivo)
2. Ritest PEC in uscita da webmail — se ancora KO, guardare pannello PEC Aruba (sospensione/quota)
3. Zona Cloudflare ormai inerte: resta nell'account o si cancella, indifferente

## Problemi aperti
- **PEC in entrata**: causa DNS risolta (08/10, MX pec pubblici su Aruba) → resta **test funzionale di consegna**
- **PEC in uscita**: causa non chiara, da ritestare a DNS propagato — se KO da webmail il problema è nel servizio PEC, non nel DNS

→ Task attivi in [[TODO_GENERALE]] sezione freelance · diretto · cars center srl

## Aree
- `01_meetings/`
- `02_communications/`
- `03_deliverables/`
- `90_archive/`
