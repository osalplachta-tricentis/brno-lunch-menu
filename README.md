# Brno lunch menu

Aggregates the daily lunch menus of a few restaurants around Vaňkovka (Brno)
into a single static HTML page, published automatically to GitHub Pages every
working day.

**Live page:** https://osalplachta-tricentis.github.io/brno-lunch-menu/

## How it works

```
restaurants.json                # which restaurants to scrape + which parser to use
scripts/
  main.py                       # runner: load config → fetch → parse → render
  fetcher.py                    # HTTP GET with a browser User-Agent
  models.py                     # MenuItem / RestaurantMenu (the unified form)
  render.py                     # builds the static HTML page
  parsers/
    __init__.py                 # parser-name → function registry
    tripoli_cms.py              # Potrefená husa + Tripoli (shared CMS)
    delitree.py                 # Delitree Bistro
    grandkitchen.py             # Grand Kitchen (menubot.cz feed)
output/                         # generated page (git-ignored)
```

Each restaurant in `restaurants.json` names a `parser`. A parser fetches one
site and returns a `RestaurantMenu` (a list of `MenuItem`s) in a unified shape,
so the runner and renderer never care which site a menu came from.

## Adding a restaurant

1. Add an entry to `restaurants.json`:
   ```json
   {
     "name": "Restaurant name",
     "site_url": "https://example.cz/",      // linked from the page
     "source_url": "https://example.cz/menu", // actually fetched & parsed
     "parser": "tripoli_cms",                 // an existing parser name
     "menu_kind": "daily"
   }
   ```
2. If the site uses a layout no existing parser understands, add a module under
   `scripts/parsers/` exposing `parse(raw, ctx) -> RestaurantMenu` and register
   it in `scripts/parsers/__init__.py`.

The `ctx` dict passed to a parser contains `name`, `site_url`, `today`
(a `date` in Europe/Prague) and the raw `config` entry.

## Running locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/main.py            # writes output/index.html
# open output/index.html in a browser
```

A failing site never sinks the page — its card shows an error and the run
continues.

## Automation

`.github/workflows/publish.yml` runs `python scripts/main.py --output-dir _site`
on a schedule and deploys `_site` to GitHub Pages.

- **Schedule:** `cron: "0 7 * * 1-5"` — 07:00 UTC on working days.
- GitHub cron is **UTC only**. 07:00 UTC is **09:00 Brno in summer (CEST)** and
  **08:00 in winter (CET)**. Adjust the cron if year-round 09:00 matters.
- Can also be triggered manually via *Actions → Publish lunch menu → Run
  workflow*.

### One-time setup

Pages must use the **GitHub Actions** source (Settings → Pages → Build and
deployment → Source: *GitHub Actions*). This repo's workflow then deploys on
its own; no secrets are required.
