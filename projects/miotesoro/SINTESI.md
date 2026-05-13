# Sintesi — miotesoro (myMoney)

## Cos'è

Copilot AI per la gestione finanziaria personale di Atti. Permette di registrare entrate e uscite su due fogli Google Sheets (PERSONALE e CASA) con validazione automatica e zero errori di doppia registrazione.

## Cosa fa

- Registra movimenti finanziari (entrate, uscite, trasferimenti) su Google Sheets
- Valida ogni registrazione prima di inserirla (niente duplicati, niente errori)
- Mantiene la coerenza tra il foglio PERSONALE e quello CASA
- Applica categorie automaticamente in base al venditore/merchant

## Come si usa

1. Di' a AttiBot cosa vuoi registrare (es. "ho speso 45€ al supermercato Esselunga")
2. AttiBot verifica, categorizza e chiede conferma se c'è ambiguità
3. Con la tua conferma, registra sul foglio corretto
4. Ti conferma la registrazione avvenuta

## File di riferimento

- Istruzioni operative complete: `miotesoro.md`
- Come fare una registrazione passo-passo: `docs/REGISTRAZIONE-RUNBOOK.md`
