# Bauchgefühl

Web-App fürs Handy: Ernährung in der Schwangerschaft, einfach gemacht.

- **Heute:** Schwangerschaftswoche (aus dem Geburtstermin), was im aktuellen Trimester wichtig ist, die heutigen Mahlzeiten aus dem Wochenplan und eine Abhak-Liste für Folsäure, Jod usw.
- **Heute** zeigt außerdem die Karte „Deine Woche“ (SSW 4 bis 40: Größenvergleich, Länge, Gewicht, Entwicklung und ein passender Ernährungstipp, mit Pfeilen zum Blättern) und einen Trink-Zähler (6 Gläser à 250 ml = 1,5 l).
- **Lust & Hilfe:** Reiter „Heißhunger“: Lust auf Schokolade, Chips, Pizza, Eis …? Gesunde, schwangerschaftssichere Alternativen mit Rezept und ein Tipp ohne Kochen. Reiter „Beschwerden“: Tipps und passende Rezepte bei Übelkeit, Sodbrennen, Verstopfung, Wadenkrämpfen und Müdigkeit, jeweils mit Hinweis, wann man zur Ärztin sollte.
- **Darf ich?:** Lebensmittel-Suche mit 769 Steckbriefen (Liste zum Stöbern nach Gruppen und A bis Z, eigene Gruppen für asiatische, italienische, griechische, mexikanische und türkische Restaurants) und Suchbegriffen. Der beste Treffer erscheint groß mit „Unbedenklich“, „Mit Vorsicht“ oder „Meiden“ und Begründung (Listerien, Toxoplasmose, Salmonellen, Quecksilber, Koffein …). Steht etwas nicht in der Liste, antwortet die App nach Regeln (roh, geräuchert, Rohmilch, Alkohol, Rohwurst …). Eingetragene Allergien werden als „Deine Allergie“ angezeigt.
- **Rezepte:** 176 Rezepte (52 Frühstück, 77 Hauptgerichte, 47 Snacks; 93 davon in höchstens 20 Minuten, 33 mit Tipp zum Einfrieren), sortiert nach den Nährstoffen, die im aktuellen Trimester wichtig sind. Jedes Rezept mit Sicherheitshinweis. Im Rezept „♥ Lieblingsrezept“ (kommt öfter in den Wochenplan, Filter „Favoriten“) und „Nicht mehr vorschlagen“ (wieder einblenden über das Zahnrad auf „Heute“).
- **Woche:** Wochenplan mit automatischem Vorschlag (bis zu 2× Fisch, Thunfisch höchstens 1×), jede Mahlzeit änderbar, Einkaufsliste für 1 bis 6 Personen zum Abhaken und Kopieren.

Alle Eingaben bleiben nur auf dem Handy (Browser-Speicher). Über das Zahnrad → **Datensicherung → „Sichern und teilen“** lässt sich alles als kleine Textdatei per WhatsApp, Mail, Drive oder iCloud sichern und mit **„Wiederherstellen“** wieder einlesen, z. B. auf einem neuen Handy. Nach dem ersten Öffnen funktioniert die App auch ohne Internet.

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
| `index.html` | Die ganze App. Oben im Skript stehen die Daten: `RECIPES`, `CRAVINGS`, `COMPLAINTS`, `FOODS`, `RULES` (Antworten für Suchbegriffe, die nicht in der Liste stehen), `TRIMESTERS`, `WEEKS`. |
| `sw.js` | Offline-Speicher. Nach Änderungen an der App `CACHE` hochzählen (`bauchgefuehl-v2` …). |
| `manifest.webmanifest`, `icon*.png`, `icon.svg` | Name und Symbol für den Startbildschirm. |

Persönliche Voreinstellung: Allergien Walnuss und Kiwi (in den Einstellungen änderbar, Rezepte mit diesen Zutaten werden ausgeblendet). Die Rezepte enthalten außerdem keine Mandeln. Lachs und Seelachs sind ausgeblendet, Thunfisch ist erlaubt.

Rezeptmengen sind immer für 2 Portionen angegeben, die App rechnet auf die gewählte Personenzahl um.

## Quellen

- Netzwerk Gesund ins Leben: Handlungsempfehlungen „Ernährung und Lebensstil vor und während der Schwangerschaft“
- Bundesinstitut für Risikobewertung (BfR): „Sicher verpflegt“, Merkblätter zu Listeriose und Toxoplasmose
- Deutsche Gesellschaft für Ernährung (DGE): Referenzwerte für die Nährstoffzufuhr

**Hinweis:** Die App ist eine Alltagshilfe und ersetzt keine Beratung durch Ärztin oder Hebamme. Nahrungsergänzungsmittel (besonders Eisen und Jod) nur nach Rücksprache.
