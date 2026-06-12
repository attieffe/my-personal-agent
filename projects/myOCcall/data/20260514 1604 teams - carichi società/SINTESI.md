# Sintesi call â€” teams â€” 2026-05-14 â€” Carichi SocietÃ 

## Info call
- **Piattaforma:** Teams
- **URL:** https://teams.microsoft.com/meet/329092404545340?p=0WjEkgYWCxmJNDAhzg
- **Bot join:** ~16:04 (Europe/Rome)
- **Bot leave:** ~17:37 (Europe/Rome)
- **Durata registrata:** ~1h33m
- **Segmenti:** 1 valido (unico segmento lungo)
- **Parole trascritte:** 655

---

## Partecipanti

| Nome | Ruolo | Presenza |
|------|-------|----------|
| Attilio (bot) | IT Manager / registratore | Presente confermato |
| Speaker principale (non attribuito) | Parla per la maggior parte della trascrizione | Presente confermato |
| **Omar** | Proponente della sostituzione Excel | Presente confermato (citato direttamente) |
| **Giorgio** | Operativo magazzino â€” destinatario di alcuni strumenti IT | Citato |
| **Nadia** | Figura operativa coinvolta nel processo carichi | Citata |
| **Alessandro** | Operativo (spunta carichi, stampa) | Citato |

---

## Contesto e inizio riunione

La call parte da un tema concreto: il file Excel attualmente usato come strumento di sincronizzazione tra piÃ¹ persone del processo di gestione carichi non basta piÃ¹. Omar ha sollevato la proposta di sostituirlo con qualcosa di piÃ¹ strutturato. Il punto di partenza Ã¨ che non si tratta solo di fare un foglio migliore, ma di valutare se costruire un portale o una dashboard che prenda il posto dell'Excel e renda il lavoro piÃ¹ affidabile.

---

## Argomenti trattati

- Valutazione del file Excel attuale come strumento di coordinamento (semi-manuale, soggetto a errori di copiatura)
- Ipotesi di sostituzione con portale/dashboard
- Giacenze come informazione operativa: necessitÃ  di avere la giacenza WMS visibile senza passare tra WMS e NAV manualmente
- Alert automatici su righe in ritardo o prossime alla criticitÃ 
- Visualizzazione di spedizioni, note, filtri rapidi in un'unica vista
- Righe bloccate / non prelevate / da ricreare: il caso tipico in cui un prodotto risulta caricato e stampato ma il giorno dopo la riga Ã¨ ancora ferma
- Riduzione del tempo perso in filtri e controlli incrociati ripetitivi
- Ruolo di Giorgio nella creazione di nuove righe per riprovare il prelievo

---

## Considerazioni e pareri emersi

- **La giacenza non Ã¨ un dato statico:** sottolineato che la giacenza puÃ² cambiare in 15 minuti, ma averla disponibile nel flusso aiuta a decidere subito se intervenire sul fornitore o no, senza giri tra WMS e NAV.
- **Gli alert cambiano il comportamento operativo:** avere una data in colonna non Ã¨ la stessa cosa di avere un segnale che fa emergere le righe critiche. Senza controlli giornalieri dedicati, chi ha altre responsabilitÃ  non riesce a dare la prioritÃ  giusta.
- **Il tempo perso nei filtri Ã¨ il vero problema percepito:** gran parte del tempo nelle riunioni operative viene speso a filtrare, incrociare dati e identificare le righe da sensibilizzare.
- **Un portale non Ã¨ una cosa leggera da fare:** riconosciuto esplicitamente che costruire una dashboard integrata richiede energie IT significative.
- **Il rischio di errore umano nella copiatura Ã¨ reale:** il processo attuale comporta copiaincolla che puÃ² introdurre errori.

---

## Decisioni prese

> âš ï¸ **Nota di Attilio (da HUMAN.MD):** Nonostante siano emerse perplessitÃ  sull'Excel e la proposta di un portale, la decisione finale Ã¨ di **restare su Excel** per mancanza di budget e risorse IT sufficienti.

**La decisione Ã¨: restare su Excel, con i seguenti impegni IT:**

1. **Giacenza WMS in Excel + link diretto**
   Inserire nel file Excel la giacenza WMS del prodotto corredata da un link di collegamento diretto alla scheda nel WMS. Obiettivo: eliminare il passaggio manuale tra Excel e WMS per ogni controllo.

2. **Strumento massivo per spedizioni parziali** *(in carico a IT â€” utente: Giorgio)*
   Sviluppare uno strumento che consenta di:
   - Impostare in modo massivo la **testata ordine a STATO 4**
   - Attivare contestualmente la **spedizione parziale**
   Il problema attuale: il sistema sposta anche le righe insieme alla testata. Lo strumento deve permettere lo spostamento della testata **senza spostamento delle righe**.

3. **Valutazione sistema di ALERT** *(da approfondire)*
   Valutare quale approccio adottare:
   - Portale con programmazione abituale (schedulazione periodica)
   - Cowork â€” su quale PC gira? *(da chiarire con Giorgio)*
   - Forma agentica / sperimentale â€” es. OPENCLAW

---

## Note di Attilio (da HUMAN.MD)

- Il budget e le risorse IT disponibili non permettono di avviare un progetto portale ora. Per questo si resta su Excel con miglioramenti puntuali.
- I tre impegni IT sopra sono le azioni concrete emerse dalla call come prioritÃ .
- **SeguirÃ  un'altra riunione sullo stesso tema, ma senza la partecipazione dell'IT.**

---

## Azioni IT in carico

| Azione | Assegnatario ipotetico | PrioritÃ  |
|--------|------------------------|----------|
| Inserire giacenza WMS + link in Excel | IT (da assegnare) | Alta |
| Strumento massivo testata â†’ STATO 4 + spedizione parziale | IT / utente Giorgio | Alta |
| Valutare architettura sistema ALERT | IT (portale vs cowork vs OPENCLAW) | Media |

> âœ… **TODO Attilio:** Revisiona questa SINTESI e conferma assegnazioni IT â†’ aggiunto in `projects/myJob/COLZANI/PERSONALI/README.md`

---

## Estratto trascrizione (frasi utili)

> *"quello che intende Omar Ã¨ la sostituzione del file Excel, cioÃ¨ non usare piÃ¹ il file Excel come metodo di sincronia tra le varie persone coinvolte nel processo"*

> *"la gecenza Ã¨ un'informazione completamente collaterale che se aggiorni un quarto d'ora dopo magari Ã¨ cambiata, quindi si puÃ² fare, sicuramente non Ã¨ una cosa super light da fare"*

> *"il non avere la giacenza del prodotto ci puÃ² aiutare nel capire che se c'Ã¨ un ordine in ritardo ma l'articolo fornitore ci dice che c'Ã¨ una giacenza, noi non dobbiamo andare a guardare singolo articolo per singolo articolo in WMS e NAV"*

> *"un conto avere i dati di consegna, un conto avere un alert che ti dice guarda che fra dieci giorni tutte queste righe qua sono in ritardo"*

> *"il giorno dopo ci troviamo la riga non prelevata perchÃ© qualcosa si Ã¨ bloccato [...] ed eventualmente dire a Giorgio di creare una nuova riga per provare a fare il prelievo"*

> *"nei nostri incontri tanto tempo lo perdiamo nel fare questi filtri"*

---

## Note qualitÃ  trascrizione

- Un solo segmento audio valido (trascrizione continua, 655 parole).
- Speaker attribution: un solo speaker identificato come "Sconosciuto" nella trascrizione attribuita. La conversazione sembra coinvolgere almeno due persone, ma l'attribuzione DOM non ha prodotto dati sufficienti.
- Vedi `trascrizione.txt` per il testo integrale; `trascrizione_attribuita.md` per il tentativo di attribuzione.
