"""Unified data model shared by every restaurant parser.

A parser's only job is to turn a fetched page (HTML or JS feed) into a
``RestaurantMenu``. The runner and renderer never need to know which site a
menu came from — they only deal with these dataclasses.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MenuItem:
    """A single line on the menu."""

    name: str
    """Dish description, e.g. ``"0,15 kg Kuřecí medailonky v kari těstíčku"``."""

    price: str = ""
    """Price exactly as shown, e.g. ``"179 Kč"``. Empty if not priced."""

    label: str = ""
    """Short per-row label such as ``"MENU 1"``, ``"TIP"`` or ``"Polévka"``."""

    category: str = ""
    """Section heading the item belongs to, e.g. ``"Týdenní nabídka"``."""

    allergens: str = ""
    """Allergen codes if the site lists them, e.g. ``"1,3,7"``."""


@dataclass
class RestaurantMenu:
    """Everything we present for one restaurant on the output page."""

    name: str
    site_url: str
    menu_date_label: str = ""
    """Human label for what the menu covers, e.g. ``"9. 6."`` or a week range."""

    items: list[MenuItem] = field(default_factory=list)
    error: str = ""
    """Set when fetching or parsing failed; the card shows this instead of items."""

    @property
    def ok(self) -> bool:
        return not self.error and bool(self.items)
