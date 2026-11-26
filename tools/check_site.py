#!/usr/bin/env python3
import os
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
CSS = ROOT / "assets" / "css" / "style.css"

REQUIRED_STRINGS = [
    "glückliche schweine in freilandhaltung",
    "erlebnisbauernhof und tiergestützte therapie",
    "gutes fleisch vom weideschwein im hofladen oder online kaufen",
    "eigene metzgerei mit traditionellem fleischerhandwerk",
    "fleischverkauf im hofladen und im onlineshop mit versand",
    "die fütterung der kulmbacher weideschweine",
    "ganzjährige freilandhaltung",
    "zucht alter vom aussterben bedrohter schweinrassen",
    "freitags von 16 bis 18 uhr",
    "samstags von 10",
    "kein soja",
    "antibiotika",
    "mangalica",
    "rotbunte husumer",
    "pata negra",
    "deutsche sattelschweine",
    "bunte bentheimer",
    "duroc",
    "8–10 wochen",
    "buchenholz",
    "glutamate",
    "015206188828",
    "hofbrief",
    "schlachtwoche",
    "kühlbox",
    "eggenreuth 3",
    "95326 kulmbach",
    "09221 3919676",
    "info@kulmbacher-weideschwein.de",
    "instagram",
    "schlammsuhle",
    "wechselweiden",
    "2017",
    "ard mediathek",
]

OLD_HEADINGS = [
    "Glückliche Schweine in Freilandhaltung",
    "Erlebnisbauernhof und Tiergestützte Therapie in",
    "Gutes Fleisch vom Weideschwein im Hofladen oder online kaufen",
    "Eigene Metzgerei mit traditionellem Fleischerhandwerk",
    "Fleischverkauf im Hofladen und im Onlineshop mit Versand",
    "Die Fütterung der Kulmbacher Weideschweine",
    "Ganzjährige Freilandhaltung",
    "Zucht alter vom Aussterben bedrohter Schweinrassen mit besonderer",
]


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def main():
    html = HTML.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    results = []

    def check(name, ok, detail=""):
        results.append((name, ok))
        print(("PASS" if ok else "FAIL"), "-", name, ("| " + str(detail) if detail else ""))

    check("index.html exists", HTML.is_file())
    check("lang=de", soup.html is not None and soup.html.get("lang") == "de")
    check("viewport meta", bool(soup.find("meta", attrs={"name": "viewport"})))
    check("title present", bool(soup.title and soup.title.string.strip()))
    check("meta description", bool(soup.find("meta", attrs={"name": "description"})))

    ids = {el.get("id") for el in soup.find_all(id=True)}
    missing_assets, missing_anchors = [], []
    for el in soup.find_all(["a", "img", "link", "script"]):
        ref = el.get("href") or el.get("src")
        if not ref:
            continue
        if ref.startswith("#"):
            if ref[1:] not in ids:
                missing_anchors.append(ref)
        elif re.match(r"^[a-z]+:", ref) or ref.startswith("//"):
            continue
        elif not (ROOT / ref).is_file():
            missing_assets.append(ref)
    check("all local assets exist", not missing_assets, missing_assets)
    check("all anchors resolve", not missing_anchors, missing_anchors)

    imgs = [el.get("src") for el in soup.find_all("img") if el.get("src") and not el["src"].startswith("http")]
    bad = []
    total = 0
    for i in imgs:
        p = ROOT / i
        total += p.stat().st_size
        if p.read_bytes()[:3] != b"\xff\xd8\xff":
            bad.append(i)
    check("all <img> are valid JPEG", not bad, f"{len(imgs)} imgs, {total // 1024} KB, bad={bad}")
    check("img total size sane (<8MB)", total < 8 * 1024 * 1024, f"{total / 1024 / 1024:.1f} MB")
    hero = soup.find("img", class_="hero__img")
    check("hero not lazy", hero is not None and hero.get("loading") != "lazy")

    new_text = norm(soup.get_text(" ", strip=True))
    missing_content = [r for r in REQUIRED_STRINGS if r not in new_text]
    check("content parity (key strings from old site)", not missing_content, f"missing: {missing_content}")

    new_headings = norm(" ".join(h.get_text(" ", strip=True) for h in soup.find_all(re.compile("^h[1-3]$"))))
    missing_h = [h for h in OLD_HEADINGS if norm(h)[:40] not in new_headings]
    check("all old H1-H3 headings present", not missing_h, f"missing: {missing_h}")

    check("template green #0B3318 in CSS", "#0B3318" in css)
    check("Anton font used", "Anton" in css and "Anton" in html)
    check("Didot heading stack", "Didot" in css)
    check("hero 96vh/85vh rule", "96vh" in css and "85vh" in css)
    check("announcement bar", bool(soup.find(class_="announcement")))
    check("dark green section", bool(soup.find(class_="section--green")))
    check("image-with-text sections >= 5", len(soup.find_all(class_="iwt")) >= 5, len(soup.find_all(class_="iwt")))
    check("card overlay 0.3", "rgba(0, 0, 0, 0.3)" in css)
    check("newsletter form", bool(soup.find("form", class_="newsletter__form")))
    check("footer with contact id", bool(soup.find("footer", id="kontakt")))
    check("6 nav cards", len(soup.find_all(class_="card")) == 6)
    check("media queries 999px & 749px", "max-width: 999px" in css and "max-width: 749px" in css)
    check("mobile nav toggle", bool(soup.find("button", class_="nav-toggle")))
    check("no fixed px width > 1200", not re.search(r"width:\s*[2-9]\d{3,}px", css))
    check("skip link", bool(soup.find(class_="skip-link")))

    import json
    import xml.etree.ElementTree as ET

    check("sitemap.xml parses and has <url>", (ROOT / "sitemap.xml").is_file() and bool(ET.parse(ROOT / "sitemap.xml").getroot().find(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url")))
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8") if (ROOT / "robots.txt").is_file() else ""
    check("robots.txt references sitemap", "sitemap.xml" in robots.lower())
    check("canonical link", bool(soup.find("link", rel="canonical")))
    check("og:title + og:image", bool(soup.find("meta", property="og:title")) and bool(soup.find("meta", property="og:image")))
    check("theme-color meta", bool(soup.find("meta", attrs={"name": "theme-color"})))
    ld = soup.find("script", type="application/ld+json")
    ld_ok = False
    if ld:
        try:
            ld_ok = json.loads(ld.string).get("@type") == "LocalBusiness"
        except Exception:
            ld_ok = False
    check("JSON-LD LocalBusiness", ld_ok)
    check("hero preload", bool(soup.find("link", rel="preload", href="assets/img/hero.jpg")))
    lazy_imgs = [i for i in soup.find_all("img") if i.get("loading") == "lazy"]
    check("all lazy imgs have decoding=async", all(i.get("decoding") == "async" for i in lazy_imgs), f"{len(lazy_imgs)} lazy imgs")

    nav_labels = ["home", "fleisch / shop", "zucht", "ferkelverkauf", "news", "galerie / videos", "geschichte", "kontakt"]
    missing_nav = [n for n in nav_labels if n not in new_text]
    check("all old nav labels present", not missing_nav, f"missing: {missing_nav}")
    missing_legal = [t for t in ["impressum", "datenschutz"] if t not in new_text]
    check("legal links (Impressum/Datenschutz) present", not missing_legal, f"missing: {missing_legal}")

    if os.environ.get("SKIP_EXTERNAL") != "1":
        ext = sorted({urljoin("https://www.kulmbacher-weideschwein.de/", a["href"]) for a in soup.find_all("a", href=True) if a["href"].startswith("http")})
        bad_links = []
        for u in ext:
            try:
                r = requests.head(u, timeout=20, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code == 429:
                    continue
                if r.status_code >= 400:
                    r2 = requests.get(u, timeout=20, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
                    if r2.status_code != 429 and r2.status_code >= 400:
                        bad_links.append((u, r2.status_code))
            except Exception as e:
                bad_links.append((u, repr(e)[:50]))
        check(f"external links OK ({len(ext)} checked)", not bad_links, bad_links)

    fails = [n for n, ok in results if not ok]
    print(f"\n=== SUMMARY: {len(results) - len(fails)} passed, {len(fails)} failed ===")
    if fails:
        print("FAILED:", fails)
        sys.exit(1)


if __name__ == "__main__":
    main()
