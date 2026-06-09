"""Parser for Grand Kitchen Vlněna (``grandkitchenvlnena.cz``).

The page itself has no menu; it embeds a menubot.cz / PerfectCanteen feed served
as JavaScript::

    document.write("<section ...><h3 class=\"fly-dish-menu-title\">Úterý 9. 6.</h3>
      <ul class=\"fly-dish-menu-content\">
        <li>
          <div class=\"fly-dish-menu-description\"><h5>Dish <small>1a,9</small></h5></div>
          <div class=\"fly-dish-menu-price\">45 Kč</div>
        </li> ...
      </ul> ...")

The feed carries the whole week; we extract the section whose date matches
today (Europe/Prague), falling back to the first day if none matches.
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup

from models import MenuItem, RestaurantMenu

from ._util import normalize_space

_DOC_WRITE_RE = re.compile(r'document\.write\("(.*)"\)\s*;?\s*$', re.S)
_DATE_RE = re.compile(r"(\d{1,2})\.\s*(\d{1,2})\.")


def _unwrap_js(raw: str) -> str:
    """Pull the HTML string out of the ``document.write("…")`` wrapper."""
    m = _DOC_WRITE_RE.search(raw.strip())
    payload = m.group(1) if m else raw
    return (
        payload.replace('\\"', '"')
        .replace("\\/", "/")
        .replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace("\\\\", "\\")
    )


def parse(raw: str, ctx: dict) -> RestaurantMenu:
    today = ctx.get("today")
    soup = BeautifulSoup(_unwrap_js(raw), "html.parser")
    menu = RestaurantMenu(name=ctx["name"], site_url=ctx["site_url"])

    days: list[tuple[str, object]] = []  # (title, <ul> content)
    for title_el in soup.select("h3.fly-dish-menu-title"):
        content = title_el.find_next("ul", class_="fly-dish-menu-content")
        if content is not None:
            days.append((normalize_space(title_el.get_text()), content))

    if not days:
        menu.error = "No menu sections found in the feed (format may have changed)."
        return menu

    chosen_title, chosen_ul = days[0]
    if today is not None:
        for title, content in days:
            m = _DATE_RE.search(title)
            if m and int(m.group(1)) == today.day and int(m.group(2)) == today.month:
                chosen_title, chosen_ul = title, content
                break

    menu.menu_date_label = chosen_title

    for li in chosen_ul.select("li"):
        desc_el = li.select_one(".fly-dish-menu-description")
        price_el = li.select_one(".fly-dish-menu-price")
        if desc_el is None:
            continue
        small = desc_el.find("small")
        allergens = normalize_space(small.get_text()) if small else ""
        if small:
            small.extract()
        dish = normalize_space(desc_el.get_text(" "))
        price = normalize_space(price_el.get_text()) if price_el else ""
        if not dish:
            continue
        menu.items.append(MenuItem(name=dish, price=price, allergens=allergens))

    if not menu.items:
        menu.error = "Menu section for today was empty."
    return menu
