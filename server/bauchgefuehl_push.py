#!/usr/bin/env python3
"""
Bauchgefühl Erinnerungs-Server (für den Raspberry Pi)

Schickt Push-Mitteilungen an die Bauchgefühl-App auf dem iPhone:
- Nahrungsergänzungen zur eingestellten Tageszeit, nur wenn noch nicht abgehakt
- Trink-Erinnerungen, nur wenn man hinter dem Tagesplan liegt

Die App meldet ihre Einstellungen und den Tagesstand (Haken, Gläser) an diesen Server.
Erreichbar ist er nur im eigenen Tailscale-Netz (über `tailscale serve`).

Start:  python3 bauchgefuehl_push.py            (Port 8787, Daten in ./data)
Test:   python3 bauchgefuehl_push.py --selftest (prüft die Logik ohne echte Mitteilungen)
"""
import json, os, sys, threading, time, argparse, logging
from datetime import datetime, date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from zoneinfo import ZoneInfo

APP_ORIGIN = os.environ.get("BG_APP_ORIGIN", "https://tarux21.github.io")
PORT = int(os.environ.get("BG_PORT", "8787"))
DATA_DIR = os.environ.get("BG_DATA", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
# Kontaktangabe für Apple/Google (muss eine gültige https- oder mailto-Adresse sein)
CONTACT = os.environ.get("BG_CONTACT", "https://tarux21.github.io")
TZ = ZoneInfo(os.environ.get("BG_TZ", "Europe/Berlin"))
GLASS_L = 0.25
DEFAULTS = {
    "times": {"morgens": "08:30", "mittags": "13:00", "abends": "19:30"},
    "waterTimes": ["11:00", "14:00", "17:00"],
    "waterOn": True,
    "quietAfter": "21:00",
    "apptReminder": "18:00",
    "waterGoal": 6,
    "supps": [],
}
log = logging.getLogger("bauchgefuehl")
lock = threading.Lock()


# ---------------------------------------------------------------- Speicher
def path(name): return os.path.join(DATA_DIR, name)

def load(name, default):
    try:
        with open(path(name), encoding="utf-8") as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return default

def store(name, obj):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = path(name) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path(name))


# ---------------------------------------------------------------- VAPID-Schlüssel
def vapid():
    """Erzeugt beim ersten Start ein Schlüsselpaar und speichert es in data/."""
    keys = load("vapid.json", None)
    if keys: return keys
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization
    import base64
    k = ec.generate_private_key(ec.SECP256R1())
    priv = k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()
    pub = k.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    keys = {"private_pem": priv, "public": base64.urlsafe_b64encode(pub).rstrip(b"=").decode()}
    store("vapid.json", keys)
    os.chmod(path("vapid.json"), 0o600)
    log.info("Neues VAPID-Schlüsselpaar erzeugt")
    return keys


# ---------------------------------------------------------------- Senden
def signing_key():
    """Privater Schlüssel als Vapid-Objekt. pywebpush versteht PEM als Text nicht, deshalb hier laden."""
    from py_vapid import Vapid
    return Vapid.from_pem(vapid()["private_pem"].encode())

def send(sub, title, body, tag="bauchgefuehl"):
    """Schickt eine Mitteilung. Gibt False zurück, wenn das Abo nicht mehr gilt."""
    from pywebpush import webpush, WebPushException
    payload = json.dumps({"title": title, "body": body, "tag": tag, "url": "./?tab=ziel"}, ensure_ascii=False)
    try:
        webpush(subscription_info=sub, data=payload, vapid_private_key=signing_key(),
                vapid_claims={"sub": CONTACT}, ttl=3600)
        log.info("Gesendet: %s – %s", title, body)
        return True
    except WebPushException as e:
        code = getattr(e.response, "status_code", None)
        log.warning("Senden fehlgeschlagen (%s): %s %s", code, e, getattr(e.response, "text", "")[:200])
        return code not in (404, 410)
    except Exception:
        log.exception("Senden fehlgeschlagen")
        return True


# ---------------------------------------------------------------- Logik
def hm(s):
    h, m = s.split(":"); return int(h) * 60 + int(m)

def fmt_l(glasses): return f"{glasses * GLASS_L:.2f}".rstrip("0").rstrip(".").replace(".", ",")

TXT = {
    "de": {"and": " und ", "supp": "Zeit für {} 💊", "supp_body": "Kurz abhaken, dann ist der lila Ring voller.",
           "appt": "Morgen: {}", "appt_at": " um {} Uhr", "appt_body": "Unterlagen einpacken und Fragen notieren.",
           "water": "Trinkpause 💧", "water_body": "{} von {} l geschafft. Ein Glas Wasser tut dir und dem Baby gut.",
           "test": "Die Erinnerungen sind eingerichtet. So sieht eine Mitteilung aus."},
    "fr": {"and": " et ", "supp": "C'est l'heure : {} 💊", "supp_body": "Coche-le vite, et l'anneau violet se remplit.",
           "appt": "Demain : {}", "appt_at": " à {}", "appt_body": "Prends ton dossier et note tes questions.",
           "water": "Pause hydratation 💧", "water_body": "{} l sur {} l bus. Un verre d'eau fait du bien à toi et au bébé.",
           "test": "Les rappels sont activés. Voici à quoi ressemble une notification."},
}

def txt(cfg): return TXT.get(cfg.get("lang"), TXT["de"])

def due_messages(dev, now):
    """Welche Mitteilungen sind für dieses Gerät jetzt (diese Minute) fällig?"""
    cfg = {**DEFAULTS, **dev.get("settings", {})}
    today = now.date().isoformat()
    st = dev.get("status", {})
    if st.get("date") != today: st = {"date": today, "water": 0, "taken": []}
    taken = set(st.get("taken", []))
    minute = now.hour * 60 + now.minute
    if minute >= hm(cfg["quietAfter"]): return []
    out = []
    T = txt(cfg)
    # Nahrungsergänzungen je Tageszeit
    for slot, t in cfg["times"].items():
        if t and hm(t) == minute:
            open_s = [s for s in cfg["supps"] if s.get("time") == slot and s["name"] not in taken]
            if open_s:
                labels = [s.get("label") or s["name"] for s in open_s]
                names = T["and"].join([", ".join(labels[:-1]), labels[-1]] if len(labels) > 1 else labels)
                hint = next((s.get("hint") for s in open_s if s.get("hint")), "")
                out.append((T["supp"].format(names), hint or T["supp_body"], "supp-" + slot))
    # Eigene Termine: Erinnerung am Vortag
    if cfg.get("apptReminder") and hm(cfg["apptReminder"]) == minute:
        tomorrow = (now.date() + timedelta(days=1)).isoformat()
        for a in cfg.get("appts", []):
            if a.get("date") == tomorrow:
                out.append((T["appt"].format(a["title"]) + (T["appt_at"].format(a["time"]) if a.get("time") else "") + " 📅",
                            T["appt_body"], "appt-" + a["date"] + a.get("time", "")))
    # Trinken: nur wenn hinter dem Plan (gleichmäßig verteilt von 8 bis 20 Uhr)
    if cfg.get("waterOn"):
        goal = int(cfg.get("waterGoal") or 6)
        for t in cfg["waterTimes"]:
            if t and hm(t) == minute:
                expected = round(goal * max(0, min(1, (minute - 8 * 60) / (12 * 60))))
                have = int(st.get("water", 0))
                if have < expected:
                    out.append((T["water"], T["water_body"].format(fmt_l(have), fmt_l(goal)), "water"))
    return out

def tick(now=None, sender=send):
    now = now or datetime.now(TZ)
    with lock:
        devs = load("devices.json", {})
        sent_log = load("sent.json", {})
        key_min = now.strftime("%Y-%m-%d %H:%M")
        changed = False
        for dev_id, dev in list(devs.items()):
            for title, body, tag in due_messages(dev, now):
                k = f"{dev_id}|{key_min}|{tag}"
                if k in sent_log: continue
                ok = sender(dev["subscription"], title, body, tag)
                sent_log[k] = 1
                if not ok:
                    log.info("Abo von %s ungültig, entfernt", dev_id); devs.pop(dev_id, None); changed = True; break
        cutoff = (now - timedelta(days=2)).strftime("%Y-%m-%d")
        sent_log = {k: v for k, v in sent_log.items() if k.split("|")[1] >= cutoff}
        store("sent.json", sent_log)
        if changed: store("devices.json", devs)

def scheduler():
    while True:
        try: tick()
        except Exception: log.exception("Fehler im Zeitplan")
        time.sleep(60 - datetime.now().second + 1)


# ---------------------------------------------------------------- HTTP
def clean_settings(s):
    out = {}
    times = s.get("times", {})
    out["times"] = {k: (times.get(k) if isinstance(times.get(k), str) and len(times.get(k)) == 5 else "") for k in ("morgens", "mittags", "abends")}
    out["waterTimes"] = [t for t in s.get("waterTimes", []) if isinstance(t, str) and len(t) == 5][:8]
    out["waterOn"] = bool(s.get("waterOn", True))
    out["waterGoal"] = max(4, min(12, int(s.get("waterGoal", 6))))
    out["appts"] = [{"title": str(a.get("title", ""))[:80], "date": str(a.get("date", ""))[:10], "time": str(a.get("time", ""))[:5]}
                     for a in s.get("appts", []) if isinstance(a, dict) and a.get("title") and len(str(a.get("date", ""))) == 10][:50]
    out["lang"] = "fr" if s.get("lang") == "fr" else "de"
    out["supps"] = [{"name": str(x.get("name", ""))[:60], "label": str(x.get("label") or x.get("name", ""))[:60], "time": x.get("time") if x.get("time") in ("morgens", "mittags", "abends") else "morgens", "hint": str(x.get("hint", ""))[:120]}
                    for x in s.get("supps", []) if isinstance(x, dict) and x.get("name")][:20]
    return out

class Handler(BaseHTTPRequestHandler):
    server_version = "Bauchgefuehl/1"
    def log_message(self, fmt, *args): log.debug("%s %s", self.address_string(), fmt % args)
    def cors(self):
        self.send_header("Access-Control-Allow-Origin", APP_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "86400")
    def reply(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code); self.cors()
        self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)
    def do_OPTIONS(self):
        self.send_response(204); self.cors(); self.end_headers()
    def read(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 64_000: raise ValueError("zu groß")
        return json.loads(self.rfile.read(n) or b"{}")
    def do_GET(self):
        if self.path == "/api/key": return self.reply(200, {"publicKey": vapid()["public"]})
        if self.path == "/api/health":
            devs = load("devices.json", {})
            return self.reply(200, {"ok": True, "devices": len(devs), "time": datetime.now(TZ).strftime("%Y-%m-%d %H:%M")})
        self.reply(404, {"error": "unbekannt"})
    def do_POST(self):
        try: data = self.read()
        except Exception: return self.reply(400, {"error": "ungültige Daten"})
        dev_id = str(data.get("device", ""))[:64]
        if not dev_id: return self.reply(400, {"error": "Gerät fehlt"})
        with lock:
            devs = load("devices.json", {})
            if self.path == "/api/subscribe":
                sub = data.get("subscription")
                if not (isinstance(sub, dict) and str(sub.get("endpoint", "")).startswith("https://")):
                    return self.reply(400, {"error": "Abo fehlt"})
                devs[dev_id] = {**devs.get(dev_id, {}), "subscription": sub, "settings": clean_settings(data.get("settings", {}))}
                store("devices.json", devs); log.info("Gerät verbunden: %s", dev_id)
                return self.reply(200, {"ok": True})
            if dev_id not in devs: return self.reply(404, {"error": "Gerät nicht verbunden"})
            if self.path == "/api/settings":
                devs[dev_id]["settings"] = clean_settings(data.get("settings", {})); store("devices.json", devs)
                return self.reply(200, {"ok": True})
            if self.path == "/api/status":
                devs[dev_id]["status"] = {"date": str(data.get("date", ""))[:10], "water": int(data.get("water", 0)), "taken": [str(x)[:60] for x in data.get("taken", [])][:20]}
                store("devices.json", devs); return self.reply(200, {"ok": True})
            if self.path == "/api/test":
                sub = devs[dev_id]["subscription"]; T = txt(devs[dev_id].get("settings", {}))
        if self.path == "/api/test":
            ok = send(sub, "Bauchgefühl 💜", T["test"], "test")
            return self.reply(200 if ok else 410, {"ok": ok})
        if self.path == "/api/unsubscribe":
            with lock:
                devs = load("devices.json", {}); devs.pop(dev_id, None); store("devices.json", devs)
            return self.reply(200, {"ok": True})
        self.reply(404, {"error": "unbekannt"})


# ---------------------------------------------------------------- Selbsttest
def datetime_shift(dev):
    d = json.loads(json.dumps(dev)); d["settings"]["appts"][0]["date"] = "2026-11-09"; return d

def real_send_check():
    """Prüft alles bis kurz vor dem Versand: Schlüssel laden, JWT signieren, Inhalt für ein Test-Abo verschlüsseln."""
    try:
        import base64, os as _os
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives import serialization
        from pywebpush import WebPusher
        b64 = lambda x: base64.urlsafe_b64encode(x).rstrip(b"=").decode()
        client = ec.generate_private_key(ec.SECP256R1()).public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
        sub = {"endpoint": "https://web.push.apple.com/test", "keys": {"p256dh": b64(client), "auth": b64(_os.urandom(16))}}
        hdr = signing_key().sign({"sub": CONTACT, "aud": "https://web.push.apple.com"})
        enc = WebPusher(sub).encode(json.dumps({"title": "Test"}).encode(), "aes128gcm")
        return hdr.get("Authorization", "").startswith("vapid t=") and len(enc["body"]) > 0
    except Exception as e:
        print("   ", type(e).__name__, e)
        return False

def selftest():
    sent = []
    fake = lambda sub, t, b, tag: sent.append((t, b)) or True
    dev = {"subscription": {"endpoint": "https://example"}, "settings": clean_settings({
        "times": {"morgens": "08:30", "mittags": "", "abends": "19:30"}, "waterTimes": ["11:00", "17:00"], "waterGoal": 6,
        "supps": [{"name": "Folsäure", "time": "morgens"}, {"name": "Jod", "time": "morgens"}, {"name": "Eisen", "time": "abends", "hint": "Nicht mit Kaffee."}]})}
    d = date(2026, 11, 7)
    at = lambda h, m: datetime(d.year, d.month, d.day, h, m, tzinfo=TZ)
    checks = []
    dev["status"] = {"date": d.isoformat(), "water": 0, "taken": []}
    checks.append(("8:30 beide offen", [t for t, _, _ in due_messages(dev, at(8, 30))] == ["Zeit für Folsäure und Jod 💊"]))
    dev["status"]["taken"] = ["Folsäure"]
    checks.append(("8:30 nur Jod offen", [t for t, _, _ in due_messages(dev, at(8, 30))] == ["Zeit für Jod 💊"]))
    dev["status"]["taken"] = ["Folsäure", "Jod"]
    checks.append(("8:30 alles genommen", due_messages(dev, at(8, 30)) == []))
    checks.append(("8:31 nichts fällig", due_messages(dev, at(8, 31)) == []))
    checks.append(("19:30 Eisen mit Hinweis", [(t, b) for t, b, _ in due_messages(dev, at(19, 30))] == [("Zeit für Eisen 💊", "Nicht mit Kaffee.")]))
    dev["status"]["water"] = 1
    checks.append(("11:00 hinter Plan (1 von 2)", [t for t, _, _ in due_messages(dev, at(11, 0))] == ["Trinkpause 💧"]))
    dev["status"]["water"] = 2
    checks.append(("11:00 im Plan", due_messages(dev, at(11, 0)) == []))
    dev["status"] = {"date": "2026-11-06", "water": 6, "taken": ["Folsäure", "Jod", "Eisen"]}
    checks.append(("neuer Tag: Stand von gestern zählt nicht", len(due_messages(dev, at(8, 30))) == 1))
    dev["settings"]["quietAfter"] = "19:00"
    checks.append(("Ruhezeit ab 19 Uhr", due_messages(dev, at(19, 30)) == []))
    dev["settings"]["quietAfter"] = "21:00"
    dev["settings"]["appts"] = clean_settings({"appts": [{"title": "Frauenarzt", "date": "2026-11-08", "time": "09:30"}]})["appts"]
    checks.append(("Termin am Vortag 18 Uhr", [t for t, _, _ in due_messages(dev, at(18, 0))] == ["Morgen: Frauenarzt um 09:30 Uhr 📅"]))
    checks.append(("Termin nicht zwei Tage vorher", due_messages(datetime_shift(dev), at(18, 0)) == []))
    fr = json.loads(json.dumps(dev)); fr["settings"] = {**fr["settings"], **clean_settings({"lang": "fr", "times": fr["settings"]["times"], "waterTimes": ["11:00"], "appts": fr["settings"]["appts"],
        "supps": [{"name": "Folsäure", "label": "Acide folique", "time": "morgens"}, {"name": "Jod", "label": "Iode", "time": "morgens"}]})}
    fr["status"] = {"date": d.isoformat(), "water": 0, "taken": ["Jod"]}
    checks.append(("Französisch: Supplement", [t for t, _, _ in due_messages(fr, at(8, 30))] == ["C'est l'heure : Acide folique 💊"]))
    checks.append(("Französisch: Termin", [t for t, _, _ in due_messages(fr, at(18, 0))] == ["Demain : Frauenarzt à 09:30 📅"]))
    checks.append(("Französisch: Trinken", [b for _, b, _ in due_messages(fr, at(11, 0))] == ["0 l sur 1,5 l bus. Un verre d'eau fait du bien à toi et au bébé."]))
    global DATA_DIR
    import tempfile
    DATA_DIR = tempfile.mkdtemp()
    dev["settings"]["quietAfter"] = "21:00"; dev["status"] = {"date": d.isoformat(), "water": 0, "taken": []}
    store("devices.json", {"handy": dev})
    tick(at(8, 30), fake); tick(at(8, 30), fake)
    checks.append(("keine doppelte Mitteilung in derselben Minute", len(sent) == 1))
    checks.append(("Schlüssel laden, signieren und verschlüsseln (ohne Senden)", real_send_check()))
    ok = all(c for _, c in checks)
    for name, c in checks: print(("OK    " if c else "FEHLER"), name)
    print("Selbsttest:", "bestanden" if ok else "FEHLGESCHLAGEN")
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if a.selftest: sys.exit(0 if selftest() else 1)
    vapid()
    threading.Thread(target=scheduler, daemon=True).start()
    log.info("Bauchgefühl-Server läuft auf 127.0.0.1:%s (erlaubt für %s)", PORT, APP_ORIGIN)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
