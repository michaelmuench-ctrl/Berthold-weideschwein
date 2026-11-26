#!/usr/bin/env python3
import argparse
import csv
import html
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

COMPANY = {
    "name": "Kulmbacher Weideschwein",
    "street": "Eggenreuth 3",
    "zip": "95326",
    "city": "Kulmbach",
    "country": "DE",
    "phone": "09221 3919676",
    "email": "info@kulmbacher-weideschwein.de",
    "vat_id": "[USt-IdNr eintragen]",
    "bank": "[Bankverbindung eintragen]",
    "payment_terms": "14 Tage netto",
}

DEFAULT_VAT_FOOD = 0.07
DEFAULT_VAT_OTHER = 0.19
MAX_PACKAGE_KG = 30.0
PACKAGE_LENGTH_CM = 60
PACKAGE_WIDTH_CM = 40
PACKAGE_HEIGHT_CM = 40

DHL_HEADER = [
    "Anrede", "Vorname", "Nachname", "Firma", "Strasse", "Hausnummer",
    "PLZ", "Ort", "Land", "Telefon", "E-Mail",
    "Gewicht_kg", "Laenge_cm", "Breite_cm", "Hoehe_cm",
    "Sendungsreferenz", "Produkt", "Services",
]


def eur(x):
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def de_date(iso):
    if not iso:
        return ""
    y, m, d = iso.split("-")
    return f"{d}.{m}.{y}"


def load_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_orders(path):
    orders = {}
    for row in load_csv(path):
        orders[row["order_id"].strip()] = {k.strip(): (v or "").strip() for k, v in row.items()}
    return orders


def load_items(path):
    items = {}
    for row in load_csv(path):
        oid = row["order_id"].strip()
        items.setdefault(oid, []).append({
            "article": row["article"].strip(),
            "description": row.get("description", "").strip(),
            "qty": float(row["qty"]),
            "unit": row.get("unit", "Stk").strip() or "Stk",
            "price_net": float(row["price_net"]),
            "vat_rate": float(row["vat_rate"]) if row.get("vat_rate", "").strip() else DEFAULT_VAT_FOOD,
            "weight_kg": float(row.get("weight_kg", "0") or 0),
            "cooled": row.get("cooled", "nein").strip().lower() in ("ja", "yes", "true", "1"),
        })
    return items


def line_total(it):
    return it["qty"] * it["price_net"]


def order_totals(order_items):
    net = sum(line_total(i) for i in order_items)
    vat_by_rate = {}
    for i in order_items:
        vat_by_rate[i["vat_rate"]] = vat_by_rate.get(i["vat_rate"], 0.0) + line_total(i) * i["vat_rate"]
    vat = sum(vat_by_rate.values())
    return net, vat, net + vat, vat_by_rate


def page(title, body):
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>{html.escape(title)}</title>
<style>
body {{ font-family: Helvetica, Arial, sans-serif; color: #282828; margin: 40px; font-size: 14px; }}
.header {{ background: #0B3318; color: #fff; padding: 18px 24px; margin-bottom: 28px; }}
.header h1 {{ font-family: Georgia, 'Times New Roman', serif; font-size: 22px; margin: 0 0 4px; }}
.header p {{ margin: 0; font-size: 12px; opacity: .85; }}
h2 {{ font-family: Georgia, serif; font-size: 18px; margin: 24px 0 8px; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 8px; }}
th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; }}
th {{ background: #f0f0f0; }}
td.num, th.num {{ text-align: right; }}
.totals td {{ border: 0; padding: 3px 10px; }}
.totals tr.total td {{ border-top: 2px solid #0B3318; font-weight: bold; }}
.addr {{ display: flex; gap: 60px; margin: 18px 0; }}
.addr div {{ line-height: 1.5; }}
.meta {{ margin: 12px 0; }}
.meta span {{ margin-right: 32px; }}
.note {{ margin-top: 24px; font-size: 12px; color: #555; }}
.no-print {{ margin-bottom: 20px; }}
@media print {{ .no-print {{ display: none; }} body {{ margin: 0; }} }}
</style>
</head>
<body>
<div class="no-print"><button onclick="window.print()">Drucken / als PDF speichern</button></div>
<div class="header"><h1>{html.escape(COMPANY['name'])}</h1>
<p>{COMPANY['street']}, {COMPANY['zip']} {COMPANY['city']} · Tel {COMPANY['phone']} · {COMPANY['email']}</p></div>
{body}
</body>
</html>"""


def customer_addr(o):
    lines = []
    if o.get("company"):
        lines.append(o["company"])
    name = " ".join(x for x in [o.get("first_name", ""), o.get("last_name", "")] if x)
    if name:
        lines.append(name)
    lines.append(f"{o.get('street', '')} {o.get('house_number', '')}".strip())
    lines.append(f"{o.get('zip', '')} {o.get('city', '')}".strip())
    if o.get("country", "DE") != "DE":
        lines.append(o["country"])
    return "<br>".join(html.escape(l) for l in lines if l)


def positions_table(items, with_prices):
    rows = ""
    for i, it in enumerate(items, 1):
        desc = it["article"] + (f" – {it['description']}" if it["description"] else "")
        row = f"<td>{i}</td><td>{html.escape(desc)}</td><td class='num'>{it['qty']:g}</td><td>{html.escape(it['unit'])}</td>"
        if with_prices:
            row += f"<td class='num'>{eur(it['price_net'])}</td><td class='num'>{int(it['vat_rate'] * 100)} %</td><td class='num'>{eur(line_total(it))}</td>"
        rows += f"<tr>{row}</tr>"
    head = "<tr><th>Pos</th><th>Artikel</th><th class='num'>Menge</th><th>Einheit</th>"
    if with_prices:
        head += "<th class='num'>Einzelpreis (netto)</th><th class='num'>MwSt</th><th class='num'>Gesamt (netto)</th>"
    head += "</tr>"
    return f"<table>{head}{rows}</table>"


def write_lieferschein(o, items, out):
    oid = o["order_id"]
    body = f"""
<h2>Lieferschein LS-{html.escape(oid)}</h2>
<div class="meta"><span><strong>Bestell-Nr.:</strong> {html.escape(oid)}</span>
<span><strong>Datum:</strong> {de_date(o.get('created', ''))}</span>
<span><strong>Lieferdatum:</strong> {de_date(o.get('delivery_date', '')) or de_date(str(date.today()))}</span></div>
<div class="addr"><div><strong>Lieferadresse:</strong><br>{customer_addr(o)}</div>
<div><strong>Verkäufer:</strong><br>{html.escape(COMPANY['name'])}<br>{COMPANY['street']}<br>{COMPANY['zip']} {COMPANY['city']}</div></div>
{positions_table(items, with_prices=False)}
<p class="note">Die Ware bleibt bis zur vollständigen Bezahlung Eigentum des Verkäufers. Versand: DHL (Sendungsreferenz {html.escape(oid)}). Kühlkette bei kühlpflichtigen Artikeln bis zur Übergabe an den Versanddienstleister sicherstellen.</p>
"""
    (out / f"Lieferschein_{oid}.html").write_text(page(f"Lieferschein LS-{oid}", body), encoding="utf-8")


def write_rechnung(o, items, out):
    oid = o["order_id"]
    year = (o.get("created") or str(date.today()))[:4]
    inv_no = f"REC-{oid}" if oid.startswith(year) else f"REC-{year}-{oid}"
    net, vat, gross, vat_by_rate = order_totals(items)
    vat_rows = "".join(
        f"<tr><td class='num'>{int(r * 100)} %</td><td class='num'>{eur(net_r)}</td><td class='num'>{eur(v)}</td></tr>"
        for r, v in sorted(vat_by_rate.items()) for net_r in [sum(line_total(i) for i in items if i['vat_rate'] == r)]
    )
    body = f"""
<h2>Rechnung {html.escape(inv_no)}</h2>
<div class="meta"><span><strong>Rechnungs-Nr.:</strong> {html.escape(inv_no)}</span>
<span><strong>Rechnungsdatum:</strong> {de_date(o.get('created', ''))}</span>
<span><strong>Lieferdatum:</strong> {de_date(o.get('delivery_date', ''))}</span>
<span><strong>Bestell-Nr.:</strong> {html.escape(oid)}</span></div>
<div class="addr"><div><strong>Rechnungsadresse:</strong><br>{customer_addr(o)}</div>
<div><strong>Verkäufer:</strong><br>{html.escape(COMPANY['name'])}<br>{COMPANY['street']}<br>{COMPANY['zip']} {COMPANY['city']}<br>USt-IdNr.: {html.escape(COMPANY['vat_id'])}</div></div>
{positions_table(items, with_prices=True)}
<table class="totals">
<tr><td class="num">Zwischensumme (netto):</td><td class="num">{eur(net)}</td></tr>
{vat_rows}
<tr class="total"><td class="num">Gesamtbetrag (brutto):</td><td class="num">{eur(gross)}</td></tr>
</table>
<p class="note">Zahlungsziel: {html.escape(COMPANY['payment_terms'])}. Bankverbindung: {html.escape(COMPANY['bank'])}. Versand: DHL (Sendungsreferenz {html.escape(oid)}).</p>
"""
    (out / f"Rechnung_{inv_no}.html").write_text(page(f"Rechnung {inv_no}", body), encoding="utf-8")
    return inv_no


def pack_items(items):
    packages = []
    current = []
    current_kg = 0.0
    for it in items:
        for _ in range(int(it["qty"])):
            w = it["weight_kg"]
            if current and current_kg + w > MAX_PACKAGE_KG:
                packages.append(current)
                current, current_kg = [], 0.0
            current.append({"article": it["article"], "unit": it["unit"], "weight_kg": w, "cooled": it["cooled"]})
            current_kg += w
    if current:
        packages.append(current)
    return packages


def write_verdichtungspapier(o, items, out):
    oid = o["order_id"]
    packages = pack_items(items)
    total_kg = sum(sum(p["weight_kg"] for p in pkg) for pkg in packages)
    cooled = any(p["cooled"] for pkg in packages for p in pkg)
    blocks = ""
    for n, pkg in enumerate(packages, 1):
        pkg_kg = sum(p["weight_kg"] for p in pkg)
        rows = "".join(
            f"<tr><td>{html.escape(p['article'])}</td><td>{html.escape(p['unit'])}</td><td class='num'>{p['weight_kg']:g} kg</td><td>{'ja' if p['cooled'] else 'nein'}</td></tr>"
            for p in pkg
        )
        blocks += f"""
<h2>Paket {n} von {len(packages)} – {pkg_kg:g} kg {('(Kühlung erforderlich)' if any(p['cooled'] for p in pkg) else '')}</h2>
<table><tr><th>Artikel</th><th>Einheit</th><th class="num">Gewicht</th><th>Kühlpflichtig</th></tr>{rows}</table>
"""
    body = f"""
<h2>Verdichtungspapier / Packzettel – Bestellung {html.escape(oid)}</h2>
<div class="meta"><span><strong>Datum:</strong> {de_date(o.get('created', ''))}</span>
<span><strong>Lieferdatum:</strong> {de_date(o.get('delivery_date', ''))}</span>
<span><strong>Pakete gesamt:</strong> {len(packages)}</span>
<span><strong>Gesamtgewicht:</strong> {total_kg:g} kg</span>
<span><strong>Kühlkette:</strong> {'erforderlich' if cooled else 'nicht erforderlich'}</span></div>
<div class="addr"><div><strong>Empfänger:</strong><br>{customer_addr(o)}</div></div>
{blocks}
<p class="note">Maße je Paket: {PACKAGE_LENGTH_CM} × {PACKAGE_WIDTH_CM} × {PACKAGE_HEIGHT_CM} cm, max. {MAX_PACKAGE_KG:g} kg. Sendungsreferenz für DHL: {html.escape(oid)}. Vor Übergabe an DHL: Kühlkette prüfen, Paketanzahl gegen Sendungsreferenz abgleichen.</p>
"""
    (out / f"Verdichtungspapier_{oid}.html").write_text(page(f"Verdichtungspapier {oid}", body), encoding="utf-8")


def dhl_row(o, items):
    weight = sum(i["qty"] * i["weight_kg"] for i in items)
    services = "Kühlkette" if any(i["cooled"] for i in items) else ""
    return [
        o.get("salutation", ""), o.get("first_name", ""), o.get("last_name", ""),
        o.get("company", ""), o.get("street", ""), o.get("house_number", ""),
        o.get("zip", ""), o.get("city", ""), o.get("country", "DE"),
        o.get("phone", ""), o.get("email", ""),
        f"{weight:.2f}", str(PACKAGE_LENGTH_CM), str(PACKAGE_WIDTH_CM), str(PACKAGE_HEIGHT_CM),
        o["order_id"], "DHL Paket", services,
    ]


def write_dhl_csv(orders, items_by_order, out):
    path = out / "dhl_export.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(DHL_HEADER)
        for oid in sorted(orders):
            w.writerow(dhl_row(orders[oid], items_by_order.get(oid, [])))
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--orders", default=str(ROOT / "orders" / "orders.csv"))
    ap.add_argument("--items", default=str(ROOT / "orders" / "items.csv"))
    ap.add_argument("--out", default=str(ROOT / "tools" / "shop" / "out"))
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    orders = load_orders(args.orders)
    items_by_order = load_items(args.items)

    manifest = []
    for oid in sorted(orders):
        o = orders[oid]
        items = items_by_order.get(oid, [])
        write_lieferschein(o, items, out)
        inv = write_rechnung(o, items, out)
        write_verdichtungspapier(o, items, out)
        manifest.append({
            "order_id": oid,
            "dhl_reference": oid,
            "lieferschein": f"Lieferschein_{oid}.html",
            "rechnung": f"Rechnung_{inv}.html",
            "verdichtungspapier": f"Verdichtungspapier_{oid}.html",
            "items": len(items),
        })
        print(f"{oid}: Lieferschein, Rechnung {inv}, Verdichtungspapier ({len(items)} Positionen)")

    dhl_path = write_dhl_csv(orders, items_by_order, out)
    print(f"DHL-CSV-Export: {dhl_path.name} ({len(orders)} Sendungen)")

    with open(out / "manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(manifest[0].keys()) if manifest else ["order_id"])
        w.writeheader()
        w.writerows(manifest)
    print(f"Manifest: manifest.csv ({len(manifest)} Bestellungen)")


if __name__ == "__main__":
    main()
