"""Parser for Delitree Bistro (``delitreebistro.cz/obedove-menu/``).

A weekly fixed menu (same all week). The dishes live in a price-list table::

    <h1><strong>8.6. - 12.6.</strong></h1>
    <div class="mt mt-pricelist ...">
      <div class="mt-i ...">
        <div class="mt-i-c ...">
          <div class="b b-text ...">... 🍵 <strong>Dish</strong>, ...</div>  <- dish
          <div class="b b-text ..."><strong>49 Kč</strong></div>             <- price
        </div>
      </div>
      ...
    </div>
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup

from models import MenuItem, RestaurantMenu

from ._util import normalize_space, split_allergens

# e.g. "8.6. - 12.6." or "8. 6. – 12. 6."
_RANGE_RE = re.compile(r"\d+\.\s*\d*\.?\s*[-–—]\s*\d+\.\s*\d*\.?")


def parse(raw: str, ctx: dict) -> RestaurantMenu:
    soup = BeautifulSoup(raw, "html.parser")
    menu = RestaurantMenu(name=ctx["name"], site_url=ctx["site_url"])

    for h in soup.find_all(["h1", "h2", "h3"]):
        text = normalize_space(h.get_text())
        if _RANGE_RE.search(text):
            menu.menu_date_label = text
            break

    # The menu is split across several price-list blocks (soups, mains, pasta,
    # salads); read items from all of them.
    pricelists = soup.select("div.mt-pricelist") or [soup]
    items = [it for pl in pricelists for it in pl.select("div.mt-i")]
    for item in items:
        blocks = [normalize_space(b.get_text(" ")) for b in item.select("div.b-text")]
        blocks = [b for b in blocks if b]
        price = next((b for b in blocks if "Kč" in b), "")
        dish_text = next((b for b in blocks if "Kč" not in b), "")
        if not dish_text or not price:
            continue
        dish, allergens = split_allergens(dish_text)
        menu.items.append(MenuItem(name=dish, price=price, allergens=allergens))

    if not menu.items:
        menu.error = "No menu items found on the page (layout may have changed)."
    return menu
