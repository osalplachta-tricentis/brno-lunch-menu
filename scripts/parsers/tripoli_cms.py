"""Parser for the shared "Tripoli recent & Omega" restaurant CMS.

Used by Potrefená husa Vaňkovka and Tripoli Vaňkovka — they run the identical
template. The homepage shows *today's* menu inline as one or more sections::

    <div class="bg-white ...">
      <div ...><h2>Menu – 9. 6.</h2></div>
      <div class="menu-one-day ...">
        <div class="flex ...">
          <div class="font-bold ...">MENU 1</div>      <- label (may be empty)
          <div class="flex-[1]">0,15 kg <b>Dish</b> ... 7</div>  <- dish
          <div class="text-right ms-auto">179 Kč</div>  <- price
        </div>
        ...
      </div>
    </div>

There are usually three sections: the dated daily menu, a "Týdenní nabídka"
(weekly specials) and "Nabídka baru" (drinks — skipped).
"""

from __future__ import annotations

from bs4 import BeautifulSoup

from models import MenuItem, RestaurantMenu

from ._util import normalize_space, split_allergens


def _has_class(token: str):
    return lambda tag: tag.name == "div" and token in (tag.get("class") or [])


def parse(raw: str, ctx: dict) -> RestaurantMenu:
    soup = BeautifulSoup(raw, "html.parser")
    menu = RestaurantMenu(name=ctx["name"], site_url=ctx["site_url"])

    for block in soup.select("div.menu-one-day"):
        section = block.find_parent(class_="bg-white")
        heading_el = section.find("h2") if section else None
        heading = normalize_space(heading_el.get_text()) if heading_el else ""

        # Drinks section — not lunch.
        if "bar" in heading.lower():
            continue

        is_daily = heading.lower().startswith("menu")
        if is_daily and not menu.menu_date_label:
            # "Menu – 9. 6." -> "9. 6."
            date = heading.split("–", 1)[-1].split("-", 1)[-1].strip()
            menu.menu_date_label = date or heading
        category = "" if is_daily else heading

        for row in block.find_all("div", recursive=False):
            price_el = row.find(_has_class("text-right"))
            dish_el = row.find(_has_class("flex-[1]"))
            if dish_el is None or price_el is None:
                continue
            label_el = row.find(_has_class("font-bold"))

            dish, allergens = split_allergens(dish_el.get_text(" "))
            price = normalize_space(price_el.get_text())
            if not dish or not price:
                continue

            menu.items.append(
                MenuItem(
                    name=dish,
                    price=price,
                    label=normalize_space(label_el.get_text()) if label_el else "",
                    category=category,
                    allergens=allergens,
                )
            )

    if not menu.items:
        menu.error = "No menu items found on the page (layout may have changed)."
    return menu
