# Appunti — miotesoro (myMoney)

Note operative, workaround, decisioni prese in corso d'opera.

---

## Token OAuth2

Il token è nel file `.env` nella cartella del progetto. Non cercarlo in variabili d'ambiente di sistema o nella home.

## Fogli Google Sheets

- I due fogli (PERSONALE e CASA) hanno struttura simile ma non identica
- Le colonne di formula post-append differiscono: K-W per PERSONALE, K-S per CASA
- Mai usare riferimenti di un foglio per validare l'altro

## Formato dati

- Importi sempre con virgola decimale (es. `45,50` non `45.50`)
- Date in formato europeo `DD/MM/YYYY`
- Timezone sempre Europe/Rome, non UTC

## Agente revisore

L'agente revisore in `agents/revisore-registrazioni.agent.md` va sempre coinvolto prima di qualsiasi append. Non saltarlo mai, anche per registrazioni "ovvie".
