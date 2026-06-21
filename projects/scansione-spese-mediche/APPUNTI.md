# APPUNTI

## CF Alice — da verificare
Calcolato manualmente: `FMNLCA22L65B729C`
Dati usati: Fiumanò Alice, F, 25/07/2022, Carate Brianza (codice catastale B729)
Verificare su codicefiscale.it prima del primo utilizzo.

## OCR su ricevute farmacia
Tesseract funziona bene su testo stampato pulito. Se la scansione è storta o a bassa risoluzione, la qualità cala. In quel caso: aumentare DPI a 400 nello script (`dpi=400` in `get_pixmap()`).

## Struttura/farmacia via LLM
Il nome della struttura è troppo variabile per regex affidabile — viene sempre delegato a Haiku. Consuma ~300-500 token per pagina. Per 60 pagine: ~$0.01-0.02 totali.
