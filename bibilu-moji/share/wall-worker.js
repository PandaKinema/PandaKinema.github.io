// みんなの碑文(ビビル文字ジェネレータの壁) ― Cloudflare Workers + D1 の1ファイル
//   GET  /wall?before=<番号>   新しい順に30件 {items:[{id,p}], more, total}
//   POST /wall  {"p":"..."}    碑文を刻む。p はジェネレータの共有URL「#p=」のあとと同じ文字列
//   POST /hide  {"id":番号}    管理者が非表示にする(ヘッダー X-Admin-Key に管理キー)
// Cloudflare 側の設定:D1 データベースを「DB」という名前でバインド/秘密の変数「ADMIN_KEY」に管理キー
// 表(wall)は最初のアクセスで自動で作られます。消した碑文は D1 の画面で hidden を 0 に戻すと復活します。
const ORIGINS = ["https://pandakinema.com", "https://www.pandakinema.com", "https://pandakinema.github.io"];
const PAGE = 30;          // 1回に読む数
const MAX_CHARS = 36;     // 刻める文字数(空白・改行は数えない)
const MAX_LINES = 6;      // 刻める行数(6文字ごとの折り返しを含む)
const GAP_SEC = 20;       // 同じ人が続けて刻めるまでの秒数
const DAY_MAX = 30;       // 同じ人が1日に刻める数
// 刻めない言葉(空白・改行・ーを抜いてから調べます)。足すときは /ことば/ の形で
const NG = [
  /しね(?!ま)/, /しんで(?!れら)/, /ころす/, /ころせ/, /ころし/, /きえろ/, /きもい/, /きしよい/, /うざい/, /ぶす/,
  /がいじ/, /きちがい/, /つんぼ/, /めくら/, /かたわ(?!ら)/,
  /ちんこ/, /ちんぽ/, /まんこ/, /おつぱい/, /せつくす/, /えつち/, /れいぷ/, /ちかん/, /やらせろ/,
  /FUCK/, /SHIT/, /BITCH/, /PUSSY/, /PENIS/, /SEX/, /PORN/, /NIGG/, /KILLYOU/,
  /[0-9]{7,}/,
];

const URL_CHARS = Array.from(new Set([
  ..."あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん",
  ..."がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ",
  ..."0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",
  ..."？！ー 　\n"
]));

function unpack(p) {
  if (typeof p !== "string" || !/^[A-Za-z0-9_-]{1,200}$/.test(p)) return null;
  try {
    let s = p.replace(/-/g, "+").replace(/_/g, "/");
    while (s.length % 4) s += "=";
    const bin = atob(s);
    let out = "";
    for (let i = 0; i < bin.length; i++) {
      const ch = URL_CHARS[bin.charCodeAt(i)];
      if (ch === undefined) return null;
      out += ch;
    }
    return out;
  } catch { return null; }
}
function pack(s) {
  let bin = "";
  for (const ch of Array.from(s)) bin += String.fromCharCode(URL_CHARS.indexOf(ch));
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
// ジェネレータと同じ形にそろえる:全角空白→半角、行末の空白と空行の連続を整理
function tidy(t) {
  return t.replace(/　/g, " ").split("\n").map(l => l.replace(/\s+$/, "")).join("\n")
    .replace(/\n{3,}/g, "\n\n").replace(/^\n+|\n+$/g, "");
}
function lineCount(t) {
  return t.split("\n").reduce((n, l) => n + Math.max(1, Math.ceil(Array.from(l).length / 6)), 0);
}

const json = (body, status, origin, extra) => new Response(status === 204 ? null : JSON.stringify(body), {
  status: status || 200,
  headers: Object.assign({
    "content-type": "application/json; charset=utf-8",
    "access-control-allow-origin": origin || ORIGINS[0],
    "access-control-allow-methods": "GET, POST, OPTIONS",
    "access-control-allow-headers": "content-type, x-admin-key",
    "vary": "origin",
  }, extra || {}),
});
const fail = (msg, status, origin) => json({ ok: false, error: msg }, status || 400, origin);

function allowed(origin) {
  return ORIGINS.includes(origin) || /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin || "");
}

let ready = null;
function init(db) {
  if (!ready) ready = db.batch([
    db.prepare("CREATE TABLE IF NOT EXISTS wall (id INTEGER PRIMARY KEY AUTOINCREMENT, p TEXT NOT NULL, created INTEGER NOT NULL, ip TEXT NOT NULL DEFAULT '', hidden INTEGER NOT NULL DEFAULT 0)"),
    db.prepare("CREATE INDEX IF NOT EXISTS wall_list ON wall (hidden, id)"),
    db.prepare("CREATE INDEX IF NOT EXISTS wall_ip ON wall (ip, created)"),
  ]).catch(e => { ready = null; throw e; });
  return ready;
}

async function who(request) {
  const ip = request.headers.get("cf-connecting-ip") || "local";
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode("bibilu-wall:" + ip));
  return Array.from(new Uint8Array(d).slice(0, 8), b => b.toString(16).padStart(2, "0")).join("");
}

function same(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let x = 0;
  for (let i = 0; i < a.length; i++) x |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return x === 0;
}

async function list(db, url, origin) {
  const before = parseInt(url.searchParams.get("before") || "0", 10);
  const q = before > 0
    ? db.prepare("SELECT id, p FROM wall WHERE hidden = 0 AND id < ? ORDER BY id DESC LIMIT ?").bind(before, PAGE + 1)
    : db.prepare("SELECT id, p FROM wall WHERE hidden = 0 ORDER BY id DESC LIMIT ?").bind(PAGE + 1);
  const [rows, count] = await db.batch([q, db.prepare("SELECT COUNT(*) AS n FROM wall WHERE hidden = 0")]);
  const items = rows.results.slice(0, PAGE);
  return json({ ok: true, items, more: rows.results.length > PAGE, total: count.results[0].n }, 200, origin, { "cache-control": "public, max-age=10" });
}

async function carve(db, request, origin) {
  let body;
  try { body = await request.json(); } catch { return fail("送りかたがちがいます", 400, origin); }
  const raw = unpack(body && body.p);
  if (raw === null) return fail("ビビル文字にない文字は刻めません", 400, origin);
  const text = tidy(raw);
  const plain = text.replace(/[ \n]/g, "");
  if (!plain) return fail("ことばを入れてから刻んでください", 400, origin);
  if (Array.from(plain).length > MAX_CHARS || lineCount(text) > MAX_LINES)
    return fail("刻めるのは" + MAX_LINES + "行・" + MAX_CHARS + "文字までです", 400, origin);
  const probe = plain.replace(/ー/g, "");
  if (NG.some(r => r.test(probe))) return fail("その言葉は刻めません", 400, origin);
  const p = pack(text);
  const ip = await who(request);
  const now = Math.floor(Date.now() / 1000);
  const [last, day, dup] = await db.batch([
    db.prepare("SELECT created FROM wall WHERE ip = ? ORDER BY created DESC LIMIT 1").bind(ip),
    db.prepare("SELECT COUNT(*) AS n FROM wall WHERE ip = ? AND created > ?").bind(ip, now - 86400),
    db.prepare("SELECT id FROM wall WHERE ip = ? AND p = ? LIMIT 1").bind(ip, p),
  ]);
  if (dup.results.length) return fail("同じ碑文はもう刻まれています", 409, origin);
  if (last.results.length && now - last.results[0].created < GAP_SEC) return fail("少し時間をおいてから刻んでください", 429, origin);
  if (day.results[0].n >= DAY_MAX) return fail("今日はもう刻めません。また明日どうぞ", 429, origin);
  const r = await db.prepare("INSERT INTO wall (p, created, ip) VALUES (?, ?, ?)").bind(p, now, ip).run();
  return json({ ok: true, item: { id: r.meta.last_row_id, p } }, 200, origin);
}

async function hide(db, request, env, origin) {
  if (!env.ADMIN_KEY) return fail("管理キーがまだ設定されていません", 403, origin);
  if (!same(request.headers.get("x-admin-key") || "", env.ADMIN_KEY)) return fail("管理キーがちがいます", 403, origin);
  let body;
  try { body = await request.json(); } catch { return fail("送りかたがちがいます", 400, origin); }
  const id = parseInt(body && body.id, 10);
  if (!(id > 0)) return fail("番号がちがいます", 400, origin);
  await db.prepare("UPDATE wall SET hidden = 1 WHERE id = ?").bind(id).run();
  return json({ ok: true }, 200, origin);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const reqOrigin = request.headers.get("origin");
    const origin = allowed(reqOrigin) ? reqOrigin : ORIGINS[0];
    if (request.method === "OPTIONS") return json({ ok: true }, 204, origin);
    if (!env.DB) return fail("データベースがつながっていません", 500, origin);
    try {
      await init(env.DB);
      if (url.pathname === "/wall" && request.method === "GET") return await list(env.DB, url, origin);
      if (request.method === "POST" && reqOrigin && !allowed(reqOrigin)) return fail("このページからは刻めません", 403, origin);
      if (url.pathname === "/wall" && request.method === "POST") return await carve(env.DB, request, origin);
      if (url.pathname === "/hide" && request.method === "POST") return await hide(env.DB, request, env, origin);
      return fail("見つかりません", 404, origin);
    } catch (e) {
      return fail("うまくいきませんでした。時間をおいてもう一度どうぞ", 500, origin);
    }
  },
};
