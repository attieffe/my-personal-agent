# Vendor → Conto Mapping (Ingenio Revolut)

Mapping vendor da estratti/import ai conti contabili.
Validare sempre il conto contro il foglio target: alcuni mapping sotto sono specifici CASA e non sono conti validi su PERSONALE.

## Confermati

| Vendor | Conto | Note |
|--------|-------|------|
| Pv1241 | Spese\|Auto\|Benzina | Distributore benzina, storico consolidato |
| Boom Di Veggian Sarae | Spese\|Prima necessità\|Pasto OPPURE Spese\|Casa condivise\|Conto Casa | Ristorante/bar - dipende dal contesto: pasto personale vs spesa condivisa. CHIEDERE SEMPRE |
| Amazon Music* | Spese\|Casa condivise\|Conto Casa | Abbonamento musica, spesa condivisa |
| Amazon Primei | Spese\|Svago\|Amazon Prime | Abbonamento Prime |
| Biemme Motorit | Spese\|Auto\|Tagliando | Officina auto/moto |
| Balza Multiservice Srlt | Spese\|Auto\|Batteria | Manutenzione auto (batteria) |
| Coldi Oil Service | Spese\|Auto\|Benzina | Distributore carburante |
| Commissione Revolut Business | Spese\|Banche\|Canone conto | Canone mensile Revolut Business |
| Pepe 68 | Spese\|Prima necessità\|Pasto | Bar/ristorante |
| Chiara Muscatello (anticipo utili) | Spese\|Casa condivise\|Bonifico Conto Casa | Anticipo utili società |
| GRUPPO COLZANI SRL (Fondi aggiunti) | Entrate\|Attività\|Ingenio Ac + Portafoglio\|Temp\|IVA Incassata | Fattura mensile con IVA (3 righe: Entrate, Portafoglio, IVA) - spesso esiste già come "Previsto", aggiornare stato |
| Playtomic | Spese\|Sport\|Padel | Prenotazione campi padel |
| Country 1 | Spese\|Sport\|Padel lezioni | Lezioni padel |
| Elle Padel Club | Spese\|Sport\|Padel | Campo padel |
| Mariano Sports Arena | Spese\|Sport\|Padel tornei OPPURE Spese\|Prima necessità\|Pasto | Torneo o consumazione - CHIEDERE SEMPRE |
| Kinesis Sport Seregno | Spese\|Mediche\|Fisioterapista | Fisioterapia |
| Google One | Spese\|Tech\|Google One | Abbonamento storage Google |
| To Condominio Mazzini 3 | Spese\|Casa condivise\|Condominio Ord. | Spesa condominiale ordinaria |
| Parrocchia Di Santa Vale | Spese\|Svago\|Uscite | Attività parrocchiali |
| Acqua & Sapone | Spese\|Prima necessità\|Supermercati vari | Confermato da Atti: supermercati vari |
| Osteria Del Gelato | Spese\|Svago\|Uscite | Gelateria/uscite |
| Alperia | Spese\|Immobile\|Corrente OPPURE Spese\|Immobile\|Gas | Se importo circa 90/100€ → Corrente; altrimenti tipicamente Gas |
| OVS | Spese\|Cura persona\|Abbigliamento | Abbigliamento bambini/bimbi; usare questo conto, non Istruzione |
| Corsico Hfb | Spese\|Arredamento\|Ikea | Vendor IKEA, arredamento |
| Pepco Cantù | Spese\|Prima necessità\|Supermercati vari | Confermato da Atti: supermercati vari |
| Shopsi Srl | Spese\|Prima necessità\|Alimenti qualità | NaturaSì / alimenti qualità |
| Max Factory | Spese\|Prima necessità\|Supermercati vari | Confermato da Atti: supermercati vari |
| D115 Carugo | Spese\|Cura persona\|Abbigliamento | Abbigliamento bimbi; esempio 05/05 -€38,02; usare questo conto, non Istruzione |

## Contropartite ricorrenti

| Caso | Contropartita | Note |
|------|---------------|------|
| Portafoglio\|Ptf\|Amazon | Entrate\|Vt\|Vt | Incassi VT: di solito il Portafoglio Amazon si chiude con entrata VT |

## Note
- Le operazioni Colzani hanno spesso già righe "Previsto" pre-inserite → aggiornare a "Eseguito" + data corretta
- Boom Di Veggian Sarae è ambiguo: chiedere sempre all'utente se Pasto o Conto Casa
- Mariano Sports Arena è ambiguo: chiedere sempre se torneo o pasto
- Alperia è condizionale: circa 90/100€ = Corrente, importi diversi tipicamente Gas
- I mapping `Supermercati vari`, `Alimenti qualità`, `Cura persona|Abbigliamento`, `Arredamento|Ikea`, `Immobile|Corrente/Gas` sono stati validati sul foglio CASA.
- Caratteri speciali (à, è, etc.) richiedono UTF-8 encoding
- ATTENZIONE: dopo un append, verificare SEMPRE `updatedRange` dalla response. Il 15/04 l'op001 è stata duplicata per errore perché non si è verificato bene l'output.
