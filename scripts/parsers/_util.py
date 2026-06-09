"""Helpers shared across parsers."""

from __future__ import annotations

import re

# Allergen codes trail a dish, e.g. "... a nudlemi 1,3,7,9" or "1a,9,10,12".
# A code is digits optionally followed by a letter (1a, 1b1c gets normalised by
# the source anyway); the run may contain stray double commas ("1,,3").
_ALLERGEN_RE = re.compile(r"\s*((?:\d+[a-z]?)(?:\s*,+\s*(?:\d+[a-z]?)?)*)\s*$", re.I)


def normalize_space(text: str) -> str:
    """Collapse all whitespace (incl. non-breaking spaces) to single spaces."""
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def split_allergens(text: str) -> tuple[str, str]:
    """Split a dish string into ``(dish, allergens)``.

    The allergen codes (if any) are stripped from the tail and returned
    separately. When nothing looks like an allergen list the whole string comes
    back as the dish with an empty allergen string.
    """
    text = normalize_space(text)
    m = _ALLERGEN_RE.search(text)
    if not m:
        return text, ""
    codes = m.group(1)
    # Guard against eating a plain trailing number that is part of the dish
    # (e.g. "10°"); require at least one digit and that something precedes it.
    dish = text[: m.start()].strip(" ,")
    if not dish:
        return text, ""
    codes = re.sub(r",\s*,+", ",", codes).strip(" ,")
    return dish, codes
