import { login, logout, getRecord, getRecords, downloadContainer } from './filemaker.mjs';
import { resolvePreventivo } from './resolver.mjs';

export async function fetchAllData(args) {
  const out = {};

  const dadeToken = await login('DADEGEST');
  try {
    const resolution = await resolvePreventivo(dadeToken, args);
    out.resolution = resolution;
    if (resolution.status !== 'found') return out;

    const testata = await getRecord('DADEGEST', dadeToken, 'V_PRE_000', resolution.recordId);
    out.testata = normalizeTestata(testata);
    out.righe = extractRighe(testata);
  } finally {
    await logout('DADEGEST', dadeToken);
  }

  const paramToken = await login('Parametri');
  try {
    const r = await getRecords('Parametri', paramToken, 'Parametri', { limit: 1 });
    const fd = r.data?.[0]?.fieldData || {};
    out.parametri = normalizeParametri(fd);
    if (fd['Logo max 9.5x2.5']) {
      try {
        const dl = await downloadContainer(fd['Logo max 9.5x2.5'], paramToken);
        out.logoDataUri = dl?.dataUri || null;
      } catch (err) {
        console.error(`[warn] Logo download failed: ${err.message}`);
        out.logoDataUri = null;
      }
    }
  } finally {
    await logout('Parametri', paramToken);
  }

  const anagToken = await login('anagrafiche');
  try {
    const r = await getRecords('anagrafiche', anagToken, 'Iva', { limit: 100 });
    out.ivaCodes = {};
    for (const rec of (r.data || [])) {
      const f = rec.fieldData;
      const code = String(f.Codice ?? '').trim();
      if (!code) continue;
      out.ivaCodes[code] = {
        codice: code,
        descrizione: (f.Descrizione || '').trim(),
        aliquota: Number(f.Aliquota) || 0,
        flagNI: String(f['Flag NI'] || '').trim().toLowerCase() === 'x',
      };
    }
  } finally {
    await logout('anagrafiche', anagToken);
  }

  return out;
}

function num(v) {
  if (v === null || v === undefined || v === '') return null;
  const n = Number(String(v).replace(',', '.'));
  return Number.isFinite(n) ? n : null;
}

function str(v) {
  return v === null || v === undefined ? '' : String(v).trim();
}

function normalizeTestata(rec) {
  const f = rec.fieldData;
  return {
    recordId: rec.recordId,
    nr: f.Nr,
    anno: f.Anno,
    data: f.Data,
    dataValidita: f['Data Validita'],
    tabella: f.Tabella,
    stato: f.Stato,
    oggettoEmail: f['oggetto email'],
    note: f['Note Documento'] || '',

    cliente: {
      codice: str(f['Cod Cliente']),
      ragioneSociale: str(f['Ragione Sociale']),
      indirizzo: str(f.Indirizzo),
      cap: str(f.Cap),
      citta: str(f['Città']),
      provincia: str(f.Povincia ?? f.Provincia),
      piva: str(f['P.iva']),
      cf: str(f['C.F.']),
      telefono: str(f['Clienti::Telefono 1']) || str(f['Clienti::Telefono 2']) || str(f['Clienti::Cellulare 1']),
      email: str(f['Clienti::Email 1']) || str(f['Clienti::Email 2']),
    },

    destinazione: extractDestinazione(f),

    pagamento: {
      codice: str(f['Cod Pagamento']),
      descrizione: str(f['Descrizione Pagamento']),
    },

    totali: {
      imponibile: num(f['Totale Imponibile']) ?? 0,
      iva: num(f['Totale Iva']) ?? 0,
      totale: num(f.Totale) ?? 0,
    },

    flagsStampa: {
      stampaTotale: yes(f['STAMPA TOTALE']),
      stampaFirma: yes(f['STAMPA FIRMA PER ACCETTAZIONE']),
      senzaQta: notEmpty(f['Stampa SENZA QTA']),
      senzaParziali: notEmpty(f['Stampa SENZA PARZIALI']),
      saltoPaginaRequisiti: notEmpty(f['STAMPA SALTO PAGINA CON REQIUSITI']),
    },

    ibanPreventivo: str(f["Parametri Preventivo::IBAN banca d'appoggio"]),
  };
}

function extractDestinazione(f) {
  const cod = str(f['Cod Detinazione Merce']);
  const ragSoc = str(f['Ragione Sociale Destinazione Merce']);
  const indirizzo = str(f['Indirizzo Destinazione merce']);
  const cap = str(f['Cap Destinazione merce']);
  const citta = str(f['Città Destinazione merce']);
  const provincia = str(f['Provincia Destinazione merce']);
  const tel1 = str(f['Telefono 1 Destinazione merce']);
  const tel2 = str(f['Telefono 2 Destinazione merce']);
  const hasAny = cod || ragSoc || indirizzo || cap || citta || provincia || tel1 || tel2;
  if (!hasAny) return null;
  return { codice: cod, ragioneSociale: ragSoc, indirizzo, cap, citta, provincia, telefono: tel1 || tel2 };
}

function extractRighe(rec) {
  const portal = rec.portalData?.['Righe Vendita Preventivo'] || [];
  return portal.map(row => {
    const get = (k) => row[`Righe Vendita Preventivo::${k}`];
    return {
      recordId: row.recordId,
      tipologia: str(get('TIPOLOGIA_ARTICOLO')),
      codiceArticolo: str(get('CODICE_ARTICOLO')),
      descrizione: str(get('DESCRIZIONE')),
      um: str(get('UM')),
      qta: num(get('QTA')) ?? 0,
      prezzo: num(get('Prezzo')) ?? 0,
      prezzoNetto: num(get('Prezzo_Netto')) ?? 0,
      prezzoFinale: num(get('Prezzo f')) ?? 0,
      sconto1: num(get('Sc_1')),
      sconto2: num(get('Sc_2')),
      sconto3: num(get('Sc_3')),
      imponibile: num(get('imponibile')) ?? 0,
      totaleRiga: num(get('Totale riga')) ?? 0,
      codiceIva: str(get('CodiceIva')),
    };
  });
}

function normalizeParametri(f) {
  return {
    ragioneSociale: str(f['Ragione Sociale']),
    piva: str(f['P.iva']),
    cf: str(f['C.f.']),
    indirizzo: str(f.Indirizo),
    cap: str(f.Cap),
    citta: str(f['Città']),
    provincia: str(f.Prov),
    bancaIntestazione: str(f['Intestazione banca']),
    bancaNome: str(f["Nome Banca d'appoggio"]),
    iban: str(f["IBAN banca d'appoggio"]),
    bicSwift: str(f['BIC SWIFT']),
    abi: str(f.ABI),
    cab: str(f.CAB),
    piePagina: normalizeFooter(str(f['pie pagina'])),
  };
}

function normalizeFooter(s) {
  return s.replace(/(\S)tel\./i, '$1 · tel.').replace(/\s+e-mail/i, ' · e-mail').replace(/Italy\s*-/i, 'Italy ·');
}

function yes(v) {
  return String(v ?? '').trim().toUpperCase() === 'SI';
}
function notEmpty(v) {
  return String(v ?? '').trim().length > 0;
}
