"""Counter items against each hero, for the "Kontry na …" / "… counter items" pages.

Usage: python3 -I site/counters.py docs   (downloads stats and icons, writes site/counters.json and docs/img/)

A hero's typical build: the items most of its players buy and keep, in buying order.

Data: deadlock-api `analytics/item-stats?bucket=enemy_hero`, matches of the last 14 days whose players
average Emissary or higher, the same source the app's advisor uses. An item's edge against a hero is
how many percentage points more often its buyers win against that hero than they do in general,
minus the same difference for all items of its price, so a hero that is weak against everything does
not lift every item. Small samples are pulled toward zero (K_ENEMY, as in the app).
"""
import json
import sys
import time
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.deadlock-api.com/v1"
DAYS = 14
MIN_BADGE = 61  # Emissary 1
K_ENEMY = 5000.0
SHOWN = 8
MIN_MATCHES = 2000  # an item needs this many matches against the hero to be shown
MIN_HERO_MATCHES = 200_000  # heroes with fewer item purchases against them are left out (new, rare)
BUILD = 8  # items in a hero's typical build
KEPT = 0.5  # an item sold in more than this share of matches is a lane item, not part of the build


def get(url, attempts=4):
    for n in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "deadlock-assist-site"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except OSError:
            if n == attempts - 1:
                raise
            time.sleep(2 ** (n + 1))


def get_json(url):
    return json.loads(get(url))


def slug(name):
    return name.lower().replace("&", "and").replace(" ", "-").replace("'", "")


def edges(rows, cost_of):
    """{enemy hero id: [(points, item id, matches)]} from item-stats rows bucketed by enemy hero."""
    total = defaultdict(lambda: [0.0, 0.0])
    vs = defaultdict(dict)
    for r in rows:
        total[r["item_id"]][0] += r["wins"]
        total[r["item_id"]][1] += r["matches"]
        vs[r["bucket"]][r["item_id"]] = (r["wins"], r["matches"])

    def by_price(pairs):
        t = defaultdict(lambda: [0.0, 0.0])
        for item, (w, m) in pairs:
            t[cost_of(item)][0] += w
            t[cost_of(item)][1] += m
        return t

    price_all = by_price(total.items())
    out = {}
    for hero, items in vs.items():
        price_vs = by_price(items.items())
        scored = []
        for item, (w, m) in items.items():
            if m < MIN_MATCHES or cost_of(item) is None:
                continue
            c = cost_of(item)
            base = price_vs[c][0] / price_vs[c][1] - price_all[c][0] / price_all[c][1]
            dev = (w / m - total[item][0] / total[item][1]) - base
            scored.append((100 * dev * m / (m + K_ENEMY), item, m))
        scored.sort(reverse=True)
        out[hero] = scored
    return out


def builds(rows, hero_matches, items_en):
    """{hero id: [(item id, share of the hero's matches, buy minute)]}: the items most players of the hero
    buy and keep, in the order they are bought."""
    by_hero = defaultdict(list)
    for r in rows:
        if r["item_id"] in items_en and r["matches"] and r["sold"] / r["matches"] <= KEPT:
            by_hero[r["bucket"]].append(r)
    out = {}
    for hero, rs in by_hero.items():
        n = hero_matches.get(hero)
        if not n:
            continue
        top = sorted(rs, key=lambda r: -r["matches"])[:BUILD]
        top.sort(key=lambda r: r["avg_buy_time_s"])
        out[hero] = [(r["item_id"], r["matches"] / n, r["avg_buy_time_s"] / 60) for r in top]
    return out


def main():
    out = Path(sys.argv[1])
    now = int(time.time())
    since = (now - DAYS * 86400) // 86400 * 86400
    rows = get_json(f"{API}/analytics/item-stats?bucket=enemy_hero&min_average_badge={MIN_BADGE}"
                    f"&min_matches=1&min_unix_timestamp={since}")
    own = get_json(f"{API}/analytics/item-stats?bucket=hero&min_average_badge={MIN_BADGE}"
                   f"&min_matches=1&min_unix_timestamp={since}")
    hero_matches = {h["hero_id"]: h["matches"] for h in get_json(
        f"{API}/analytics/hero-stats?min_average_badge={MIN_BADGE}&min_unix_timestamp={since}")}
    heroes = [h for h in get_json(f"{API}/assets/heroes") if h.get("player_selectable") and not h.get("disabled")]
    items_en = {i["id"]: i for i in get_json(f"{API}/assets/items") if i.get("shopable") and i.get("type") == "upgrade"}
    items_pl = {i["id"]: i for i in get_json(f"{API}/assets/items?language=polish")}
    cost_of = lambda i: items_en[i]["cost"] if i in items_en else None  # noqa: E731

    matches = defaultdict(float)
    for r in rows:
        matches[r["bucket"]] += r["matches"]
    found = edges(rows, cost_of)
    build_of = builds(own, hero_matches, items_en)

    img = out / "img"
    (img / "heroes").mkdir(parents=True, exist_ok=True)
    (img / "items").mkdir(parents=True, exist_ok=True)

    missing = []

    def icon(url, path):
        """Saves the icon next to the pages; the pages fall back to the remote URL while it is missing."""
        if url and not path.exists():
            if missing:  # the icon server is unreachable: do not wait on every icon
                missing.append(url)
                return url
            try:
                path.write_bytes(get(url, attempts=2))
            except OSError:
                missing.append(url)
        return url

    result = []
    used_items = set()
    for h in sorted(heroes, key=lambda h: h["name"]):
        if matches[h["id"]] < MIN_HERO_MATCHES:
            continue
        top = [(p, i, m) for p, i, m in found.get(h["id"], []) if p > 0][:SHOWN]
        build = build_of.get(h["id"], [])
        if len(top) < 4 or len(build) < BUILD:
            continue
        s = slug(h["name"])
        hero_img = icon(h["images"].get("icon_image_small_webp") or h["images"].get("icon_image_small"),
                        img / "heroes" / f"{s}.webp")
        used_items.update(i for _, i, _ in top)
        used_items.update(i for i, _, _ in build)
        result.append({
            "id": h["id"],
            "name": h["name"],
            "slug": s,
            "img": hero_img,
            "matches": round(matches[h["id"]]),
            "items": [{"id": i, "points": round(p, 2), "matches": round(m)} for p, i, m in top],
            "build": [{"id": i, "share": round(sh, 3), "min": round(mi, 1)} for i, sh, mi in build],
        })
    items = {}
    for i in sorted(used_items):
        it = items_en[i]
        item_img = icon(it.get("shop_image_webp") or it.get("image_webp") or it.get("image"), img / "items" / f"{i}.webp")
        items[str(i)] = {
            "img": item_img,
            "en": it["name"],
            "pl": items_pl.get(i, it)["name"],
            "cost": it["cost"],
            "slot": it.get("item_slot_type"),
        }
    day = datetime.fromtimestamp(now, timezone.utc).date().isoformat()
    data = {"date": day, "days": DAYS, "heroes": result, "items": items}
    Path(__file__).with_name("counters.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    print(f"{len(result)} heroes, {len(items)} items, data up to {day}")
    if missing:
        print(f"{len(missing)} icons not downloaded (pages use the remote URL for them)")


main()
