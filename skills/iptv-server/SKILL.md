---
name: "iptv-server"
description: "Controllo on-demand del server IPTV intv-server via Tailscale SSH + PM2 (utente ubuntu). Solo su richiesta esplicita di Atti."
---

# IPTV Server Control (intv-server)

Skill per controllare **on-demand** il server IPTV di Atti. Ogni operazione parte SOLO da una richiesta esplicita di Atti: nessun watchdog automatico, nessuna azione non richiesta.

## Target

- **Nodo Tailscale:** `intv-server` — IP tailnet `100.117.206.109` (account `ralf00@`)
- **Accesso:** Tailscale SSH dal gateway (nodo `ubuntu`), ACL `action: accept` → nessuna chiave, nessuna approvazione browser
- **Comando base:**
  ```bash
  ssh -o BatchMode=yes -o ConnectTimeout=10 root@100.117.206.109 '<comando>'
  ```
- **OS:** Ubuntu 22.04.4 LTS

## Regole operative (FERREE)

1. **Solo su richiesta di Atti.** Letture (status, log, porte) ok senza chiedere; MAI azioni oltre a quanto chiesto.
2. **Restart solo con consenso esplicito** di Atti (es. "riavvia index").
3. PM2 gira come utente `ubuntu` → usare SEMPRE `sudo -u ubuntu pm2 ...`.
   MAI `pm2` diretto da root: spawna un daemon vuoto parallelo. (Se capita per errore: `pm2 kill` da root per ripulire.)
4. Non modificare configurazioni (DNS, Apache, systemd, firewall) se non richiesto esplicitamente.
5. La porta 22 è gestita da Tailscale SSH: la chiave `~/.ssh/id_ed25519_iptv` NON viene usata lì.

## Mappa servizi (verificata 2026-10-16)

- **PM2 v5.4.3**, daemon utente `ubuntu`, home `/home/ubuntu/.pm2`, startup systemd attivo (`pm2-ubuntu`), modulo `pm2-logrotate`
- **App dir:** `/home/ubuntu/nodeapp`
- **Processi PM2:**
  - `index` (pm_id 1) → app IPTV principale, ascolta **:8080**
  - `record` (pm_id 2) → ascolta **:8081**
  - `sync_lines` (pm_id 3)
  - `source_monitor` (pm_id 4)
- **Log PM2:** `/home/ubuntu/.pm2/logs/<nome>-out.log` e `<nome>-error.log`
- **Altro sul server:** n8n in Docker :5678 · MySQL locale :3306 · Apache :80/:443

## Comandi della skill

- **STATUS** — `sudo -u ubuntu pm2 ls` + `ss -tlnp` + uptime/disco/memoria
- **HEALTH** — probe TCP su :8080, :8081 (+ :5678 se richiesto); `pm2 jlist` per restart count e uptime
- **RESTART `<nome>`** — `sudo -u ubuntu pm2 restart <nome>` (solo con OK esplicito)
- **LOGS `<nome>` [n]** — tail di out+err (default 30 righe)
- **DESCRIBE `<nome>`** — `pm2 describe` completo

## Note tecniche importanti (lezioni 16/10)

- **GET / su :8080 NON risponde PER SCELTA DEL CODICE** (nei log: "Chiamata streaming ignorata e nessuna risposta inviata al client"). Un probe HTTP su / va in timeout ANCHE a servizio perfettamente sano → NON usare GET / come health check, non è un indicatore di hang.
- `record` su :8081 risponde 404 su / → per liveness basta "risponde HTTP con qualsiasi codice".
- Health check affidabile per `index`: **solo TCP connect** sulla porta + stato PM2. Eventuali check app-level richiederebbero una rotta player con parametri validi (da chiedere ad Atti prima di implementare).
- Le richieste player reali passano da rotte dedicate (`panel_api.php`, `get.php`, `/bridge`, admin su `/4dM111287`).
