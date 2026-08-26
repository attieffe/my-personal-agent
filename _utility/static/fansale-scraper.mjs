#!/usr/bin/env node
/**
 * Fansale.it scraper usando patchright (Node.js)
 * Basato sullo script originale test-fansale-patchright.mjs
 */

import { chromium } from 'patchright';
import { readFile, writeFile } from 'node:fs/promises';

// Selettori (stessi dello script originale)
const CONTAINER_SELECTOR = '#EventDetailsAndListingCard > div.Card.Card-onEventDetailsPage.Card-isMobileCard.EventDetail-Listing.js-EventDetail-Listing.EventDetail-Listing-seatmapLoaded > div.EventEntryList.js-EventEntryList.EventEntryList-clearFloat.u-flexboxSortingContainer';
const OFFER_SELECTOR = CONTAINER_SELECTOR + ' > .EventEntry';

const log = (...args) => console.error(new Date().toISOString(), ...args);

// Funzione di estrazione offerte (stessa dello script originale)
async function extractOffers(page) {
  return page.$$eval(OFFER_SELECTOR, (nodes) =>
    nodes.map((el) => {
      const seatDesc = el.getAttribute('data-seatdescriptionforarialabel') || '';
      const parseField = (label) => {
        const match = seatDesc.match(new RegExp(label + '\\s*([^|]+)', 'i'));
        return match ? match[1].trim() : null;
      };
      const qtyEl = el.querySelector('.NumberOfTicketsInOffer');
      return {
        offerId: el.getAttribute('data-offer-id'),
        quantita: qtyEl ? qtyEl.textContent.trim() : el.getAttribute('data-splitting-possibilities'),
        ingresso: parseField('Ingresso'),
        fila: parseField('Fila'),
        posto: parseField('Posto'),
        blocco: parseField('Blocco'),
        tipoOfferta: el.getAttribute('data-offertype'),
        prezzo: el.getAttribute('data-splitting-possibility-prices'),
        fairDeal: el.getAttribute('data-fairdeal') === 'true',
        certified: el.getAttribute('data-certified') === 'true',
      };
    })
  );
}

async function scrapeEvent(browser, event) {
  const result = {
    url: event.url,
    titolo: event.titolo,
    data: event.data,
    timestamp: new Date().toISOString(),
    success: false,
    offers: [],
    error: null
  };

  const context = await browser.newContext({
    locale: 'it-IT',
    viewport: { width: 1366, height: 900 },
  });

  try {
    const page = await context.newPage();

    log('Navigo a', event.url);
    await page.goto(event.url, { waitUntil: 'domcontentloaded', timeout: 60000 });

    // Gestisci cookie banner (stessa logica script originale)
    const cookieSelectors = [
      'button#onetrust-accept-btn-handler',
      'button:has-text("Accetta")',
      'button:has-text("Accetto")',
      'button:has-text("Accept")',
    ];

    for (const sel of cookieSelectors) {
      try {
        const btn = page.locator(sel).first();
        if (await btn.isVisible({ timeout: 3000 })) {
          await btn.click();
          log('Cliccato banner cookie:', sel);
          break;
        }
      } catch {}
    }

    await page.waitForTimeout(3000);

    // Cerca container
    let containerFound = false;
    try {
      await page.waitForSelector(CONTAINER_SELECTOR, { timeout: 20000 });
      containerFound = true;
      log('Container trovato');
    } catch {
      log('Container non trovato entro 20s');
    }

    const finalContainer = page.locator(CONTAINER_SELECTOR);
    const finalCount = await finalContainer.count();
    log('Occorrenze selettore container:', finalCount);

    if (finalCount > 0) {
      const offers = await extractOffers(page);
      log('Offerte estratte:', offers.length);
      result.offers = offers;
      result.success = true;
    } else {
      const bodyText = await page.locator('body').innerText();
      if (bodyText.includes('Access Denied')) {
        result.error = 'Access Denied - bot detection attivo';
        log('ERRORE: Access Denied');
      } else {
        result.error = 'Container offerte non trovato';
        log('ERRORE: Container non trovato');
      }
    }

  } catch (err) {
    log('ERRORE:', err.message);
    result.error = err.message;
  } finally {
    await context.close();
  }

  return result;
}

async function scrapeEvents(events) {
  const results = {
    timestamp: new Date().toISOString(),
    total_events: events.length,
    successful: 0,
    failed: 0,
    events: []
  };

  // Riusa stesso browser per tutti gli eventi (più efficiente)
  const browser = await chromium.launch({
    headless: false,
    channel: 'chrome'
  });

  try {
    for (const event of events) {
      log(`\n=== Scraping: ${event.titolo} (${event.data}) ===`);
      const result = await scrapeEvent(browser, event);
      results.events.push(result);

      if (result.success) {
        results.successful++;
      } else {
        results.failed++;
      }
    }
  } finally {
    await browser.close();
  }

  return results;
}

// Main
if (process.argv.length < 3) {
  console.error('Uso: fansale-scraper.mjs <events_json_file>');
  console.error('');
  console.error('Il file JSON deve contenere un array di oggetti:');
  console.error('[{"url": "...", "titolo": "...", "data": "..."}]');
  process.exit(1);
}

const inputFile = process.argv[2];

try {
  log('Caricamento eventi da', inputFile);
  const eventsData = await readFile(inputFile, 'utf-8');
  const events = JSON.parse(eventsData);

  log(`Caricati ${events.length} eventi da processare\n`);

  const results = await scrapeEvents(events);

  // Output JSON su stdout
  console.log(JSON.stringify(results, null, 2));

  log(`\nCompletato: ${results.successful}/${results.total_events} successi`);

} catch (err) {
  log('ERRORE FATALE:', err.message);
  process.exit(1);
}
