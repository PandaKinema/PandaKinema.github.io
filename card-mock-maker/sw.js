/* カードモックツクール:オフラインでも開けるようにする。
   ふだんはネットの最新版を使い(取れなければ保存しておいた版)、
   バージョンつきの外部ライブラリとフォントは、一度取ったものを使う。 */
const CACHE = "cmm-v2";
const CORE = ["./", "index.html", "app.js", "app.css", "i18n.js", "logo.svg", "manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png"];
const LIBS = [
  "https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js",
  "https://cdn.jsdelivr.net/npm/pdf-lib@1.17.1/dist/pdf-lib.min.js"
];
self.addEventListener("install", e => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    await c.addAll(CORE);
    // 外部のライブラリは取れなくても入れ直しを止めない(次に使ったときに保存する)
    await Promise.all(LIBS.map(u => fetch(u, { mode: "no-cors" }).then(r => c.put(u, r)).catch(() => {})));
    self.skipWaiting();
  })());
});
self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k !== CACHE && k.startsWith("cmm-")) await caches.delete(k);
    await self.clients.claim();
  })());
});
function fromNetwork(req, timeout) {
  return new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error("timeout")), timeout);
    fetch(req).then(r => { clearTimeout(t); resolve(r); }, err => { clearTimeout(t); reject(err); });
  });
}
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  const sameScope = url.origin === location.origin && url.pathname.startsWith(new URL("./", location).pathname);
  const lib = /cdn\.jsdelivr\.net$/.test(url.hostname) || /fonts\.(googleapis|gstatic)\.com$/.test(url.hostname);
  if (!sameScope && !lib) return;
  if (lib) {   // 版の決まったものは保存した版を先に使う
    e.respondWith(caches.open(CACHE).then(async c => {
      const hit = await c.match(req);
      if (hit) return hit;
      const r = await fetch(req); if (r && (r.ok || r.type === "opaque")) c.put(req, r.clone()); return r;
    }));
    return;
  }
  // ツールのファイル:ネット優先(遅いときは4秒で保存した版へ)
  e.respondWith(caches.open(CACHE).then(async c => {
    try {
      const r = await fromNetwork(req, 4000);
      if (r && r.ok) c.put(req, r.clone());
      return r;
    } catch (err) {
      const hit = await c.match(req, { ignoreSearch: true }) || (req.mode === "navigate" ? await c.match("index.html") : null);
      if (hit) return hit;
      throw err;
    }
  }));
});
