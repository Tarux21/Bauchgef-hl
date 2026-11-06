// Offline-Speicher: App-Dateien beim ersten Öffnen ablegen, danach auch ohne Internet starten.
// Bei Änderungen an der App die Versionsnummer erhöhen (auch APP_VERSION in index.html).
const CACHE = "bauchgefuehl-v17";
const FILES = ["./", "index.html", "manifest.webmanifest", "icon.svg", "icon-180.png", "icon-192.png", "icon-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES.map(f => new Request(f, {cache: "reload"})))).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
// Erst Netz (damit Updates ankommen), ohne Netz aus dem Speicher.
// Eigene Dateien immer frisch beim Server nachfragen, nicht aus dem Browser-Zwischenspeicher nehmen.
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  const own = new URL(e.request.url).origin === self.location.origin;
  const req = own ? new Request(e.request, {cache: "no-cache"}) : e.request;
  e.respondWith(
    fetch(req).then(res => {
      if (res.ok || res.type === "opaque") { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
      return res;
    }).catch(() => caches.match(e.request).then(r => r || caches.match("index.html")))
  );
});
