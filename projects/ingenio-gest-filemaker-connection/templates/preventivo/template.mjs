const ITALIAN_NUMBER = new Intl.NumberFormat('it-IT', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const ITALIAN_INT = new Intl.NumberFormat('it-IT', { minimumFractionDigits: 0, maximumFractionDigits: 3 });

function escapeHtml(s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function fmtMoney(n) {
  if (n === null || n === undefined || n === '') return '';
  const num = Number(n);
  if (!Number.isFinite(num)) return '';
  return ITALIAN_NUMBER.format(num);
}

function fmtQty(n) {
  if (n === null || n === undefined || n === '') return '';
  const num = Number(n);
  if (!Number.isFinite(num)) return '';
  return ITALIAN_INT.format(num);
}

function fmtPercent(n) {
  if (n === null || n === undefined || n === '' || Number(n) === 0) return '';
  return `${ITALIAN_INT.format(Number(n))}%`;
}

function fmtDateITFromUS(s) {
  if (!s) return '';
  const m = String(s).match(/^(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})$/);
  if (!m) return s;
  const [, mm, dd, yyyy] = m;
  return `${dd.padStart(2, '0')}/${mm.padStart(2, '0')}/${yyyy}`;
}

function noteToHtml(text) {
  if (!text) return '';
  const safe = escapeHtml(text);
  return safe
    .split(/\n{2,}/)
    .map(par => `<p>${par.replace(/\n/g, '<br>')}</p>`)
    .join('\n');
}

function buildScontoText(r) {
  const parts = [r.sconto1, r.sconto2, r.sconto3].filter(s => s !== null && s !== undefined && Number(s) !== 0);
  return parts.map(p => fmtPercent(p)).filter(Boolean).join(' + ');
}

function buildRiepilogoIva(righe, ivaCodes) {
  const groups = new Map();
  for (const r of righe) {
    const key = r.codiceIva || '—';
    const g = groups.get(key) || { codice: key, imponibile: 0, iva: 0, descrizione: '', aliquota: 0 };
    const code = ivaCodes?.[key];
    g.descrizione = code?.descrizione || (g.descrizione || `IVA ${key}`);
    g.aliquota = code?.aliquota ?? g.aliquota;
    g.imponibile += Number(r.imponibile) || 0;
    const ivaRiga = (Number(r.imponibile) || 0) * (Number(g.aliquota) || 0) / 100;
    g.iva += ivaRiga;
    groups.set(key, g);
  }
  return Array.from(groups.values());
}

export function generateHtml(data, options = {}) {
  const { testata, righe, parametri, logoDataUri, ivaCodes } = data;
  const ivaInclusa = options.ivaInclusa === true;
  const flags = testata.flagsStampa;

  const tipoDocMap = { 'Preventivi': 'Preventivo', 'fatture': 'Fattura', 'ddt': 'DDT', 'Ordini': 'Ordine' };
  const tipoDoc = (tipoDocMap[testata.tabella] || testata.tabella || 'Preventivo').toUpperCase();
  const dataDoc = fmtDateITFromUS(testata.data);
  const dataValidita = fmtDateITFromUS(testata.dataValidita);
  const oggetto = testata.oggettoEmail || '';

  const showQta = !flags.senzaQta;
  const showParziali = !flags.senzaParziali;
  const showTotali = flags.stampaTotale;
  const showFirma = flags.stampaFirma;
  const valoreColonna = ivaInclusa ? 'totaleRiga' : 'imponibile';
  const valoreColTitle = ivaInclusa ? 'Totale (IVA incl.)' : 'Imponibile';

  const riepilogo = buildRiepilogoIva(righe, ivaCodes);

  const ibanFinale = parametri.iban || testata.ibanPreventivo || '';
  const bancaFinale = parametri.bancaNome || '';

  const styles = `
:root {
  --ink: #1a1a1a;
  --muted: #6b6b6b;
  --line: #c8c8c8;
  --soft: #f3f4f6;
  --accent: #0f3b66;
  --accent-soft: #eaf1f8;
  --strong: #0a2440;
}

* { box-sizing: border-box; }

@page {
  size: A4;
  margin: 12mm 12mm 14mm 12mm;
}

html, body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  font-size: 9.5pt;
  color: var(--ink);
  line-height: 1.35;
}

.doc {
  width: 100%;
}

/* --- HEADER --- */
.header {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 18px;
  align-items: center;
  border-bottom: 2px solid var(--accent);
  padding-bottom: 10px;
  margin-bottom: 14px;
}
.header .logo img {
  max-width: 220px;
  max-height: 70px;
  object-fit: contain;
}
.header .azienda {
  text-align: right;
}
.header .azienda .ragsoc {
  font-size: 13.5pt;
  font-weight: 700;
  color: var(--strong);
  letter-spacing: 0.2px;
}
.header .azienda .meta {
  margin-top: 4px;
  color: var(--muted);
  font-size: 8.5pt;
}

/* --- DESTINATARI --- */
.destinatari {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 12px;
}
.dest-box {
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 9px 11px;
  background: white;
}
.dest-box .label {
  font-size: 7.8pt;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--accent);
  letter-spacing: 0.6px;
  margin-bottom: 4px;
}
.dest-box .codice {
  font-size: 7.6pt;
  color: var(--muted);
  margin-left: 8px;
  font-weight: 400;
}
.dest-box .row { font-size: 9.5pt; }
.dest-box .row.bold { font-weight: 700; font-size: 10pt; }
.dest-box .row.muted { color: var(--muted); font-size: 8.6pt; }

/* --- DOC META --- */
.doc-meta {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1.2fr 1.4fr 1.2fr;
  border: 1px solid var(--line);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 14px;
  background: var(--soft);
}
.doc-meta .cell {
  padding: 7px 11px;
  border-right: 1px solid var(--line);
}
.doc-meta .cell:last-child { border-right: none; }
.doc-meta .label {
  font-size: 7.6pt;
  text-transform: uppercase;
  color: var(--muted);
  letter-spacing: 0.5px;
}
.doc-meta .value {
  font-weight: 700;
  font-size: 10.5pt;
  color: var(--strong);
}
.doc-meta .cell.tipo .value {
  color: var(--accent);
  font-size: 11pt;
}

/* --- OGGETTO --- */
.oggetto {
  font-size: 11pt;
  font-weight: 600;
  color: var(--strong);
  margin: 4px 0 10px 2px;
}

/* --- NOTE DOCUMENTO --- */
.note {
  margin: 0 0 14px 0;
  font-size: 9.6pt;
  color: var(--ink);
  background: var(--accent-soft);
  border-left: 3px solid var(--accent);
  padding: 9px 12px;
  border-radius: 0 6px 6px 0;
  white-space: normal;
}
.note p { margin: 0 0 6px 0; }
.note p:last-child { margin-bottom: 0; }
.note.salto-pagina { page-break-before: always; }

/* --- RIGHE TABLE --- */
table.righe {
  width: 100%;
  border-collapse: collapse;
  font-size: 9.4pt;
  margin-bottom: 14px;
}
table.righe thead th {
  background: var(--strong);
  color: white;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 7.8pt;
  letter-spacing: 0.5px;
  padding: 6px 8px;
  text-align: left;
}
table.righe thead th.num { text-align: right; }
table.righe tbody td {
  padding: 7px 8px;
  border-bottom: 1px solid var(--line);
  vertical-align: top;
}
table.righe tbody td.num { text-align: right; }
table.righe tbody td.imp {
  font-weight: 600;
  color: var(--strong);
}
table.righe tbody tr { page-break-inside: avoid; }
table.righe .codart { color: var(--muted); font-size: 8.4pt; }

/* --- BOTTOM AREA --- */
.bottom {
  display: grid;
  grid-template-columns: 1fr 1.1fr 1fr;
  gap: 10px;
  margin-top: 10px;
  page-break-inside: avoid;
}
.bottom.no-firma { grid-template-columns: 1fr 1fr; }
.bottom.no-totali { grid-template-columns: 1fr 1fr; }
.bottom.no-firma.no-totali { grid-template-columns: 1fr; }

/* Per accettazione */
.firma {
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 110px;
}
.firma .label {
  font-size: 8pt;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--accent);
  letter-spacing: 0.5px;
}
.firma .firma-line {
  border-top: 1px solid var(--ink);
  margin-top: 50px;
  padding-top: 4px;
  font-size: 8pt;
  text-align: center;
  color: var(--muted);
}

/* Riepilogo IVA */
.riepilogo {
  border: 1px solid var(--line);
  border-radius: 6px;
  overflow: hidden;
}
.riepilogo .label {
  background: var(--soft);
  padding: 6px 10px;
  font-size: 7.8pt;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--accent);
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--line);
}
.riepilogo table {
  width: 100%;
  border-collapse: collapse;
  font-size: 8.6pt;
}
.riepilogo th, .riepilogo td {
  padding: 4px 8px;
  text-align: left;
}
.riepilogo th.num, .riepilogo td.num { text-align: right; }
.riepilogo th {
  font-weight: 600;
  color: var(--muted);
  font-size: 7.4pt;
  text-transform: uppercase;
  border-bottom: 1px solid var(--line);
}

/* Totali */
.totali {
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 10px 12px;
  background: white;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.totali .row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 9.4pt;
}
.totali .row.muted { color: var(--muted); }
.totali .row.imponibile {
  background: var(--accent-soft);
  color: var(--strong);
  padding: 8px 2px;
  border-radius: 4px;
  margin: 4px -2px;
}
.totali .row.imponibile .val {
  font-size: 16pt;
  font-weight: 800;
  letter-spacing: -0.3px;
}
.totali .row.imponibile .lbl {
  font-size: 8.6pt;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.totali .row.totale {
  border-top: 1px solid var(--line);
  padding-top: 6px;
  margin-top: 4px;
  font-weight: 700;
  font-size: 10.4pt;
  color: var(--strong);
}

/* --- BANCA + FOOTER --- */
.banca {
  margin-top: 12px;
  padding: 7px 10px;
  background: var(--soft);
  border-radius: 4px;
  font-size: 8.6pt;
  color: var(--ink);
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  justify-content: center;
}
.banca .item .lbl {
  color: var(--muted);
  text-transform: uppercase;
  font-size: 7.4pt;
  letter-spacing: 0.5px;
  margin-right: 4px;
}
.banca .item .val { font-weight: 600; }

.footer {
  margin-top: 6px;
  border-top: 1px solid var(--line);
  padding-top: 5px;
  font-size: 7.6pt;
  color: var(--muted);
  text-align: center;
}
`;

  const html = `<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>${escapeHtml(tipoDoc)} ${escapeHtml(testata.nr)}/${escapeHtml(testata.anno)} — ${escapeHtml(testata.cliente.ragioneSociale)}</title>
  <style>${styles}</style>
</head>
<body>
  <div class="doc">

    <div class="header">
      <div class="logo">
        ${logoDataUri ? `<img src="${logoDataUri}" alt="Logo">` : `<div style="font-weight:700;font-size:14pt;color:var(--strong);">${escapeHtml(parametri.ragioneSociale)}</div>`}
      </div>
      <div class="azienda">
        <div class="ragsoc">${escapeHtml(parametri.ragioneSociale)}</div>
        <div class="meta">
          ${escapeHtml(parametri.indirizzo)} · ${escapeHtml(parametri.cap)} ${escapeHtml(parametri.citta)} (${escapeHtml(parametri.provincia)})<br>
          P. IVA: ${escapeHtml(parametri.piva)} · Cod. Fis.: ${escapeHtml(parametri.cf)}
        </div>
      </div>
    </div>

    <div class="destinatari">
      <div class="dest-box">
        <div class="label">Dati Fatturazione ${testata.cliente.codice ? `<span class="codice">cod. ${escapeHtml(testata.cliente.codice)}</span>` : ''}</div>
        <div class="row bold">${escapeHtml(testata.cliente.ragioneSociale)}</div>
        <div class="row">${escapeHtml(testata.cliente.indirizzo)}</div>
        <div class="row">${escapeHtml(testata.cliente.cap)} ${escapeHtml(testata.cliente.citta)}${testata.cliente.provincia ? ` (${escapeHtml(testata.cliente.provincia)})` : ''}</div>
        ${testata.cliente.piva ? `<div class="row muted">P.IVA: ${escapeHtml(testata.cliente.piva)}${testata.cliente.cf && testata.cliente.cf !== testata.cliente.piva ? ` · Cod Fisc: ${escapeHtml(testata.cliente.cf)}` : ''}</div>` : ''}
      </div>
      ${testata.destinazione ? `
      <div class="dest-box">
        <div class="label">Destinazione Merce ${testata.destinazione.codice ? `<span class="codice">cod. ${escapeHtml(testata.destinazione.codice)}</span>` : ''}</div>
        <div class="row bold">${escapeHtml(testata.destinazione.ragioneSociale || testata.cliente.ragioneSociale)}</div>
        <div class="row">${escapeHtml(testata.destinazione.indirizzo)}</div>
        <div class="row">${escapeHtml(testata.destinazione.cap)} ${escapeHtml(testata.destinazione.citta)}${testata.destinazione.provincia ? ` (${escapeHtml(testata.destinazione.provincia)})` : ''}</div>
        ${testata.destinazione.telefono ? `<div class="row muted">Tel: ${escapeHtml(testata.destinazione.telefono)}</div>` : ''}
      </div>
      ` : `
      <div class="dest-box" style="background:var(--soft);">
        <div class="label">Destinazione Merce</div>
        <div class="row muted" style="margin-top:4px;">Coincide con i dati di fatturazione</div>
      </div>
      `}
    </div>

    <div class="doc-meta">
      <div class="cell tipo">
        <div class="label">Tipo documento</div>
        <div class="value">${escapeHtml(tipoDoc)}</div>
      </div>
      <div class="cell">
        <div class="label">Numero</div>
        <div class="value">${escapeHtml(testata.nr)}/${escapeHtml(testata.anno)}</div>
      </div>
      <div class="cell">
        <div class="label">Data</div>
        <div class="value">${escapeHtml(dataDoc)}</div>
      </div>
      <div class="cell">
        <div class="label">Pagamento</div>
        <div class="value" style="font-size:9pt;">${escapeHtml(testata.pagamento.descrizione || '—')}</div>
      </div>
      <div class="cell">
        <div class="label">Validità offerta</div>
        <div class="value">${escapeHtml(dataValidita || '—')}</div>
      </div>
    </div>

    ${oggetto ? `<div class="oggetto">${escapeHtml(oggetto)}</div>` : ''}

    ${testata.note ? `<div class="note ${flags.saltoPaginaRequisiti ? 'salto-pagina' : ''}">${noteToHtml(testata.note)}</div>` : ''}

    <table class="righe">
      <thead>
        <tr>
          <th style="width:11%;">Cod. articolo</th>
          <th>Descrizione</th>
          <th style="width:5%;">UM</th>
          ${showQta ? `<th class="num" style="width:7%;">Qtà</th><th class="num" style="width:9%;">Prezzo unit.</th>` : ''}
          <th class="num" style="width:8%;">Sconto</th>
          ${showParziali ? `<th class="num" style="width:11%;">${escapeHtml(valoreColTitle)}</th>` : ''}
          <th class="num" style="width:6%;">Cod. IVA</th>
        </tr>
      </thead>
      <tbody>
        ${righe.map(r => `
        <tr>
          <td><span class="codart">${escapeHtml(r.codiceArticolo || r.tipologia || '')}</span></td>
          <td>${escapeHtml(r.descrizione)}</td>
          <td>${escapeHtml(r.um)}</td>
          ${showQta ? `<td class="num">${fmtQty(r.qta)}</td><td class="num">${fmtMoney(r.prezzo)}</td>` : ''}
          <td class="num">${escapeHtml(buildScontoText(r))}</td>
          ${showParziali ? `<td class="num imp">${fmtMoney(r[valoreColonna])}</td>` : ''}
          <td class="num">${escapeHtml(r.codiceIva)}</td>
        </tr>
        `).join('')}
      </tbody>
    </table>

    ${(showFirma || riepilogo.length || showTotali) ? `
    <div class="bottom ${!showFirma ? 'no-firma' : ''} ${!showTotali ? 'no-totali' : ''}">
      ${showFirma ? `
      <div class="firma">
        <div class="label">Per accettazione</div>
        <div class="firma-line">timbro e firma</div>
      </div>
      ` : ''}

      ${riepilogo.length ? `
      <div class="riepilogo">
        <div class="label">Riepilogo IVA</div>
        <table>
          <thead>
            <tr><th>Cod</th><th>Descrizione</th><th class="num">Imponibile</th><th class="num">Imp. IVA</th></tr>
          </thead>
          <tbody>
            ${riepilogo.map(g => `
            <tr>
              <td>${escapeHtml(g.codice)}</td>
              <td>${escapeHtml(g.descrizione)}</td>
              <td class="num">${fmtMoney(g.imponibile)}</td>
              <td class="num">${fmtMoney(g.iva)}</td>
            </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      ` : ''}

      ${showTotali ? `
      <div class="totali">
        <div class="row imponibile">
          <span class="lbl">Imponibile</span>
          <span class="val">€ ${fmtMoney(testata.totali.imponibile)}</span>
        </div>
        <div class="row muted">
          <span>IVA</span>
          <span>€ ${fmtMoney(testata.totali.iva)}</span>
        </div>
        <div class="row totale">
          <span>Totale</span>
          <span>€ ${fmtMoney(testata.totali.totale)}</span>
        </div>
      </div>
      ` : ''}
    </div>
    ` : ''}

    ${(ibanFinale || bancaFinale) ? `
    <div class="banca">
      ${bancaFinale ? `<div class="item"><span class="lbl">Banca d'appoggio:</span><span class="val">${escapeHtml(bancaFinale)}</span></div>` : ''}
      ${ibanFinale ? `<div class="item"><span class="lbl">IBAN:</span><span class="val">${escapeHtml(ibanFinale)}</span></div>` : ''}
      ${parametri.bicSwift ? `<div class="item"><span class="lbl">BIC/SWIFT:</span><span class="val">${escapeHtml(parametri.bicSwift)}</span></div>` : ''}
    </div>
    ` : ''}

    ${parametri.piePagina ? `<div class="footer">${escapeHtml(parametri.piePagina)}</div>` : ''}

  </div>
</body>
</html>`;

  return html;
}
