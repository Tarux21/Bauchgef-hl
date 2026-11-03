# Bauchgefühl

Web-App fürs Handy: Ernährung in der Schwangerschaft, einfach gemacht.

- **Heute:** Schwangerschaftswoche (aus dem Geburtstermin), was im aktuellen Trimester wichtig ist, die heutigen Mahlzeiten aus dem Wochenplan und eine Abhak-Liste für Folsäure, Jod usw.
- **Lust auf:** Heißhunger auf Schokolade, Chips, Pizza, Eis …? Gesunde, schwangerschaftssichere Alternativen mit Rezept und ein Tipp ohne Kochen.
- **Darf ich?:** Lebensmittel-Ampel mit Suche (Ja / Prüfen / Nein) und kurzer Begründung (Listerien, Toxoplasmose, Salmonellen, Quecksilber, Koffein).
- **Rezepte:** 25 Rezepte, sortiert nach den Nährstoffen, die im aktuellen Trimester wichtig sind. Jedes Rezept mit Sicherheitshinweis.
- **Woche:** Wochenplan mit automatischem Vorschlag (immer 2× Fisch), jede Mahlzeit änderbar, Einkaufsliste für 1 bis 6 Personen zum Abhaken und Kopieren.

Alle Eingaben bleiben nur auf dem Handy (Browser-Speicher). Nach dem ersten Öffnen funktioniert die App auch ohne Internet.

## Aufs Handy bringen

1. Auf GitHub im Repo: **Settings → Pages → Branch `main`, Ordner `/ (root)` → Save**.
2. Nach ca. 1 Minute ist die App erreichbar unter `https://tarux21.github.io/Bauchgef-hl/`.
3. Auf dem Handy öffnen und zum Startbildschirm hinzufügen:
   - **iPhone (Safari):** Teilen-Symbol → „Zum Home-Bildschirm“.
   - **Android (Chrome):** Menü ⋮ → „Zum Startbildschirm hinzufügen“ bzw. „App installieren“.

## Am Rechner ansehen

`index.html` im Browser öffnen genügt. Für den Offline-Modus einen kleinen Server starten, z. B. `python -m http.server` im Ordner, dann http://localhost:8000/ öffnen.

## Dateien

| Datei | Inhalt |
|---|---|
| `index.html` | Die ganze App. Oben im Skript stehen die Daten: `RECIPES`, `CRAVINGS`, `FOODS`, `TRIMESTERS`. |
| `sw.js` | Offline-Speicher. Nach Änderungen an der App `CACHE` hochzählen (`bauchgefuehl-v2` …). |
| `manifest.webmanifest`, `icon*.png`, `icon.svg` | Name und Symbol für den Startbildschirm. |

Rezeptmengen sind immer für 2 Portionen angegeben, die App rechnet auf die gewählte Personenzahl um.

## Quellen

- Netzwerk Gesund ins Leben: Handlungsempfehlungen „Ernährung und Lebensstil vor und während der Schwangerschaft“
- Bundesinstitut für Risikobewertung (BfR): „Sicher verpflegt“, Merkblätter zu Listeriose und Toxoplasmose
- Deutsche Gesellschaft für Ernährung (DGE): Referenzwerte für die Nährstoffzufuhr

**Hinweis:** Die App ist eine Alltagshilfe und ersetzt keine Beratung durch Ärztin oder Hebamme. Nahrungsergänzungsmittel (besonders Eisen und Jod) nur nach Rücksprache.
