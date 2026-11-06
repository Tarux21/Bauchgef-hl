// Offline-Speicher: App-Dateien beim ersten Öffnen ablegen, danach auch ohne Internet starten.
// Bei Änderungen an der App die Versionsnummer erhöhen (auch APP_VERSION in index.html).
const CACHE = "bauchgefuehl-v19";
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
  const url = new URL(e.request.url);
  const own = url.origin === self.location.origin;
  // Anfragen an den eigenen Erinnerungs-Server (Raspberry Pi) nicht anfassen
  if (!own && !/fonts\.(googleapis|gstatic)\.com$/.test(url.hostname)) return;
  const req = own ? new Request(e.request, {cache: "no-cache"}) : e.request;
  e.respondWith(
    fetch(req).then(res => {
      if (res.ok || res.type === "opaque") { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
      return res;
    }).catch(() => caches.match(e.request).then(r => r || caches.match("index.html")))
  );
});

// Push-Mitteilungen vom Erinnerungs-Server
self.addEventListener("push", e => {
  let d = {};
  try { d = e.data ? e.data.json() : {}; } catch (_) { d = {body: e.data ? e.data.text() : ""}; }
  e.waitUntil(self.registration.showNotification(d.title || "Bauchgefühl", {
    body: d.body || "", tag: d.tag || "bauchgefuehl", icon: "icon-192.png", badge: "icon-192.png", data: {url: d.url || "./?tab=ziel"}
  }));
});
self.addEventListener("notificationclick", e => {
  e.notification.close();
  const target = new URL(e.notification.data && e.notification.data.url || "./?tab=ziel", self.registration.scope).href;
  e.waitUntil(self.clients.matchAll({type: "window", includeUncontrolled: true}).then(list => {
    for (const c of list) { if ("focus" in c) { c.postMessage({tab: "ziel"}); return c.focus(); } }
    return self.clients.openWindow(target);
  }));
});
