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

class RankingCards(HTMLParser):
    """Read rank, artist name and image URL from each official DJ Mag card."""
    def __init__(self):
        super().__init__()
        self.entries = []
        self.card = None
        self.rank_depth = 0
        self.name_depth = 0
        self.rank_text = []
        self.name_text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = (attrs.get("class") or "").split()
        if tag.lower() == "article" and any(value.startswith("djm-26-card") for value in classes):
            self.card = {"rank": "", "name": "", "avatar": ""}
            self.rank_depth = self.name_depth = 0
            self.rank_text, self.name_text = [], []
        if self.card is None:
            return
        if tag.lower() == "div" and "djm-26-card__rank" in classes:
            self.rank_depth += 1
        if tag.lower() in ("h2", "h3") and "djm-26-card__title" in classes:
            self.name_depth += 1
        if tag.lower() == "img" and not self.card["avatar"]:
            src = attrs.get("data-src") or attrs.get("src") or ""
            if src:
                self.card["avatar"] = urljoin(BASE, src)
        if tag.lower() == "source" and not self.card["avatar"]:
            srcset = attrs.get("srcset") or ""
            src = srcset.split(",", 1)[0].strip().split(" ", 1)[0]
            if src:
                self.card["avatar"] = urljoin(BASE, src)

    def handle_data(self, data):
        if self.card is None:
            return
        if self.rank_depth:
            self.rank_text.append(data)
        if self.name_depth:
            self.name_text.append(data)

    def handle_endtag(self, tag):
        if self.card is None:
            return
        if tag.lower() == "div" and self.rank_depth:
            self.rank_depth -= 1
            if self.rank_depth == 0:
                self.card["rank"] = " ".join(self.rank_text)
        if tag.lower() in ("h2", "h3") and self.name_depth:
            self.name_depth -= 1
            if self.name_depth == 0:
                self.card["name"] = " ".join(self.name_text)
        if tag.lower() == "article":
            name = re.sub(r"\s+", " ", self.card["name"]).strip()
            rank_match = re.search(r"\d+", self.card["rank"])
            if name and rank_match:
                self.entries.append({"rank": int(rank_match.group()), "name": name, "avatar": self.card["avatar"]})
            self.card = None

def fetch_year(year):
    path = "top100djs" if year == LAST_YEAR else f"top100djs/{year}"
    request = Request(urljoin(BASE, path), headers={"User-Agent": "RaveSignal/1.0 (+https://github.com/capmoonxd-afk/Moonbreak7)"})
    with urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", "replace")
    parser = RankingCards()
    parser.feed(html)
    entries = sorted(parser.entries, key=lambda item: item["rank"])
    if len(entries) < 80:
        raise ValueError(f"Expected at least 80 ranking cards for {year}; got {len(entries)}")
    return entries[:100]

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
