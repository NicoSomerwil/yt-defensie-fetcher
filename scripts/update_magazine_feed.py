#!/usr/bin/env python3
"""Build a JSON feed with the latest editions of six Defensie magazines."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


BASE_URL = "https://www.defensie.nl"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "defensie-magazines.json"
CSV_OUTPUT = Path(__file__).resolve().parents[1] / "data" / "defensie_magazines.csv"
MAGAZINES = (
    ("Defensiekrant", "defensiekrant"),
    ("Alle Hens", "alle-hens"),
    ("Landmacht", "landmacht"),
    ("de Vliegende Hollander", "de-vliegende-hollander"),
    ("KMarMagazine", "kmarmagazine"),
    ("Materieelgezien", "materieelgezien"),
)


class FirstEditionParser(HTMLParser):
    def __init__(self, slug: str, year: int) -> None:
        super().__init__(convert_charrefs=True)
        self.pattern = re.compile(rf"^/magazines/{re.escape(slug)}/{year}/editie-([^/?#]+)$")
        self.depth = 0
        self.item: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if self.item is None and tag == "a":
            href = values.get("href") or ""
            match = self.pattern.match(href)
            if match:
                self.item = {"href": href, "edition": match.group(1), "image": ""}
                self.depth = 1
                return

        if self.item is not None and self.depth:
            self.depth += 1
            if tag == "img" and not self.item["image"]:
                self.item["image"] = values.get("src") or ""

    def handle_endtag(self, tag: str) -> None:
        if self.item is not None and self.depth:
            self.depth -= 1


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "KVEO feed updater/1.0 (+https://kveo.nl)"})
    with urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status} for {url}")
        return response.read().decode("utf-8")


def latest_edition(label: str, slug: str, current_year: int) -> dict[str, object]:
    last_error = "geen editie gevonden"
    for year in (current_year, current_year - 1):
        overview_url = f"{BASE_URL}/magazines/{slug}/{year}"
        try:
            html = fetch_text(overview_url)
        except (HTTPError, URLError, TimeoutError, RuntimeError) as exc:
            last_error = str(exc)
            continue

        parser = FirstEditionParser(slug, year)
        parser.feed(html)
        if not parser.item:
            last_error = f"geen editie gevonden op {overview_url}"
            continue

        image = urljoin(overview_url, parser.item["image"])
        if not image:
            raise RuntimeError(f"geen omslagafbeelding gevonden voor {label}")

        edition = parser.item["edition"]
        return {
            "id": slug,
            "title": label,
            "edition": f"Editie {edition}",
            "year": year,
            "url": urljoin(overview_url, parser.item["href"]),
            "image": image,
            "overview_url": f"{BASE_URL}/magazines/{slug}",
        }

    raise RuntimeError(f"{label}: {last_error}")


def main() -> None:
    current_year = datetime.now(timezone.utc).year
    items = [latest_edition(label, slug, current_year) for label, slug in MAGAZINES]
    existing = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else {}
    payload = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": f"{BASE_URL}/magazines",
        "items": items,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    changed = existing.get("items") != items or not CSV_OUTPUT.exists()

    if existing.get("items") != items:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=("titel", "editie", "jaar", "link", "afbeelding"),
        )
        writer.writeheader()
        for item in items:
            writer.writerow(
                {
                    "titel": item["title"],
                    "editie": item["edition"],
                    "jaar": item["year"],
                    "link": item["url"],
                    "afbeelding": item["image"],
                }
            )

    if changed:
        print(f"Feeds bijgewerkt: {OUTPUT} en {CSV_OUTPUT} ({len(items)} magazines)")
    else:
        print("Geen wijzigingen in de nieuwste edities.")


if __name__ == "__main__":
    main()
