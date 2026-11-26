# Shop-Zusatzanbindungen (DHL, Lieferschein, Rechnung, Verdichtungspapier)

`generate.py` erzeugt aus den Bestell-CSVs in `orders/` vollautomatisch:

| Ausgabe | Datei | Zweck |
|---|---|---|
| DHL-Anmeldung (CSV-Export) | `out/dhl_export.csv` | Import ins DHL-Geschäftskundenportal → Sendungen automatisch angemeldet, Paketmarken erzeugbar |
| Lieferschein | `out/Lieferschein_<Bestellnr>.html` | Druck-/PDF-fähig, ohne Preise |
| Rechnung | `out/Rechnung_REC-<Jahr>-<Bestellnr>.html` | Druck-/PDF-fähig, mit MwSt-Ausweis und Pflichtangaben |
| Verdichtungspapier (Packzettel) | `out/Verdichtungspapier_<Bestellnr>.html` | Zerlegung der Bestellung in Pakete (max. 30 kg), Gewichte, Kühlpflicht – für die Metzgerei/Kommissionierung |
| Manifest | `out/manifest.csv` | Zuordnung Dateien ↔ Bestellung |

## Nutzung

```bash
python3 tools/shop/generate.py                      # defaults: orders/orders.csv, orders/items.csv -> tools/shop/out/
python3 tools/shop/generate.py --orders meine_bestellungen.csv --items meine_positionen.csv --out out/
```

Vollautomatisch in CI: Push von Änderungen unter `orders/` auf `main` startet den
Workflow `shop-documents` (`.github/workflows/shop-documents.yml`); die fertigen
Dokumente stehen als Workflow-Artefakt `shop-documents` zum Download bereit.

## Anpassen

- Firmen-/Absenderdaten, USt-IdNr, Bankverbindung: `COMPANY` oben in `generate.py`
  (Platzhalter `[USt-IdNr eintragen]` / `[Bankverbindung eintragen]` ersetzen).
- Paketgewicht/-maße: `MAX_PACKAGE_KG`, `PACKAGE_*_CM`.
- MwSt-Sätze: Default 7 % (Lebensmittel) bzw. 19 %, pro Position überschreibbar
  über die Spalte `vat_rate` in `items.csv`.
- DHL-CSV-Spaltenkopf: `DHL_HEADER` in `generate.py` – vor Produktivbetrieb mit dem
  aktuellen Import-Template des DHL-Portals abgleichen.

## Verdichtungspapier

Packt die Bestellpositionen nacheinander in Pakete à max. `MAX_PACKAGE_KG` und listet
pro Paket Artikel, Gewicht und Kühlpflicht – inkl. Gesamtgewicht, Paketanzahl und
Hinweis auf die Kühlkette vor DHL-Übergabe.
