/* テスト版（/card-mock-maker-next/）の役目はおしまい。
   前に登録されたサービスワーカーを外し、テスト版の保存分を消して、正式版へ移す。
   正式版の保存分（cmm-v2 以降）は消さない。 */
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    await caches.delete("cmm-v1");
    await self.registration.unregister();
    for (const c of await self.clients.matchAll({ type: "window" })) {
      c.navigate(c.url.replace("/card-mock-maker-next/", "/card-mock-maker/")).catch(() => {});
    }
  })());
});
