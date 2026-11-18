"""Parser for menicka.cz iframe menus (``menicka.cz/api/iframe/?id=…``).

Restaurant sites embed the menicka.cz iframe; its static HTML holds the whole
working week, one block per day::

    <div class='content'>
      <h2>Středa 18.11.2026 <span class='dnes'>&laquo; dnes</span></h2>
      <table class='menu'>
        <tr class="soup photomenu">
          <td colspan='2' class='food'>0, 25l Zelná polévka s klobásou</td>
          <td class='prize'>30 Kč</td>
        </tr>
        <tr class="main photomenu">
          <td class='no'>1. </td>
          <td class='food'>150g Zapečený kuřecí steak …</td>
          <td class='prize'>169 Kč</td>
        </tr> ...
      </table>
    </div> ...

We extract the block whose date matches today (Europe/Prague). There is no
fallback to another day: if today is missing, the card shows an error. A block
holding only the "no menu entered" placeholder row (weekends) counts as missing.

Labels: priced soup rows get "Polévka", priced mains their ``td.no`` number;
unpriced rows (e.g. a holiday notice) get no label.
"""

from __future__ import annotations

import re
from datetime import date

from bs4 import BeautifulSoup

from models import MenuItem, RestaurantMenu

from ._util import normalize_space

_DATE_RE = re.compile(r"(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})")
_PLACEHOLDER = "Pro tento den nebylo zadáno"
_NO_MENU = "No menu published for today."


def _text(el) -> str:
    return normalize_space(el.get_text(" ")) if el else ""


def parse(raw: str, ctx: dict) -> RestaurantMenu:
    today = ctx["today"]
    soup = BeautifulSoup(raw, "html.parser")
    menu = RestaurantMenu(name=ctx["name"], site_url=ctx["site_url"])

    days = soup.select("div.content")
    if not days:
        menu.error = "No menu sections found on the page (layout may have changed)."
        return menu

    for day in days:
        h2 = day.find("h2")
        if h2 is None:
            continue
        for marker in h2.select("span.dnes"):
            marker.extract()
        title = _text(h2)
        m = _DATE_RE.search(title)
        if m and date(int(m[3]), int(m[2]), int(m[1])) == today:
            break
    else:
        menu.error = _NO_MENU
        return menu

    menu.menu_date_label = title

    placeholder = False
    for tr in day.select("table.menu tr"):
        name = _text(tr.select_one("td.food"))
        if not name:
            continue
        if name.startswith(_PLACEHOLDER):
            placeholder = True
            continue
        price = _text(tr.select_one("td.prize"))
        if not price:
            label = ""
        elif "soup" in tr.get("class", []):
            label = "Polévka"
        else:
            label = _text(tr.select_one("td.no"))
        menu.items.append(MenuItem(name=name, price=price, label=label))

    if not menu.items and placeholder:
        menu.error = _NO_MENU
    elif not menu.items:
        menu.error = "Menu section for today was empty."
    return menu
