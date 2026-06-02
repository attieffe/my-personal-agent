// Bypass TLS verification for FileMaker self-signed certificate on localhost.
// Sicuro perché ci connettiamo solo a https://localhost/. Sopprimiamo il warning di Node.
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
const _origEmit = process.emit;
process.emit = function (name, data, ...args) {
  if (name === 'warning' && data?.name === 'Warning' && /NODE_TLS_REJECT_UNAUTHORIZED/.test(String(data?.message))) {
    return false;
  }
  return _origEmit.call(process, name, data, ...args);
};

const HOST = process.env.FM_HOST || 'localhost';
const PORT = process.env.FM_PORT || '443';
const USER = process.env.FM_USER;
const PASS = process.env.FM_PASSWORD;

if (!USER || !PASS) {
  throw new Error('FM_USER / FM_PASSWORD mancanti — verifica .env');
}

const BASE = `https://${HOST}:${PORT}/fmi/data/v2`;

function basicAuth() {
  return 'Basic ' + Buffer.from(`${USER}:${PASS}`).toString('base64');
}

async function fmRequest(url, { method = 'GET', headers = {}, body, raw = false } = {}) {
  const res = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json', ...headers },
    body: body && typeof body !== 'string' ? JSON.stringify(body) : body,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`FM ${method} ${url} → HTTP ${res.status}: ${text.slice(0, 400)}`);
  }
  if (raw) return res;
  const json = await res.json();
  if (json.messages?.[0]?.code && json.messages[0].code !== '0') {
    throw new Error(`FM error ${json.messages[0].code}: ${json.messages[0].message}`);
  }
  return json;
}

export async function login(database) {
  const url = `${BASE}/databases/${encodeURIComponent(database)}/sessions`;
  const json = await fmRequest(url, {
    method: 'POST',
    headers: { Authorization: basicAuth() },
    body: '{}',
  });
  return json.response.token;
}

export async function logout(database, token) {
  if (!token) return;
  const url = `${BASE}/databases/${encodeURIComponent(database)}/sessions/${token}`;
  try {
    await fmRequest(url, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } });
  } catch {
    // logout failure is non-fatal
  }
}

function bearer(token) {
  return { Authorization: `Bearer ${token}` };
}

function buildQuery(params = {}) {
  const qp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null) continue;
    if (Array.isArray(v) || typeof v === 'object') qp.set(k, JSON.stringify(v));
    else qp.set(k, String(v));
  }
  const s = qp.toString();
  return s ? `?${s}` : '';
}

export async function getRecords(database, token, layout, opts = {}) {
  const qp = buildQuery({
    _limit: opts.limit ?? 100,
    _offset: opts.offset ?? 1,
    _sort: opts.sort,
  });
  const url = `${BASE}/databases/${encodeURIComponent(database)}/layouts/${encodeURIComponent(layout)}/records${qp}`;
  const json = await fmRequest(url, { headers: bearer(token) });
  return json.response;
}

export async function getRecord(database, token, layout, recordId) {
  const url = `${BASE}/databases/${encodeURIComponent(database)}/layouts/${encodeURIComponent(layout)}/records/${recordId}`;
  const json = await fmRequest(url, { headers: bearer(token) });
  return json.response.data?.[0];
}

export async function findRecords(database, token, layout, body) {
  const url = `${BASE}/databases/${encodeURIComponent(database)}/layouts/${encodeURIComponent(layout)}/_find`;
  try {
    const json = await fmRequest(url, {
      method: 'POST',
      headers: bearer(token),
      body,
    });
    return json.response;
  } catch (err) {
    if (String(err.message).includes('FM error 401')) {
      return { data: [], dataInfo: { foundCount: 0, returnedCount: 0 } };
    }
    throw err;
  }
}

export async function downloadContainer(url, token) {
  if (!url) return null;
  const cookies = [];
  let current = url;
  for (let hop = 0; hop < 5; hop++) {
    const headers = { Authorization: `Bearer ${token}` };
    if (cookies.length) headers.Cookie = cookies.join('; ');
    const res = await fetch(current, { headers, redirect: 'manual' });

    const setCookieList = typeof res.headers.getSetCookie === 'function'
      ? res.headers.getSetCookie()
      : (res.headers.get('set-cookie') ? [res.headers.get('set-cookie')] : []);
    for (const sc of setCookieList) {
      const cookiePart = String(sc).split(';')[0];
      if (cookiePart) cookies.push(cookiePart);
    }

    if (res.status >= 200 && res.status < 300) {
      const mime = res.headers.get('content-type') || 'application/octet-stream';
      const buf = Buffer.from(await res.arrayBuffer());
      const base64 = buf.toString('base64');
      return { mime, base64, dataUri: `data:${mime};base64,${base64}` };
    }
    if (res.status >= 300 && res.status < 400) {
      const loc = res.headers.get('location');
      if (!loc) throw new Error(`Container redirect ${res.status} senza Location`);
      current = new URL(loc, current).toString();
      continue;
    }
    throw new Error(`Container HTTP ${res.status} for ${current.slice(0, 120)}`);
  }
  throw new Error('Container: troppi redirect');
}

export async function withSession(database, fn) {
  const token = await login(database);
  try {
    return await fn(token);
  } finally {
    await logout(database, token);
  }
}
