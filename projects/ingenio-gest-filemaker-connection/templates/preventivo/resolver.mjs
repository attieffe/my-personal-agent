import { findRecords, getRecord } from './filemaker.mjs';

const DB = 'DADEGEST';
const LAYOUT = 'V_PRE_000';

function meta(rec) {
  const f = rec.fieldData;
  return {
    recordId: rec.recordId,
    nr: f.Nr,
    anno: f.Anno,
    data: f.Data,
    ragioneSociale: f['Ragione Sociale'] ?? f['Ragione Sociale Cliente'] ?? '',
    note: (f['Note Documento'] || '').toString().split('\n')[0].slice(0, 80),
    totale: f.Totale,
  };
}

async function findByNumberAndYear(token, nr, anno) {
  const r = await findRecords(DB, token, LAYOUT, {
    query: [{ Nr: `==${nr}`, Anno: `==${anno}` }],
    limit: 5,
  });
  return r.data || [];
}

async function findByClient(token, clienteText, extra = {}) {
  const q = { 'Ragione Sociale': `*${clienteText}*` };
  if (extra.argomento) q['Note Documento'] = `*${extra.argomento}*`;
  if (extra.dataDa || extra.dataA) {
    if (extra.dataDa && extra.dataA) q.Data = `${extra.dataDa}...${extra.dataA}`;
    else if (extra.dataDa) q.Data = `>=${extra.dataDa}`;
    else if (extra.dataA) q.Data = `<=${extra.dataA}`;
  }
  const r = await findRecords(DB, token, LAYOUT, {
    query: [q],
    sort: [
      { fieldName: 'Data', sortOrder: 'descend' },
      { fieldName: 'Nr', sortOrder: 'descend' },
    ],
    limit: extra.limit ?? 20,
  });
  return r.data || [];
}

export async function resolvePreventivo(token, args) {
  if (args.recordId) {
    const rec = await getRecord(DB, token, LAYOUT, args.recordId);
    if (!rec) return { status: 'notfound', hint: `recordId ${args.recordId} non esiste in ${LAYOUT}` };
    return { status: 'found', recordId: rec.recordId, meta: meta(rec) };
  }

  if (args.nr) {
    const targetYear = args.anno ?? new Date().getFullYear();
    let recs = await findByNumberAndYear(token, args.nr, targetYear);
    if (recs.length === 1) {
      return { status: 'found', recordId: recs[0].recordId, meta: meta(recs[0]) };
    }
    if (recs.length > 1) {
      return { status: 'multiple', candidates: recs.map(meta), hint: `Più preventivi con Nr ${args.nr}/${targetYear}` };
    }
    if (!args.anno) {
      const prev = await findByNumberAndYear(token, args.nr, targetYear - 1);
      if (prev.length >= 1) {
        return {
          status: 'fallback',
          candidates: prev.map(meta),
          hint: `Nessun preventivo Nr ${args.nr} nel ${targetYear}. Trovato/i nel ${targetYear - 1}: rilancia con --anno ${targetYear - 1} per usarlo.`,
        };
      }
    }
    return { status: 'notfound', hint: `Nessun preventivo Nr ${args.nr} (${args.anno ? 'anno ' + args.anno : `${targetYear} né ${targetYear - 1}`}).` };
  }

  if (args.cliente) {
    const recs = await findByClient(token, args.cliente, {
      argomento: args.argomento,
      dataDa: args.dataDa,
      dataA: args.dataA,
      limit: args.ultimo ? 1 : 20,
    });
    if (recs.length === 0) {
      return { status: 'notfound', hint: `Nessun preventivo per cliente "${args.cliente}"${args.argomento ? ` con argomento "${args.argomento}"` : ''}.` };
    }
    if (args.ultimo || recs.length === 1) {
      return { status: 'found', recordId: recs[0].recordId, meta: meta(recs[0]) };
    }
    return { status: 'multiple', candidates: recs.map(meta), hint: `${recs.length} preventivi trovati — specifica con --nr o --argomento.` };
  }

  return { status: 'notfound', hint: 'Specifica almeno --nr, --cliente, o --recordId.' };
}
