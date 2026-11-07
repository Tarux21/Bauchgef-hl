# Bauchgefühl

Web-App fürs Handy: Ernährung in der Schwangerschaft, einfach gemacht. Auf **Deutsch und Französisch** (Schalter **DE | FR** oben auf „Heute“ oder im Zahnrad unter „Sprache“; beim ersten Start nach der Sprache des Handys).

- **Heute:** Schwangerschaftswoche (aus dem Geburtstermin), die Karte **„Als Nächstes in der Vorsorge“** (öffnet den Vorsorge-Kalender nach dem **französischen System** (HAS, Assurance Maladie): Untersuchungen, Ultraschall, Impfungen und Behördengänge wie déclaration de grossesse, entretien prénatal précoce, congé maternité, passend zur Woche, mit Fortschritt und eigenen Terminen), die Karte „Deine Woche“ (SSW 4 bis 40: Größenvergleich, Länge, Gewicht, Entwicklung, Ernährungstipp) und „Jetzt wichtig“ mit den Nährstoffen des Trimesters.
- **Tagesziel:** zwei Ringe für Trinken (außen) und Nahrungsergänzungen (innen) mit einem Baby in der Mitte, das immer mehr lächelt, dazu die letzten 7 Tage und die Serie „Tage in Folge alles geschafft“. Trinkziel (1,5 bis 2,5 l) und Nahrungsergänzungen mit Tageszeit und Hinweis lassen sich unter „Anpassen“ einstellen.
- **Lust & Hilfe:** Reiter „Heißhunger“: Lust auf Schokolade, Chips, Pizza, Eis …? Gesunde, schwangerschaftssichere Alternativen mit Rezept und ein Tipp ohne Kochen. Reiter „Beschwerden“: Tipps und passende Rezepte bei Übelkeit, Sodbrennen, Verstopfung, Wadenkrämpfen und Müdigkeit, jeweils mit Hinweis, wann man zur Ärztin sollte.
- **Darf ich?:** Lebensmittel-Suche mit 896 Steckbriefen (Liste zum Stöbern nach Gruppen und A bis Z, eigene Gruppen für asiatische, thailändische, vietnamesische, indische, italienische, spanische, französische, griechische, amerikanische, mexikanische und türkische Restaurants) und Suchbegriffen. Der beste Treffer erscheint groß mit „Unbedenklich“, „Mit Vorsicht“ oder „Meiden“ und Begründung (Listerien, Toxoplasmose, Salmonellen, Quecksilber, Koffein …). Steht etwas nicht in der Liste, antwortet die App nach Regeln (roh, geräuchert, Rohmilch, Alkohol, Rohwurst …). Eingetragene Allergien werden als „Deine Allergie“ angezeigt.
- **Rezepte:** 176 Rezepte (52 Frühstück, 77 Hauptgerichte, 47 Snacks; 93 davon in höchstens 20 Minuten, 33 mit Tipp zum Einfrieren), sortiert nach den Nährstoffen, die im aktuellen Trimester wichtig sind. Jedes Rezept mit Sicherheitshinweis. Im Rezept „♥ Lieblingsrezept“ (Filter „Favoriten“) und „Nicht mehr vorschlagen“ (wieder einblenden über das Zahnrad auf „Heute“).

**Französisch:** Alle Inhalte (896 Lebensmittel, 176 Rezepte mit Zutaten und Einheiten, Heißhunger, Beschwerden, Trimester, Wochen-Infos, Regeln, Vorsorge) sind übersetzt. Die Empfehlungen bleiben die deutschen (DGE, BfR), nur übersetzt. Die Suche versteht immer beide Sprachen („Ente“ und „canard“ finden denselben Steckbrief), Allergien ebenfalls („Walnuss“ warnt auch bei „noix“). Auf Französisch wird statt SSW die SA (semaine d'aménorrhée) angezeigt, gezählt ab der letzten Periode wie die SSW.

**Erinnerungen per Mitteilung** kommen optional von einem eigenen Raspberry Pi im Tailscale-Netz (siehe `server/README.md`). Dafür meldet die App Erinnerungszeiten, Supplement-Namen und den Tagesstand an den Pi, sonst nirgendwohin.

Alle Eingaben bleiben sonst nur auf dem Handy (Browser-Speicher). Über das Zahnrad → **Datensicherung → „Sichern und teilen“** lässt sich alles als kleine Textdatei per WhatsApp, Mail, Drive oder iCloud sichern und mit **„Wiederherstellen“** wieder einlesen, z. B. auf einem neuen Handy. Nach dem ersten Öffnen funktioniert die App auch ohne Internet.

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
| `index.html` | Die ganze App. Im ersten Skriptblock die französischen Übersetzungen (`FR_FOODS`, `FR_REC`, `FR_ING`, `FR_RULES`, `FR_WEEKS` …, Schlüssel ist der deutsche Name bzw. die Rezept-ID). Im zweiten die Daten: `RECIPES`, `CRAVINGS`, `COMPLAINTS`, `FOODS`, `RULES` (Antworten für Suchbegriffe, die nicht in der Liste stehen), `TRIMESTERS`, `WEEKS`, `VORSORGE`. Neue Einträge immer auch auf Französisch ergänzen. |
| `docs/Pruefliste-Hebamme.pdf`, `docs/Liste-de-verification-sage-femme.pdf` | Alle Angaben der App zum Abhaken für die Hebamme bzw. Sage-femme. |
| `sw.js` | Offline-Speicher. Nach Änderungen an der App `CACHE` hochzählen (`bauchgefuehl-v2` …). |
| `manifest.webmanifest`, `icon*.png`, `icon.svg` | Name und Symbol für den Startbildschirm. |

Persönliche Voreinstellung: Allergien Walnuss und Kiwi (in den Einstellungen änderbar, Rezepte mit diesen Zutaten werden ausgeblendet). Die Rezepte enthalten außerdem keine Mandeln. Lachs und Seelachs sind ausgeblendet, Thunfisch ist erlaubt.

Rezeptmengen sind immer für 2 Portionen angegeben, die App rechnet auf die gewählte Personenzahl um.

## Quellen

- Netzwerk Gesund ins Leben: Handlungsempfehlungen „Ernährung und Lebensstil vor und während der Schwangerschaft“
- Bundesinstitut für Risikobewertung (BfR): „Sicher verpflegt“, Merkblätter zu Listeriose und Toxoplasmose
- Deutsche Gesellschaft für Ernährung (DGE): Referenzwerte für die Nährstoffzufuhr
- Vorsorge-Kalender: Haute Autorité de Santé (HAS) und Assurance Maladie (ameli.fr)

**Hinweis:** Die App ist eine Alltagshilfe und ersetzt keine Beratung durch Ärztin oder Hebamme. Nahrungsergänzungsmittel (besonders Eisen und Jod) nur nach Rücksprache.
