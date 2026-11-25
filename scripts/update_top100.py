import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://djmag.com/"
FIRST_YEAR, LAST_YEAR = 1995, 2026

class PollImages(HTMLParser):
    def __init__(self, year):
        super().__init__()
        self.year = str(year)
        self.entries = []
        self.seen = set()

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "img":
            return
        attrs = dict(attrs)
        alt = (attrs.get("alt") or "").strip()
        match = re.search(r"Poll\s+(\d{4})\s*:\s*(.+)$", alt, re.I)
        if not match or match.group(1) != self.year:
            return
        name = re.sub(r"\s+", " ", match.group(2)).strip()
        if not name or name.casefold() in self.seen:
            return
        self.seen.add(name.casefold())
        image = attrs.get("data-src") or attrs.get("data-original") or attrs.get("src") or ""
        self.entries.append({"rank": len(self.entries) + 1, "name": name, "avatar": urljoin(BASE, image) if image else ""})

def fetch_year(year):
    path = "top100djs" if year == LAST_YEAR else f"top100djs/{year}"
    request = Request(urljoin(BASE, path), headers={"User-Agent": "RaveSignal/1.0 (+https://github.com/capmoonxd-afk/Moonbreak7)"})
    with urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", "replace")
    parser = PollImages(year)
    parser.feed(html)
    if len(parser.entries) < 80:
        raise ValueError(f"Expected at least 80 DJ portraits for {year}; got {len(parser.entries)}")
    return parser.entries[:100]

years = {}
failures = []
for year in range(LAST_YEAR, FIRST_YEAR - 1, -1):
    try:
        years[str(year)] = fetch_year(year)
        print(f"{year}: saved {len(years[str(year)])} artists")
    except (HTTPError, URLError, TimeoutError, UnicodeError, ValueError) as error:
        failures.append(f"{year}: {error}")
        print(f"{year}: skipped ({error})")
if not years:
    raise SystemExit("No Top 100 rankings could be fetched; leaving existing archive unchanged.")
output = {"updated_at": datetime.now(timezone.utc).isoformat(timespec="minutes"), "source": "DJ Mag Top 100 DJs archive", "source_url": "https://djmag.com/top100djs", "years": years, "unavailable_years": failures}
target = ROOT / "data" / "top100.json"
target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Saved {len(years)} yearly rankings to {target}")

