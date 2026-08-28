#!/usr/bin/env python3
"""Deterministic compliance, truth, accessibility, and asset gate."""
from __future__ import annotations
import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
ORIGINALS = ROOT / "photos/original"
OPTIMIZED = ROOT / "photos/optimized"

def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)

source = HTML.read_text(encoding="utf-8")
doc = BeautifulSoup(source, "html.parser")
text = re.sub(r"\s+", " ", doc.get_text(" ", strip=True))

required = {
    "identity": ("4038 Northlight Dr, Unit 1506", "Naples Winterpark IV, A Condominium", "63700800000"),
    "price and status": ("$259,900", "For Sale", "2 Beds", "2 Baths", "1,234"),
    "association": ("$1,850 per quarter", "Application fee: $150", "Association approval required; allow 1–2 weeks", "membership: yes, $0 additional"),
    "flood and as-is": ("Flood Zone AE", "12021C0394J", "Sold AS-IS"),
    "brokerage": ("Marzucco Real Estate", "DeShawn Robinson, Broker", "BK3335121", "239-776-5194"),
    "MLS": ("226030364", "A12079628", "TB8542303"),
    "fair housing": ("Equal Housing Opportunity", "Information deemed reliable but not guaranteed. Buyer to verify independently."),
    "image disclosure": ("No images are virtually staged.",),
    "view truth": ("Waterfront No", "View Lake"),
    "structural scope": ("Not subject to Florida milestone inspection or SIRS requirements, which apply at three stories and above.",),
}
for category, strings in required.items():
    for string in strings:
        if string not in text:
            fail(f"{category} missing exact text: {string}")
    print(f"PASS: {category}")

for forbidden in ("FHA", "VA financing", "pickleball", "clubhouse", "clubroom", "jog path", "piping", "permit"):
    if re.search(rf"\b{re.escape(forbidden)}\b", text, re.I):
        fail(f"forbidden public claim present: {forbidden}")
print("PASS: forbidden/confidential public-copy claims absent")

included = doc.select_one("#included")
if included is None:
    fail("missing protected #included selector")
included_text = included.get_text(" ", strip=True).lower()
for excluded in ("electricity", "water", "sewer", "internet", "interior pest"):
    if excluded in included_text:
        fail(f"unverified fee inclusion present: {excluded}")
for selector in ("#included", "#details", "#disclosures", "#contact", "footer"):
    if doc.select_one(selector) is None:
        fail(f"missing protected selector {selector}")
print("PASS: protected regions and fee exclusion gate")

originals = sorted(ORIGINALS.glob("*.jpg"))
if len(originals) != 57:
    fail(f"expected 57 retained originals, found {len(originals)}")
for original in originals:
    widths = (480, 960, 1600, 1920) if original.stem == "mls-01" else (480, 960, 1600)
    for width in widths:
        for ext in ("jpg", "webp"):
            candidate = OPTIMIZED / f"{original.stem}-{width}.{ext}"
            if not candidate.is_file(): fail(f"missing derivative {candidate.name}")
            ceiling = 120_000 if width == 480 else 400_000
            if candidate.stat().st_size >= ceiling: fail(f"{candidate.name} is {candidate.stat().st_size} bytes; ceiling is <{ceiling}")
print("PASS: 57 originals retained; 344 responsive derivatives meet byte ceilings")

gallery = doc.select("#gallery img")
if len(gallery) < 12: fail("gallery is unexpectedly sparse")
for image in gallery:
    for attr in ("src", "srcset", "sizes", "width", "height", "loading", "decoding", "alt"):
        if not image.get(attr): fail(f"gallery image missing {attr}")
    if image["loading"] != "lazy" or image["decoding"] != "async": fail("gallery loading strategy incorrect")
hero = doc.select_one("#hero img")
if hero is None or hero.get("loading") == "lazy" or hero.get("fetchpriority") != "high": fail("hero priority incorrect")
if doc.select_one('link[rel="preload"][as="image"][fetchpriority="high"]') is None: fail("hero preload missing")
print("PASS: responsive image attributes and LCP priority")

tour = doc.select_one('#virtual-tour iframe')
tour_url = "https://lacasatour.com/property/4038-northlight-dr-1506-naples-fl-34112/ub"
if tour is None: fail("virtual tour iframe missing")
for attr in ("width", "height", "title"):
    if not tour.get(attr): fail(f"virtual tour iframe missing {attr}")
if tour.get("src") != tour_url or tour.get("loading") != "lazy": fail("virtual tour URL/loading strategy incorrect")
fallback = doc.select_one(f'#virtual-tour a[href="{tour_url}"]')
if fallback is None: fail("virtual tour fallback link missing")
print("PASS: branded lazy virtual tour has dimensions, accessible title, and fallback link")

if len(doc.find_all("h1")) != 1: fail("expected exactly one h1")
if doc.select_one("#stickyCta") is None: fail("sticky CTA missing")
css = (ROOT / "assets/site.css").read_text()
js = (ROOT / "assets/site.js").read_text()
if "prefers-reduced-motion" not in css or "IntersectionObserver" not in js: fail("motion/reveal gate missing")
if re.search(r"[\U0001F300-\U0001FAFF]", source): fail("emoji present")
if "openstreetmap.org" not in js or "createElement(\"iframe\")" not in js: fail("lazy map implementation missing")
print("PASS: semantics, zero emoji, sentinel reveal, reduced motion, sticky CTA, and lazy map")
print("VERDICT: PASS")
