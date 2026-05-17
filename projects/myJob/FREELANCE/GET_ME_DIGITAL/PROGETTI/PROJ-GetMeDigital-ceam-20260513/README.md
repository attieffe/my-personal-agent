# PROJ-GetMeDigital-ceam-20260513

## Anagrafica
- **ID progetto**: PROJ-GetMeDigital-ceam-20260513
- **Cliente/ramo**: CEAM (tramite agenzia Get Me Digital)
- **Obiettivo**: sistemare errore 403 di accesso tra alcuni paesi stranieri
- **Stack**: WordPress (presunto) + access control/geo restriction
- **Ambiente**: 

## Referenti
- **Tu (owner)**: AttiEffe
- **PM/Commerciale**: (Get Me Digital)
- **Dev**: 
- **Grafica/UX**: 
- **Sistemista/operazioni**: 
- **Consulenti esterni**: 

## Contesto & Requisiti
- Requisiti principali:
  - capire la causa del 403 tra paesi
  - applicare fix per permettere accesso alle aree corrette
- Vincoli:
  - 

## Deliverable
- Fix funzionante dell’accesso (403) per gli IP/paesi coinvolti

## TODO / Backlog
- [~] sistemare errore 403 di accesso tra alcuni paesi stranieri — **in attesa risposta NetSense** (provider hosting) per capire se possono intervenire (2026-05-17)

## Decisioni
-

## Changelog
- **2026-05-14** — Configurato proxy nginx temporaneo su server AttiBot (217.160.215.44) per bypassare blocco geo dell'hosting dal Brasile. Proxy pass verso 46.252.149.103, SSL con Cloudflare Origin Certificate, redirect 80→443. Soluzione temporanea in attesa di fix definitivo sul geo-blocking.

## Note tecniche
- 
