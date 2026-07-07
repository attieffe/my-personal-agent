# Davide Rizzi

## Servizi
- Sviluppo gestionale in FileMaker

## Referenti
- Owner (tu): AttiEffe
- Referente cliente: 

## Roadmap
-

## TODO / Backlog

- [x] Attenzione: ribaltare TELA MICROFIBRA in TESSUTO introducenzo attributo 
- [ ] creazione automatica articoli da attributi con costruzione prezzi e descrizione
	- [ ] creare template su categoria
	- [ ] quando cambio macchinario intervenire su Altezza materiali
	- [ ] duplicare categorie e rinominarle
- [ ] Considerare quando si TAGLIA che la LUNGHEZZA può non esser soddisfatta perchè un rotolo anche più corto si taglia tante volte
	- [ ] A004652 => VENEZIA 47 H 220 [A005826 TEST ATTILIO]
	- [ ] A004228 => VENEZIA 47 H 35
	- [ ] A004876 => VENEZIA 47 H 23
	- [ ] A002444 => VENEZIA 47 H 30 [A005827 TEST ATTILIO]
	- [ ] A003746 => VENEZIA 47 H 9
	- [ ] Esempio 1
		- [ ] Procedura logica:
			- [ ] Se voglio 700 qta (metri lineari) del H 30, devo tagliare H220
			- [ ] H220 / H30 = 7,123, quindi 7 fasce H30 e 1 fascia H10 (220 - 30x7)
			- [ ] Mi servono (700 / 7 ) 100 metri dell'H220
		- [ ] Dopo il taglio ottengo:
			- [ ] 700 metri dell'H30
			- [ ] 700 metri H10 (capire se anagrafare o no)
	- [ ] Esempio 2
		- [ ] Procedura logica:
			- [ ] Se voglio 700 qta (metri lineari) del H 9, devo tagliare H220
			- [ ] H220 / H9 = 24,444, quindi 24 e 1 fascia H4 (220 - 9x24)
			- [ ] Mi servono (700 / 24 ) 29,17 metri dell'H220
		- [ ] Dopo il taglio ottengo:
			- [ ] 700 metri dell'H9
			- [ ] 700 metri alti H4
			
- [ ] generazione impegni per prodotto diretto, prodotto lavorato, e lavorazione iterativa (taglio+produzione)
- [ ] 16/6/2026 preparato script generazione impegni ma da affinare, il TIPO e RIFERIMENTI non sono impsotato, andrebbe creato ORDINE DI PRODUZIONE. E andrebbe fatto script che inizialmente SVUOTA GLI IMPEGNI e li ricrea tutti
- [ ] 7/7/2026 adeguare script Cerca articoli per estire caso in cui articolo non esiste
- [ ] Su ana temp locale 261776 
	- [ ] A005905
	- [ ] A005906
	- [ ] altro
- [ ] 261777
	- [ ] A005907

## Note
-
