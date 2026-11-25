import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "data/sources.json").read_text(encoding="utf-8"))
items = []
def clean(value):
    value = re.sub(r"<[^>]*>", " ", value or "")
    return re.sub(r"\s+", " ", value).strip()
for source in CONFIG["sources"]:
    req = Request(source["url"], headers={"User-Agent": "RaveSignal/1.0 (RSS reader)"})
    with urlopen(req, timeout=25) as response:
        root = ET.fromstring(response.read())
    for node in root.findall(".//item"):
        title = clean(node.findtext("title"))
        link = clean(node.findtext("link"))
        if not title or not link:
            continue
        raw_date = clean(node.findtext("pubDate"))
        try:
            dt = parsedate_to_datetime(raw_date)
            date_label = dt.astimezone(timezone.utc).strftime("%b %d · %H:%M UTC")
            iso_date = dt.astimezone(timezone.utc).isoformat()
        except Exception:
            date_label, iso_date = "RECENT", ""
        desc = clean(node.findtext("description"))
        items.append({"title": title, "link": link, "summary": desc[:240], "source": source["name"], "date_label": date_label, "published": iso_date})
items.sort(key=lambda x: x["published"], reverse=True)
output = {"updated_at": datetime.now(timezone.utc).isoformat(timespec="minutes"), "items": items[:CONFIG.get("max_items", 100)]}
(ROOT / "data/latest.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Saved {len(output['items'])} stories")
