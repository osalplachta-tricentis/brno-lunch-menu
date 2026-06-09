"""Runner: load config, fetch + parse each restaurant, render the static page.

Usage::

    python scripts/main.py [--config restaurants.json] [--output-dir output]

Each restaurant is fetched and parsed independently: a failure produces a card
with an error message rather than aborting the whole page. Failures are also
emitted as ``::warning::`` lines so they surface in the GitHub Actions log.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# Make sibling modules importable whether run as "python scripts/main.py" or
# from inside the scripts/ directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import parsers  # noqa: E402
from fetcher import fetch  # noqa: E402
from models import RestaurantMenu  # noqa: E402
from render import render_page  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
BRNO_TZ = ZoneInfo("Europe/Prague")


def build_menu(cfg: dict, today) -> RestaurantMenu:
    name = cfg.get("name", "?")
    site_url = cfg.get("site_url", cfg.get("source_url", ""))
    try:
        parse = parsers.get(cfg["parser"])
        raw = fetch(cfg["source_url"])
        ctx = {"name": name, "site_url": site_url, "today": today, "config": cfg}
        return parse(raw, ctx)
    except Exception as exc:  # noqa: BLE001 — one bad site must not sink the page
        return RestaurantMenu(name=name, site_url=site_url, error=f"{type(exc).__name__}: {exc}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the Brno lunch-menu page.")
    ap.add_argument("--config", type=Path, default=REPO_ROOT / "restaurants.json")
    ap.add_argument("--output-dir", type=Path, default=REPO_ROOT / "output")
    args = ap.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    restaurants = config["restaurants"]

    now = datetime.now(BRNO_TZ)
    today = now.date()

    menus: list[RestaurantMenu] = []
    failures = 0
    for cfg in restaurants:
        menu = build_menu(cfg, today)
        menus.append(menu)
        if menu.ok:
            print(f"  ok   {menu.name}: {len(menu.items)} item(s)")
        else:
            failures += 1
            reason = menu.error or "no items"
            print(f"  FAIL {menu.name}: {reason}")
            print(f"::warning title=Menu failed::{menu.name}: {reason}")

    html = render_page(menus, now)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    out = args.output_dir / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out} ({len(menus) - failures}/{len(menus)} restaurants OK)")

    # Always exit 0: a partial page is still worth publishing. Failures are
    # visible on the page and as warnings above.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
