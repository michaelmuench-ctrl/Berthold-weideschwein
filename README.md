# Kulmbacher Weideschwein – neue Homepage

Statische One-Pager-Homepage: Inhalte der bisherigen Jimdo-Seite
(https://www.kulmbacher-weideschwein.de) im Design der Vorlage
https://josefsbio.de (Shopify-Theme: Dunkelgrün `#0B3318`, Anton-Buttons,
Didot-Headlines, 96vh-Hero, Image-with-Text, Kacheln, Newsletter, Footer).

## Lokal starten

```bash
python3 -m http.server 8000
# dann http://localhost:8000 öffnen
```

## Aufbau

- `index.html` – komplette Homepage (semantisches HTML5, `lang="de"`)
- `assets/css/style.css` – Design-System der Vorlage (CSS-Variablen in `:root`)
- `assets/js/main.js` – Sticky-Header, Mobile-Menü, Newsletter-Formular, Jahr im Footer
- `assets/img/` – alle Bilder lokal (von image.jimcdn.com heruntergeladen, neu skaliert)
- `tools/check_site.py` – Selbst-Checks der Homepage (Assets, Anker, Links, Inhaltsparität, Template-Tokens)
- `tools/shop/` – Shop-Zusatzanbindungen (DHL-CSV-Export, Lieferschein, Rechnung, Verdichtungspapier)
- `orders/` – Bestellungen als CSV (Eingang für die Shop-Tools, Beispieldaten)

## CI/CD (GitHub Actions)

- `weideschwein-kulmbach-ci` (`.github/workflows/ci.yml`) – läuft bei Push/PR:
  HTML-Validierung (`html-validate`), Site-Checks (`tools/check_site.py`),
  Homepage als Artefakt.
- `shop-documents` (`.github/workflows/shop-documents.yml`) – läuft bei Änderungen
  unter `orders/`: erzeugt DHL-CSV, Lieferschein, Rechnung, Verdichtungspapier
  als Artefakt.
- `pages-deploy` (`.github/workflows/pages.yml`) – **manuell** per
  `workflow_dispatch` auslösbar: deployed das Repo als GitHub Pages.
  Aktivierung von Pages in den Repo-Einstellungen (Settings → Pages → GitHub Actions)
  und ein Lauf des Workflows genügen.

## Shop-Zusatzanbindungen

Details siehe `tools/shop/README.md` und `orders/README.md`:

```bash
python3 tools/shop/generate.py   # orders/*.csv -> tools/shop/out/
```

Erzeugt pro Bestellung: `dhl_export.csv` (DHL-Geschäftskundenportal-Import),
`Lieferschein_*.html`, `Rechnung_REC-*.html`, `Verdichtungspapier_*.html` (Packzettel
für die Metzgerei: Pakete, Gewichte, Kühlkette) + `manifest.csv`.

## Mapping Alt-Seite → neue Homepage

| Alt-Seite (kulmbacher-weideschwein.de) | Neue Homepage |
|---|---|
| H1 „Glückliche Schweine in Freilandhaltung“ + Intro-Text | Hero + grüne Intro-Sektion |
| Abschnitte Erlebnisbauernhof, Fleisch/Shop, Metzgerei, Versand, Fütterung, Freilandhaltung, Zucht | Image-with-Text-Sektionen mit Ankern `#erlebnis`, `#fleisch`, `#fuetterung`, `#freiland`, `#zucht` |
| Navigation (Home, Fleisch/Shop, Zucht, Ferkelverkauf, News, Galerie/Videos, Geschichte, Kontakt) | Header-Nav; Unterseiten verlinken aktuell noch auf die Live-Seite |
| Hofbrief-Anmeldung | Newsletter-Sektion `#hofbrief` |
| WhatsApp 015206188828 | WhatsApp-Sektion mit wa.me-Link |
| Bildergalerie | Galerie `#galerie` (10 Bilder, lokal) |
| Kontakt (Eggenreuth 3, 95326 Kulmbach, Tel 09221 3919676, info@kulmbacher-weideschwein.de) | Footer `#kontakt` |
| BR-Beitrag „Unser Land“ | Image-with-Text mit ARD-Mediathek-Link |

## Design-Tokens der Vorlage (josefsbio.de)

- Primärfarbe Dunkelgrün: `rgb(11, 51, 24)` = `#0B3318` (Buttons, dunkle Sektionen, Footer)
- Text auf Hell: `rgb(40, 40, 40)` = `#282828`; Sektions-Hintergrund `#fafafa`
- Headlines: Didot-Serifen (`"Linotype Didot", Didot, serif` + Playfair Display als Webfont-Fallback)
- Buttons/Eyebrows: `Anton`, Uppercase
- Hero: 96vh Desktop / 85vh Mobile mit Gradient-Overlay
- Kacheln (Collection-List): Bild + Overlay `rgba(0,0,0,.3)`, weiße Headline

## Offene Punkte / TODO

- Nav-Links auf Unterseiten (Ferkelverkauf, News, Geschichte) und Legal-Links zeigen
  noch auf die bisherige Live-Seite – umstellen, sobald die Unterseiten migriert sind.
- Newsletter-Formular ist statisch (Double-Opt-in-Hinweis); für echten Versand
  an einen ESP (z. B. Sendinblue – bisher im Einsatz) anbinden.
- Hero der Vorlage nutzt ein Video; hier wurde ein Hero-Bild eingesetzt.
- Rechtliches (Impressum/Datenschutz) muss an den neuen Auftritt angepasst werden.
- Shop-Tools: Platzhalter in `tools/shop/generate.py` (`USt-IdNr`, Bankverbindung)
  ersetzen; DHL-CSV-Spaltenkopf mit dem DHL-Portal-Template abgleichen; Beispieldaten
  in `orders/` durch echte Bestellungen ersetzen.
