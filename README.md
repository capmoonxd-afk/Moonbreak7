# Rave Signal

A small, static EDM news and releases radar. The site reads `data/latest.json`; GitHub Actions refreshes that feed every 30 minutes from the configured RSS sources and commits changed snapshots to Git.

## Local preview

Open `index.html` in a browser. To fetch current stories locally, run:

```powershell
python scripts/update_feed.py
```

Then serve the project folder with any static web server (for example `python -m http.server 8000`) and open `http://localhost:8000`.

## GitHub setup

1. Push this repository to GitHub.
2. Enable Actions for the repository. Run **Update EDM feed** once from the Actions tab for an immediate first scan; scheduled runs continue every 30 minutes.
3. In **Settings → Pages**, choose **Deploy from a branch**, then select `main` (or `master`) and `/ (root)`.

The workflow stores each changed feed snapshot in Git history. GitHub Pages serves the site. RSS content is summarized for display and linked to its original publisher.

## Sources

The starter configuration uses the EDM.com RSS feed at `https://edm.com/blog/feed/`. Add more feeds to `data/sources.json`.
