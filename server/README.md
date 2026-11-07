# Bauchgefühl Erinnerungs-Server (Raspberry Pi)

Schickt Push-Mitteilungen an die Bauchgefühl-App auf dem iPhone:

- **Nahrungsergänzungen** zur eingestellten Tageszeit (morgens, mittags, abends), nur wenn sie noch nicht abgehakt sind.
- **Trinken** zu den eingestellten Uhrzeiten, nur wenn man hinter dem Tagesplan liegt.
- **Eigene Termine** aus dem Vorsorge-Kalender am Vortag um 18 Uhr.
- Nach der Ruhezeit (21 Uhr) kommt nichts mehr.

Die Mitteilungen kommen in der Sprache, die in der App eingestellt ist (Deutsch oder Französisch). Die App meldet ihre Einstellungen und den Tagesstand (Haken, Gläser) an den Server. Er ist **nur im eigenen Tailscale-Netz** erreichbar (`tailscale serve`, kein Funnel). Die Mitteilungen selbst laufen über Apples Push-Dienst. Dafür muss der Pi nur ins Internet können, am Router wird nichts geöffnet.

## Voraussetzungen

- Raspberry Pi mit Raspberry Pi OS, dauerhaft an und mit Internet
- Tailscale auf dem Pi und auf dem iPhone, im selben Netz
- In der Tailscale-Verwaltung: **MagicDNS** und **HTTPS-Zertifikate** eingeschaltet (DNS-Seite)
- iPhone mit iOS 16.4 oder neuer, App vom Home-Bildschirm geöffnet

## Einrichten

```bash
git clone https://github.com/Tarux21/Bauchgef-hl.git ~/bauchgefuehl
cd ~/bauchgefuehl/server
bash install.sh
```

Das Skript installiert die Python-Pakete, führt einen Selbsttest aus, richtet den Dienst `bauchgefuehl-push` ein und gibt ihn per `tailscale serve` frei. Am Ende steht die Adresse, z. B. `https://raspberrypi.tail1234.ts.net`.

In der App: **Zahnrad → Erinnerungen → Adresse eintragen → „Mitteilungen einschalten“** und die Nachfrage des iPhones erlauben. Mit „Testnachricht“ prüfen.

## Aktualisieren

```bash
cd ~/bauchgefuehl && git pull && sudo systemctl restart bauchgefuehl-push
```

## Prüfen

```bash
systemctl status bauchgefuehl-push        # läuft der Dienst?
journalctl -u bauchgefuehl-push -n 50     # was wurde gesendet?
curl -s http://127.0.0.1:8787/api/health  # wie viele Geräte verbunden?
```

## Daten

Im Ordner `server/data/`:

- `vapid.json`: Schlüsselpaar für die Mitteilungen (geheimer Teil, nicht weitergeben)
- `devices.json`: verbundene iPhones, deren Erinnerungszeiten, Supplement-Namen und der heutige Stand
- `sent.json`: bereits gesendete Mitteilungen (verhindert doppelte)

Der Ordner steht in `.gitignore` und wird nicht hochgeladen. Wird `vapid.json` gelöscht, muss sich die App neu verbinden.
