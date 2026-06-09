"""Render a list of :class:`RestaurantMenu` into a single static HTML page."""

from __future__ import annotations

from datetime import datetime
from html import escape

from models import RestaurantMenu

_CSS = """
:root{--bg:#f4f5f7;--card:#fff;--ink:#1b1b1b;--muted:#6b7280;--accent:#b8860b;--line:#e5e7eb;}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
  background:var(--bg);color:var(--ink);line-height:1.45}
header{padding:2rem 1rem 1rem;text-align:center}
header h1{margin:0 0 .3rem;font-size:1.7rem}
header .sub{color:var(--muted);font-size:.9rem}
main{max-width:1200px;margin:0 auto;padding:1rem;
  display:grid;gap:1.25rem;grid-template-columns:repeat(auto-fill,minmax(330px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:1.1rem 1.2rem;box-shadow:0 1px 2px rgba(0,0,0,.04);display:flex;flex-direction:column}
.card h2{margin:0;font-size:1.15rem}
.card h2 a{color:inherit;text-decoration:none}
.card h2 a:hover{text-decoration:underline}
.date{color:var(--accent);font-weight:600;font-size:.85rem;margin:.15rem 0 .8rem}
.cat{margin:.9rem 0 .35rem;font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.item{display:flex;gap:.75rem;padding:.4rem 0;border-top:1px dashed var(--line)}
.item:first-of-type{border-top:none}
.item .body{flex:1}
.item .label{font-weight:700;font-size:.78rem;color:var(--accent);display:block}
.item .name{font-size:.92rem}
.item .alg{color:var(--muted);font-size:.72rem}
.item .price{white-space:nowrap;font-weight:600;font-size:.9rem}
.err{color:#b91c1c;background:#fef2f2;border:1px solid #fecaca;border-radius:8px;
  padding:.6rem .8rem;font-size:.88rem}
footer{text-align:center;color:var(--muted);font-size:.8rem;padding:1.5rem 1rem 2.5rem}
""".strip()


def _render_card(menu: RestaurantMenu) -> str:
    head = (
        f'<h2><a href="{escape(menu.site_url)}" target="_blank" '
        f'rel="noopener">{escape(menu.name)}</a></h2>'
    )
    date = f'<div class="date">{escape(menu.menu_date_label)}</div>' if menu.menu_date_label else ""

    if menu.error:
        body = f'<div class="err">{escape(menu.error)}</div>'
        return f'<section class="card">{head}{date}{body}</section>'

    rows: list[str] = []
    current_cat = None
    for item in menu.items:
        if item.category != current_cat:
            current_cat = item.category
            if current_cat:
                rows.append(f'<div class="cat">{escape(current_cat)}</div>')
        label = f'<span class="label">{escape(item.label)}</span>' if item.label else ""
        alg = f' <span class="alg">({escape(item.allergens)})</span>' if item.allergens else ""
        price = f'<div class="price">{escape(item.price)}</div>' if item.price else ""
        rows.append(
            '<div class="item"><div class="body">'
            f'{label}<span class="name">{escape(item.name)}</span>{alg}'
            f"</div>{price}</div>"
        )
    return f'<section class="card">{head}{date}{"".join(rows)}</section>'


def render_page(menus: list[RestaurantMenu], generated_at: datetime) -> str:
    cards = "\n".join(_render_card(m) for m in menus)
    stamp = generated_at.strftime("%A %d.%m.%Y %H:%M")
    return f"""<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Obědové menu — Brno / Vaňkovka</title>
<style>{_CSS}</style>
</head>
<body>
<header>
  <h1>🍽️ Obědové menu — Vlněna a okolí</h1>
  <div class="sub">Aktualizováno {escape(stamp)} (čas Brno)</div>
</header>
<main>
{cards}
</main>
<footer>Generováno automaticky z webů restaurací. Ceny a dostupnost ověřte na místě.</footer>
</body>
</html>
"""
