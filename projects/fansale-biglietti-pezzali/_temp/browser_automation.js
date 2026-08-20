/**
 * Script per estrarre biglietti dalla pagina FanSale
 * Naviga attraverso gli eventi e raccoglie i dati
 */

// Estrae i biglietti da una pagina evento
function extractTickets() {
  const tickets = [];

  // Cerca elementi che contengono "Quantità"
  const textContent = document.body.innerText;
  const lines = textContent.split('\n');

  let currentTicket = null;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    // Trova linee con "Quantità"
    if (line.includes('Quantità')) {
      // Estrai il numero dopo "Quantità"
      const match = line.match(/Quantità[\s]*(\d+)/);
      if (match) {
        const qty = parseInt(match[1]);

        if (qty >= 2) {
          // Inizia a raccogliere info per questo biglietto
          currentTicket = {
            quantita: qty,
            descrizione: [],
            prezzo: 'N/A',
            blocco: 'N/A'
          };
        }
      }
    }

    // Raccoglie info per il biglietto corrente
    if (currentTicket) {
      if (line.includes('€')) {
        currentTicket.prezzo = line;
      }
      if (line.includes('Blocco')) {
        currentTicket.blocco = line;
      }

      currentTicket.descrizione.push(line);

      // Fine del biglietto (quando vediamo la prossima quantità o altri marker)
      if ((line.includes('Quantità') && currentTicket.descrizione.length > 1) ||
          line.includes('Vendi biglietti') ||
          line.includes('Alert offerte')) {

        // Filtra Parterre e Posto Unico
        const fullText = currentTicket.descrizione.join(' ').toUpperCase();
        if (!fullText.includes('PARTERRE') && !fullText.includes('POSTO UNICO')) {
          tickets.push({
            quantita: currentTicket.quantita,
            descrizione: currentTicket.descrizione.slice(0, 3).join(' | '),
            prezzo: currentTicket.prezzo,
            blocco: currentTicket.blocco
          });
        }
        currentTicket = null;
      }
    }
  }

  return tickets;
}

// Ritorna i biglietti
JSON.stringify(extractTickets());
