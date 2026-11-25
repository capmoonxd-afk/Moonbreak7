# Rave Signal

An EDM news and releases radar with the annual DJ Mag Top 100 DJs archive. News reads `data/latest.json`; GitHub Actions refreshes it every 30 minutes. A separate workflow collects year-by-year rankings and portrait image links from DJ Mag, from 1995 onward.

## Local preview

Serve this folder with any static web server (for example `python -m http.server 8000`) and open `http://localhost:8000`. Run `python scripts/update_feed.py` for fresh news or `python scripts/update_top100.py` to refresh the ranking archive.

## GitHub

The Pages site is published from `main` and available at https://capmoonxd-afk.github.io/Moonbreak7/. News updates are committed automatically every 30 minutes. The DJ ranking archive is refreshed annually and can be started manually from the Actions tab.

## Sources

News feed: https://edm.com/blog/feed/ · DJ Mag Top 100 archive: https://djmag.com/top100djs
