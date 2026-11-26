# Bestellungen (Eingang für die Shop-Tools)

Diese beiden CSV-Dateien sind der Maschineneingang für `tools/shop/generate.py`.
Die enthaltenen Zeilen sind **Beispieldaten** – vor Produktivbetrieb durch echte
Bestellungen ersetzen (gleiche Spaltenstruktur).

- `orders.csv` – eine Zeile pro Bestellung (Kundendaten, Lieferadresse, Versand)
- `items.csv` – eine Zeile pro Bestellposition (Artikel, Menge, Preis, Gewicht, Kühlung)

## Ablauf (vollautomatisch)

1. Neue Bestellung als Zeile in `orders.csv` + Positionen in `items.csv` eintragen (oder per Shop-Export einspielen).
2. Lokal: `python3 tools/shop/generate.py`
   oder in CI: Push auf `main` mit Änderungen unter `orders/` löst den Workflow
   `shop-documents` aus – alle Dokumente landen als Artefakt `shop-documents`.
3. Ergebnis in `tools/shop/out/`:
   - `dhl_export.csv` – DHL-CSV-Export (Semikolon-getrennt) für den Import im
     DHL-Geschäftskundenportal (Sendungsanmeldung vollautomatisch vorbereitet)
   - `Lieferschein_<Bestellnr>.html` – druck-/PDF-fähig
   - `Rechnung_REC-<Jahr>-<Bestellnr>.html` – mit allen Pflichtangaben
   - `Verdichtungspapier_<Bestellnr>.html` – Packzettel: Artikel pro Paket, Gewichte, Kühlkette
   - `manifest.csv` – Übersicht welche Dateien zu welcher Bestellung gehören

## DHL-CSV-Spalten

Der Spaltenkopf in `generate.py` (`DHL_HEADER`) folgt dem üblichen CSV-Import des
DHL-Geschäftskundenportals. Vor dem ersten Produktiv-Import einmalig gegen das
aktuelle Template des DHL-Portals prüfen und ggf. in `generate.py` anpassen.
