# MEMORY.md - Long-Term Memory

_Memoria curata — distillato di ciò che ho imparato. Le prime 200 righe vengono auto-caricate in ogni sessione principale._

Dettagli giornalieri raw → `memory/YYYY-MM-DD.md` · Progetti → [progetti.md](progetti.md)

---

## 🎯 Lezioni Critiche

### Cron
- Job `agentTurn` con chiamate modello/web_fetch: timeout **generoso** (240-300s+). Casi 09/2026 (meteo 60s → doppio messaggio + retry): ora tutti ≥240s; "TODO scadenze light" 20→120s
- `systemEvent` su main: ~10-30ms, nessun rischio
- Sintomo timeout: messaggi doppi + notifiche errore = run scaduto che completa comunque + retry riuscito
- **Caso 09/10**: cron "ToDo Colzani" falliva sempre — `toolsAllow` senza `read` → nella allowlist mettere TUTTI gli strumenti che il prompt usa

### Regole Ferree
- **SEMPRE `Europe/Rome`** per date/ora (mai UTC)
- Verificare conti su Sheet specifici: **CASA ≠ PERSONALE** (piani dei conti diversi); aggiornare sia file locali che Sheet
- **MAI azioni distruttive** senza permesso esplicito; `trash` > `rm`
- **⭐ LEGGI PRIMA DI CREARE**: cercare sempre il file `.md` esistente più adatto → aggiornarlo; se non esiste → chiedere conferma ad Atti con path proposto. (Caso BMW_X1: creato duplicato ignorando file esistente. Mai più.)
- **Segreti nei link firmati** (09/2026): parametri `q-ak` di link COS/fatture Z.ai contengono credenziali → mai incollarli integri in file tracciati da git; `.md` preview vanno sanitizzati
- **COLZANI = workspace separato** — non esiste in myOcSync
- Transcript vocale sbaglia nomi ("Colsanit"=Colzani, "Sportit"→Brico Sport) — normalizzare SEMPRE e confermare

### Naming mio-tesoro
- `mio-tesoro-file` (full privacy) · `mio-tesoro-paas` (full service) · `mio-tesoro-cloud` (cloud ibrido) · `mio-tesoro-sheet` (Google Sheet senza webapp)

### Routing myJob
- Idee/brainstorming → `PERSONALE/lavori_a_casa/idee_progetti/INDEX` · Implementazione → `projects/<nome>/`
- TODO: **SEMPRE in `TODO_GENERALE.md`** (fonte unica) + opzionale file specifico (agenzia: `FREELANCE/<AGENZIA>/<AGENZIA>_INDEX.md`; personale: `PERSONALE/TODO_PERSONALE.md`)
- Prima di modificare TODO leggere [[projects/myJob/ROUTING]] · ambiguo → chiedere ad Atti · MAI toccare `_TEMPLATE/`
- Cliente diretto → aggiornare file cliente + `PERSONALE/README.md` · Sinapps e GMD = lavoro da CASA · registro agenzie: [[PERSONALE/lavori_a_casa/41_clienti_agenzie]]

---

## 🏗️ Decisioni Architetturali

### myOCcall — Pipeline Audio
ffmpeg chunk 300s → `audio/segments/` + `manifest.tsv` → Whisper multi-segmento → merge `trascrizione.txt` → controlli anti-falsa-trascrizione prima della sintesi. Stack: PulseAudio+ffmpeg+null sink+Whisper API. Path: `projects/myOCcall/data/YYYYMMDD HHMM <platform>/`

### AttiBot — File intake
`https://attibot.ingeniosolution.it/upload` → ref `UP-YYYYMMDD-HHMMSS-XXXXXX` → `/home/openclaw/attibot/uploads/<ref>/` con `manifest.json`

### myJob — Struttura
```
FREELANCE/ (GET_ME_DIGITAL socio 2017 · SINAPPS T PROJECT SRL · NEWU_SRL 2023 Plenitude · STUDIO_VISUAL occasionale · DIRETTI/)
PERSONALE/ (famiglia/hobby, ex ATTILIO_A_CASA) · INGENIO_SOLUTION/ (società di Atti) · EMAIL/ (IMAP)
```
Convenzione nuova agenzia: [[projects/myJob/CONVENTIONS]] §10

### myJob — Email IMAP Workflow
- Cron oraria (solo UNSEEN) → notifica Telegram non tecnica/sintetica: mittente reale + azione proposta + link originale + % confidenza (no UID)
- Flow: `00_inbox/` → `incoming_untriaged.md` → conferma Atti → azione → `90_archive/` + rimozione da untriaged (mai email con azione già eseguita lì)
- Regole operative: `INBOX_WORKFLOW.md`

### Stato Servizi (2026-10)
- Cron email myJob (`01d3cd46`) + AOS (`52ac6a54`): **disabled** da ~21 ago, in attesa Atti — NON insistere
- google_meet calendar_events: OAuth mancante — calendario in skip

### Modelli AI
- Runtime: **zai/glm-4.7** · cron agentTurn: modelli leggeri/nano · vocali: OpenAI API
- Claude Code: account Pro (`sonnet`/`opus`/`haiku`); default non-Colzani `anthropic/claude-sonnet-4-6`, Colzani `github-copilot/claude-sonnet-4.6`

---

## 👤 Preferenze Operative (Atti)

- **IAcopo**: ingegnere informatico, simpatico, preciso, sicuro · italiano · Europe/Rome
- Email myJob: non tecnico, sintetico · Telegram: diretto, no fumo · routine padel via cron: formattata Telegram-friendly
- **Slot liberi (MyAgenda)**: chiedere se per call o città specifica (città → considerare spostamenti/durata eventi successivi) · Colzani: solo slot negli orari base Colzani incrociati col calendario · personali: ignorare orari Colzani · lavoro: inizio non oltre le 18
- **Scontrini benzinaio** (audio/foto): estrarre distributore/stazione/indirizzo/numero/data/ora/importo/volume/tipo benzina → TODO con scadenza domani
- Cron OpenClaw update check 20:00: nuova release → TODO in TODO_GENERALE.md
- **Padel**: checklist (borsone, bibita, fascia, orologio) + checklist mentale pre-partita con data/ora inserimento (vibora palla davanti, impugnatura continental, palla profonda, palla lenta se lontano da rete, rovesci piatti forti) + routine individuale (smash, 3, volée, smorzata, rovescio, vibora) — dettagli in `hobby/32_padel.md`
- Attrezzatura censita in `32_padel.md`: ASICS Gel-Resolution X (07/2025, da pronatore) + 2× adidas Metalbone HRD+ 3.4 · 09/10/2026 soletta usurata ma scarpa ok → valutare sola sostituzione soletta
- Sessioni Telegram: stessa chat = stesso contesto · separare con `NUOVO CONTESTO: <tema>` / `USA FILO: <tema>`

---

## 🔧 Informazioni Tecniche

### myJob Email
```
Host: mail.ingsoftware.it · IMAP 993 | SMTP 465 · User: myjob@ingeniosolution.it · Pass: in .env
```

### ADB wireless → S23 (Tailscale) ✅
- `~/tools/s23connect.sh` auto-connette · telefono `s23-di-attilio` = 100.97.50.126 (SM-S916B S23 Ultra, Android 16)
- Pairing persistente dal 14/10/2026 — NO re-pairing · **tcpip 5555 attivo dal 14/10** (stabile anche a schermo spento, fino a riavvio; dopo riavvio: Debug wireless ON + script)
- pm install da /sdcard bloccato (FUSE) → copiare APK in /data/local/tmp · APK vecchi: `--bypass-low-target-sdk-block`
- Lezione pairing: dialogo muore se esci dalla schermata → vista divisa Impostazioni+Telegram

### Miotesoro — Vendor Mapping frequenti (dettagli: `docs/vendor-mapping.md`)
Acqua & Sapone → Supermercati · Osteria del Gelato → Uscite · Alperia ~90-100€ → Corrente (altrimenti Gas) · OVS/D115 Carugo → Abbigliamento · Corsico HFB → Arredamento (IKEA) · Pepco/Max Factory → Supermercati · Shopsi Srl e Tri Malnatt → Alimenti qualità

### TTS
OpenAI TTS (`tts-1`) · voce `nova` · italiano · dopo invio del file in chat, cancellarlo dal filesystem

### Cars Center SRL — DNS/PEC (10/2026)
- 02/08: Cloudflare di terzi con zona incompleta → PEC perse · 06/10 rollback NS Aruba · **08/10 propagazione completata, zona pulita** (sito .it→301 carscentersrl.com, MX PEC ok)
- Resta SOLO test PEC funzionale (lato Atti); uscita KO → pannello PEC Aruba · Dossier: `FREELANCE/DIRETTI/Cars_Center_SRL/00_index.md`

### Server IPTV — intv-server (skill `iptv-server`)
- In tailnet `ralf00@`: `intv-server` 100.117.206.109 · Tailscale SSH ACL `accept` → `ssh root@100.117.206.109` (chiave id_ed25519_iptv inutilizzata: port 22 = Tailscale SSH)
- PM2 v5.4.3 come utente `ubuntu` (SEMPRE `sudo -u ubuntu pm2`, mai pm2 da root): index :8080 · record :8081 · sync_lines · source_monitor · app in /home/ubuntu/nodeapp
- Skill `iptv-server`: controllo ON-DEMAND (status/health/logs/restart) · **MAI azioni non richieste, restart solo con OK esplicito** (feedback Atti 16/10) · watchdog NON armato (non richiesto)
- GET / su :8080 non risponde by design ("streaming ignorata") → NON è un hang, non usare come health check

### Canale YouTube tech (ideazione 15/10)
- Struttura: `PERSONALE/lavori_a_casa/idee_progetti/canale_youtube_tech/` → piano_editoriale (16 titoli) · analisi_mercato · creazione_video/{strumentazione,software_utili,montaggio}
- Stack scelto: DaVinci Resolve free (principale, CapCut solo verticali) · Auto-Editor (taglio silenzi) · ffmpeg (automatismi) · Remotion/Jitter/Flourish (infografiche animate)

### Synology NAS DS220+ (10/2026)
- **Jellyfin** via Container Manager (network host, /dev/dri Quick Sync) · media read-only: /volume1/homes/{attilio,chiara}/Photos · config in /volume1/docker/jellyfin · vecchio contenitore manuale "jelly-container" da eliminare
- Cast su Chromecast vecchia (solo-cast): richiede **HTTPS con certificato pubblico anche in LAN** → piano: record A su dominio → ACME :80 → reverse proxy DSM **:2097** → localhost:8096 · remoto via OpenVPN NAS esistente (niente Tailscale) · telefono = solo telecomando
- Synology Photos video remoto KO: fix = DSM Accesso esterno → Porta esterna (DDNS) HTTP **2095** / HTTPS **2096**
- DA FARE: ffmpeg verticali (bruciare rotazione), marca/modello TV (app nativa?), chi gestisce DNS ingeniosolution.it, guida OpenVPN+Jellyfin per suoceri

### Ingenio Solution — strategia web (10/2026)
- Home **v0.4** in preview (`attibot.ingeniosolution.it/reports/20261011_ingenio_home`) · CTA "Incontro di fattibilità gratuito" (mai "30 min", veto)
- **v0.5 IN ATTESA DEL VIA** — input pronti in `STRATEGIA_ACQUISIZIONE_WEB.md` §3
- **Doppia passata copy = STANDARD**: GPT-5.5 (chiave OpenAI env) → revisione IAcopo · brief: `WEBSITE/gpt5_copy_brief.json`
- Portfolio: `PORTFOLIO_PROGETTI.md` (11 voci, [?] per dettagli mancanti, mappa → landing A automazione/B MCP/C custom)

---

## 📂 Progetti

Registro canonico: [progetti.md](progetti.md) · Nuovo progetto solo se: ambito distinto + config dedicata + ciclo autonomo → cartella `projects/<nome>/` + file (CHANGELOG, TODO, TECNICO, SINTESI, APPUNTI) + voce in registro.

- **miotesoro-sheet-agent**: finanze personali su Google Sheets (CASA/PERSONALE) → spese/entrate, movimenti bancari
- **myOCcall**: auto-join videocall + trascrizione Whisper + sintesi → call/trascrizioni
- **myJob**: TODO, clienti (GMD/Sinapps/Newu/StudioVisual/diretti), famiglia, INGENIO_SOLUTION, email → TODO/clienti/email

Routing: "registra spesa" → miotesoro · "trascrivi call" → myOCcall · "TODO/cliente/email" → myJob · dubbio → progetti.md

---

## 🏠 Pratiche Famiglia

### Dossier Stato Civile Francese
- CNI rinnovo: pre-domanda ANTS **WMQRZ8M1N5** · **CNI arrivata in consolato (16/10)** — ritiro senza appuntamento Lun-Gio 9-12/14-16, Ven 9-12, entro **13/01/2027** · France Identité: link monouso già consumato, pratica vive nell'app (QR); finalizzazione (NFC + fronte carta) solo DOPO il ritiro · porta la vecchia CNI, va restituita
- Regole: atto nascita francese da solo NON prova nazionalità (serve menzione a margine o CNF) · CNI italiana = solo doc identità genitori · atti per Roma SOLO copie integrali cartacee ORIGINALI timbro+firma (PDF digitali rifiutati, atti non tornano) · atti Chiara+matrimonio Corbetta+atto francese Atti: vincolo <3 mesi alla spedizione
- Spedizione: Ambassade de France à Rome — Service de l'état civil, Piazza Farnese 67, 00186 Roma · dettagli in TODO_GENERALE

### Salute
- Cronologia: `projects/myJob/PERSONALE/salute/Cronologia_Sanitaria.md`
- **02/10/2026 ginocchio destro padel: contrattura popliteo (fisio 14/10) — DA MONITORARE** · piano: carico modulato (no padel finché lampo in flessione), max 1 test/giorno, no FANS orale, crema FANS ok, NO infiltrazioni · red flags → ecografia: gonfiore, cedimento senza dolore, blocco estensione · contesto: 16/08 punti PS (scogli) · 28/08 torcicollo→schiena

### MoneyViz (aggiornato 29/09)
Pacchetto CRYPTO 53€ + tax DEGIRO omaggio (in attesa OK sblocco) · "plusvalenze 42,52€" erano prelievi (chiuso) · wallet/xpub: FISCO/PERSONALE/dichiarazioni_anno_2025

### Concordato Preventivo Biennale 2026-27 (Ingenio)
Proposta Buraschi (24/6): 2026 reddito **61.573€**/IRAP 48.376€ · 2027 62.809€/49.585€ — fattibile · **Adesione entro 30/11/2026** · `INGENIO_SOLUTION/AMMINISTRAZIONE/Concordato preventivo.md`

---

## 🔄 Manutenzione

Heartbeat review (~ogni 5 giorni): leggere file giornalieri recenti → distillare qui → rimuovere obsoleto. **Limite: 200 righe.**

---

_Ultimo aggiornamento: 2026-10-18 (revisione 14-18/10: CNI ritirabile 13/01/2027, piano ginocchio, canale YouTube, Jellyfin/Synology)_
