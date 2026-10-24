// ビビル文字カード(Xのリンクカード用)
//   /m/<p>      Xが読みに来るページ。人が開くとジェネレーターのお題ページへ移動
//   /i/<p>.png  カード画像(1200×630)。<p> はジェネレーターの共有URL「#p=」のあとと同じ
// カードの下地は GitHub の bibilu-moji/share/card-base.bin(差し替えればデザインを変えられます)
const SITE = "https://pandakinema.github.io/bibilu-moji/";
const BASE_URL = "https://pandakinema.github.io/bibilu-moji/share/card-base.bin";
const TITLE = "このビビル文字、よめる？";
const DESC = "ビビル文字ジェネレーターでつくった、なぞのメッセージ。こたえはリンクの先で！";

const W = 1200, H = 630, BAND = 122, AREA_X = 106, AREA_W = 988, PAD_Y = 44;
const GLYPH = 7, GAP = 1, MAX = 6, WHITE = 255, MAX_TEXT = 120;

const URL_CHARS = Array.from(new Set([
  ..."あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん",
  ..."がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ",
  ..."0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",
  ..."？！ー 　\n"
]));
const GLYPHS = {"0":[127,65,77,73,89,65,127],"1":[125,5,117,21,85,20,119],"2":[127,1,93,81,23,80,95],"3":[127,1,93,1,93,1,127],"4":[85,85,84,85,65,117,85],"5":[127,64,93,69,117,5,125],"6":[125,65,93,68,85,5,125],"7":[95,81,85,93,65,29,85],"8":[127,64,93,65,93,1,127],"9":[95,80,85,17,93,65,95],"び":[85,85,85,80,95,64,127],"る":[85,85,85,85,85,20,119],"れ":[85,84,87,80,95,64,127],"ら":[127,0,127,1,125,5,117],"た":[127,65,95,1,125,5,117],"て":[127,0,127,8,107,42,107],"つ":[85,85,85,5,125,1,127],"づ":[85,85,80,5,125,1,127],"か":[87,16,127,17,85,85,85],"き":[107,8,127,8,127,8,107],"う":[85,20,127,65,93,21,117],"み":[119,16,95,64,127,0,127],"わ":[127,65,93,5,117,21,85],"い":[125,1,127,8,107,74,107],"そ":[125,1,93,69,93,1,127],"お":[107,8,127,8,123,9,107],"し":[125,1,125,5,117,1,127],"ね":[107,8,127,1,127,10,107],"む":[85,84,87,80,93,65,127],"さ":[85,20,127,20,117,5,125],"に":[95,64,95,65,95,64,111],"く":[127,65,93,21,85,85,85],"り":[85,21,117,5,117,17,87],"せ":[85,20,127,20,23,80,95],"ど":[85,80,95,64,95,80,87],"ほ":[107,8,127,8,107,42,107],"ん":[125,1,117,85,93,1,127],"で":[117,0,127,8,107,42,107],"あ":[127,1,125,5,125,64,95],"や":[83,16,127,17,20,87,85],"こ":[127,1,125,5,125,1,127],"ち":[125,1,127,8,127,8,107],"え":[119,20,85,85,85,20,119],"け":[65,127,68,21,117,5,125],"す":[127,1,125,65,95,20,119],"と":[87,80,95,64,95,80,87],"な":[117,4,127,4,117,5,125],"は":[85,85,85,20,119,0,119],"ぬ":[127,1,93,69,95,20,119],"の":[85,21,117,5,125,1,127],"ひ":[87,84,87,80,95,64,127],"ふ":[127,1,125,5,117,21,85],"へ":[125,69,85,84,87,81,93],"ま":[127,1,125,65,127,64,95],"め":[119,21,84,31,84,69,125],"を":[107,8,127,8,123,10,107],"も":[127,8,127,8,107,40,111],"ゆ":[125,5,117,21,117,4,127],"よ":[127,1,125,1,125,1,127],"ろ":[127,65,93,85,93,65,127],"ぴ":[85,85,87,80,95,64,127],"ば":[85,84,85,20,119,0,119],"ぶ":[117,0,125,5,117,21,85],"！":[93,85,85,20,85,65,85],"？":[127,65,93,81,23,84,85],"ー":[127,64,1,127,64,1,127],"ぱ":[85,87,84,20,119,0,119],"べ":[125,68,85,84,87,81,93],"ぼ":[109,8,127,8,107,42,107],"だ":[117,64,95,1,125,5,117],"ぢ":[117,0,127,8,127,8,107],"ぷ":[117,7,124,5,117,21,85],"ぺ":[117,71,81,84,87,81,93],"ぽ":[105,8,127,8,107,42,107],"が":[85,16,127,17,85,85,85],"ぎ":[109,8,127,8,127,8,107],"ぐ":[117,64,93,21,85,85,85],"げ":[69,127,68,21,117,5,125],"ご":[117,0,125,5,125,1,127],"ざ":[85,16,127,20,117,5,125],"じ":[117,0,125,5,117,1,127],"ず":[117,0,125,65,95,20,119],"ぜ":[85,16,127,20,23,80,95],"ぞ":[117,0,93,69,93,1,127],"A":[127,65,73,93,65,93,85],"C":[95,81,84,87,20,81,95],"D":[127,1,109,41,109,1,127],"B":[127,1,109,33,109,1,127],"E":[127,64,95,64,95,64,127],"F":[127,64,95,64,95,80,87],"G":[95,80,87,20,86,80,95],"H":[85,20,93,65,93,20,85],"I":[85,20,127,0,93,85,85],"J":[85,7,117,5,125,1,127],"K":[85,85,85,68,93,69,85],"L":[85,85,85,84,87,80,95],"M":[127,73,8,73,93,65,119],"N":[117,85,85,84,85,85,93],"O":[127,65,93,85,85,65,127],"P":[125,68,85,65,95,80,87],"Q":[95,17,85,69,93,20,87],"R":[127,64,93,69,85,85,85],"S":[127,64,95,65,125,1,127],"T":[127,8,107,42,107,8,107],"U":[85,85,85,85,93,65,127],"V":[85,85,85,73,42,34,119],"W":[119,65,28,73,73,73,127],"X":[127,8,107,34,107,8,127],"Y":[85,93,65,119,20,85,93],"Z":[95,0,125,65,95,0,125]};

const pipe = async (bytes, stream) => new Uint8Array(await new Response(new Response(bytes).body.pipeThrough(stream)).arrayBuffer());

let BASE = null;
async function base() {
  if (BASE) return BASE;
  const r = await fetch(BASE_URL, { cf: { cacheTtl: 3600 } });
  if (!r.ok) throw new Error("base " + r.status);
  const buf = new Uint8Array(await r.arrayBuffer());
  BASE = { plte: buf.slice(0, 768), px: await pipe(buf.subarray(768), new DecompressionStream("deflate")) };
  return BASE;
}

function unpack(p) {
  if (!/^[A-Za-z0-9_-]{1,220}$/.test(p)) return "";
  try {
    let s = p.replace(/-/g, "+").replace(/_/g, "/");
    while (s.length % 4) s += "=";
    const bin = atob(s);
    let out = "";
    for (let i = 0; i < bin.length; i++) {
      const ch = URL_CHARS[bin.charCodeAt(i)];
      if (ch === undefined) return "";
      out += ch;
    }
    return Array.from(out).length <= MAX_TEXT ? out : "";
  } catch { return ""; }
}

function linesFor(s) {
  const out = [];
  for (const src of s.split("\n").map(l => Array.from(l))) {
    if (!src.length) { out.push([]); continue; }
    for (let i = 0; i < src.length; i += MAX) out.push(src.slice(i, i + MAX));
  }
  return out.length ? out : [[]];
}

const CRC = (() => { const t = new Int32Array(256); for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c; } return t; })();
function crc32(b) { let c = -1; for (let i = 0; i < b.length; i++) c = CRC[(c ^ b[i]) & 255] ^ (c >>> 8); return (c ^ -1) >>> 0; }
function chunk(type, data) {
  const out = new Uint8Array(12 + data.length), dv = new DataView(out.buffer);
  dv.setUint32(0, data.length);
  for (let i = 0; i < 4; i++) out[4 + i] = type.charCodeAt(i);
  out.set(data, 8);
  dv.setUint32(8 + data.length, crc32(out.subarray(4, 8 + data.length)));
  return out;
}
function concat(parts) { const o = new Uint8Array(parts.reduce((a, p) => a + p.length, 0)); let i = 0; for (const p of parts) { o.set(p, i); i += p.length; } return o; }

async function render(text) {
  const { plte, px: src } = await base();
  const lines = linesFor(text);
  const cols = Math.max(1, ...lines.map(l => l.length));
  const u = Math.max(2, Math.min(
    Math.floor(AREA_W / (cols * GLYPH + (cols - 1) * GAP)),
    Math.floor((H - BAND * 2 - PAD_Y * 2) / (lines.length * GLYPH + (lines.length - 1) * GAP))
  ));
  const textH = lines.length * GLYPH * u + (lines.length - 1) * GAP * u;
  const y0 = Math.round(BAND + (H - BAND * 2 - textH) / 2);
  // 1行ごとに先頭へフィルタ番号(0)を付けた形で、下地をコピーしてから文字を塗る
  const raw = new Uint8Array(H * (W + 1));
  for (let y = 0; y < H; y++) raw.set(src.subarray(y * W, y * W + W), y * (W + 1) + 1);
  lines.forEach((line, li) => {
    const lw = line.length ? line.length * GLYPH * u + (line.length - 1) * GAP * u : 0;
    let x = Math.round(AREA_X + (AREA_W - lw) / 2);
    const y = y0 + li * (GLYPH + GAP) * u;
    for (const ch of line) {
      const g = GLYPHS[ch];
      if (g) for (let r = 0; r < GLYPH; r++) for (let c = 0; c < GLYPH; c++) {
        if (!(g[r] >> (GLYPH - 1 - c) & 1)) continue;
        for (let yy = y + r * u, ye = yy + u; yy < ye; yy++) { const o = yy * (W + 1) + 1 + x + c * u; raw.fill(WHITE, o, o + u); }
      }
      x += (GLYPH + GAP) * u;
    }
  });
  const ihdr = new Uint8Array(13), dv = new DataView(ihdr.buffer);
  dv.setUint32(0, W); dv.setUint32(4, H); ihdr[8] = 8; ihdr[9] = 3;
  return concat([
    new Uint8Array([137, 80, 78, 71, 13, 10, 26, 10]),
    chunk("IHDR", ihdr), chunk("PLTE", plte),
    chunk("IDAT", await pipe(raw, new CompressionStream("deflate"))),
    chunk("IEND", new Uint8Array(0)),
  ]);
}

const esc = s => s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

function page(origin, p) {
  const target = SITE + "#p=" + p, img = `${origin}/i/${p}.png`;
  return `<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(TITLE)}</title>
<meta name="robots" content="noindex">
<meta property="og:type" content="website">
<meta property="og:site_name" content="PANDA KINEMA">
<meta property="og:title" content="${esc(TITLE)}">
<meta property="og:description" content="${esc(DESC)}">
<meta property="og:url" content="${esc(origin + "/m/" + p)}">
<meta property="og:image" content="${esc(img)}">
<meta property="og:image:width" content="${W}"><meta property="og:image:height" content="${H}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="${esc(img)}">
<style>body{margin:0;background:#fef4d6;color:#173f53;font-family:sans-serif;display:grid;place-items:center;min-height:100vh}a{color:inherit}</style>
</head><body><a href="${esc(target)}">こたえを見に行く</a>
<script>location.replace(${JSON.stringify(target)})</script></body></html>`;
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const m = url.pathname.match(/^\/(m|i)\/([A-Za-z0-9_-]+?)(\.png)?$/);
    if (!m || !unpack(m[2])) return Response.redirect(SITE, 302);
    if (m[1] === "m") {
      return new Response(page(url.origin, m[2]), { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=3600" } });
    }
    return new Response(await render(unpack(m[2])), {
      headers: { "content-type": "image/png", "cache-control": "public, max-age=31536000, immutable" },
    });
  },
};
