"""Parser registry.

Each restaurant in ``restaurants.json`` names a ``parser``. That name maps to a
``parse(raw, ctx) -> RestaurantMenu`` callable here. Adding a restaurant that
uses an existing site type needs no code — only a JSON entry. A genuinely new
site type means a new module registered in ``REGISTRY``.
"""

from __future__ import annotations

from collections.abc import Callable

from . import delitree, grandkitchen, tripoli_cms

# parser name -> callable(raw: str, ctx: dict) -> RestaurantMenu
REGISTRY: dict[str, Callable] = {
    "tripoli_cms": tripoli_cms.parse,
    "delitree": delitree.parse,
    "grandkitchen": grandkitchen.parse,
}


def get(name: str) -> Callable:
    try:
        return REGISTRY[name]
    except KeyError:
        raise KeyError(
            f"Unknown parser {name!r}. Known parsers: {sorted(REGISTRY)}"
        ) from None
