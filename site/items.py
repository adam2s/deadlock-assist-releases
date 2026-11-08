"""Every shop item with its description and stats, for the "Przedmioty" / "Items" pages.

Usage: python3 -I site/items.py docs   (downloads items, stats and icons, writes site/items.json and docs/img/)

Text: deadlock-api `assets/items` in English and Polish, the same tooltip the game and the app's
"Dane gry" tab show (sections, their text and numbers).
Stats: deadlock-api `analytics/item-stats?bucket=hero`, matches of the last 14 days whose players average
Emissary or higher, the same window as the counter pages. For each item: how many players buy it, how
often they win, when they buy it, how many sell it later, and the heroes whose players buy it most.
"""
import html
import json
import re
import sys
import time
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.deadlock-api.com/v1"
DAYS = 14
MIN_BADGE = 61  # Emissary 1
HEROES_SHOWN = 8  # heroes listed on an item page
MIN_HERO_MATCHES = 300  # a hero needs this many players with the item to be listed
SECTION_ORDER = ["innate", "passive", "active"]


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
    """Same as the counter pages for plain names; anything else that is not a letter or digit becomes a dash."""
    s = name.lower().replace("&", "and").replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def game_text(src):
    """The API's HTML-ish tooltip text as safe HTML: highlights become <strong>, <br> stays, icons and
    template tokens go (as in the app's parseGameText)."""
    if not src:
        return ""
    s = re.sub(r"<svg[\s\S]*?</svg>", "", src, flags=re.I)
    s = re.sub(r"<img[^>]*>", "", s, flags=re.I)
    s = re.sub(r"\{[a-z]:[^}]*\}", "", s)
    s = re.sub(r"#\|[^|#]*\|#", "", s)
    out, stack, last = [], [], 0

    def push(text):
        text = html.unescape(text).replace(" ", " ")
        if not text:
            return
        t = html.escape(text, quote=False)
        out.append(f"<strong>{t}</strong>" if any(stack) else t)

    for m in re.finditer(r'<br\s*/?>|<span\s+class="([^"]*)"\s*>|</span>|<[^>]+>', s, flags=re.I):
        push(s[last:m.start()])
        last = m.end()
        tag = m.group(0).lower()
        if tag.startswith("<br"):
            out.append("<br>")
        elif tag.startswith("<span"):
            stack.append("highlight" in (m.group(1) or ""))
        elif tag == "</span>":
            if stack:
                stack.pop()
    push(s[last:])
    text = "".join(out).replace("</strong><strong>", "")
    text = re.sub(r"^(\s*<br>)+|(<br>\s*)+$", "", text.strip())
    return re.sub(r"(<br>\s*){3,}", "<br><br>", text).strip()


def number(v):
    """Number part of an API value ("7m" → 7), None when there is none (as parseFloat in the app)."""
    m = re.match(r"\s*[-+]?(\d+\.?\d*|\.\d+)", "" if v is None else str(v))
    return float(m.group(0)) if m else None


def trim(n):
    r = round(n * 100) / 100
    return str(int(r)) if r == int(r) else str(r)


def stat(p):
    """[label, value] of one tooltip number ("Czas odnowienia", "30 s"), or None for unlabelled, zero or
    disabled ones (as the app's formatProperty)."""
    if not p or not p.get("label"):
        return None
    n = number(p.get("value"))
    if n is None or n == 0:
        return None
    if p.get("disable_value") is not None and number(p["disable_value"]) == n:
        return None
    prefix = p.get("prefix") or ""
    sign = "+" if "{s:sign}" in prefix and n > 0 else ""
    prefix = prefix.replace("{s:sign}", "")
    label = re.sub(r"#\|[^|#]*\|#", "", p["label"]).strip()
    return [label, f"{sign}{prefix}{trim(n)}{p.get('postfix') or ''}".strip()]


def sections(item):
    """The tooltip as [{type, blocks: [{text, stats, extra}]}]; the plain description when there is none."""
    props = item.get("properties") or {}
    secs = sorted(item.get("tooltip_sections") or [],
                  key=lambda s: SECTION_ORDER.index(s.get("section_type")) if s.get("section_type") in SECTION_ORDER else 9)
    out = []
    for s in secs:
        blocks = []
        for a in s.get("section_attributes") or []:
            main = [x for n in (a.get("important_properties") or []) + (a.get("elevated_properties") or [])
                    if (x := stat(props.get(n)))]
            rest = [x for n in a.get("properties") or [] if (x := stat(props.get(n)))]
            text = game_text(a.get("loc_string"))
            if text or main or rest:
                blocks.append({"text": text, "main": main, "stats": rest})
        if blocks:
            out.append({"type": s.get("section_type") or "", "blocks": blocks})
    if not out:
        desc = game_text((item.get("description") or {}).get("desc"))
        if desc:
            out.append({"type": "", "blocks": [{"text": desc, "main": [], "stats": []}]})
    return out


def main():
    out = Path(sys.argv[1])
    now = int(time.time())
    since = (now - DAYS * 86400) // 86400 * 86400
    rows = get_json(f"{API}/analytics/item-stats?bucket=hero&min_average_badge={MIN_BADGE}"
                    f"&min_matches=1&min_unix_timestamp={since}")
    hero_matches = {h["hero_id"]: h["matches"] for h in get_json(
        f"{API}/analytics/hero-stats?min_average_badge={MIN_BADGE}&min_unix_timestamp={since}")}
    heroes = {h["id"]: h for h in get_json(f"{API}/assets/heroes") if h.get("player_selectable") and not h.get("disabled")}
    items_en = {i["id"]: i for i in get_json(f"{API}/assets/items")
                if i.get("shopable") and i.get("type") == "upgrade" and i.get("cost") and i.get("name")}
    items_pl = {i["id"]: i for i in get_json(f"{API}/assets/items?language=polish")}
    by_class = {i["class_name"]: i["id"] for i in items_en.values() if i.get("class_name")}
    players = sum(m for h, m in hero_matches.items() if h in heroes)

    total = defaultdict(lambda: {"matches": 0, "wins": 0, "sold": 0, "buy": 0.0})
    per_hero = defaultdict(list)
    for r in rows:
        if r["item_id"] not in items_en or r["bucket"] not in heroes:
            continue
        t = total[r["item_id"]]
        t["matches"] += r["matches"]
        t["wins"] += r["wins"]
        t["sold"] += r.get("sold") or 0
        t["buy"] += (r.get("avg_buy_time_s") or 0) * r["matches"]
        if r["matches"] >= MIN_HERO_MATCHES and hero_matches.get(r["bucket"]):
            per_hero[r["item_id"]].append((r["matches"] / hero_matches[r["bucket"]], r["bucket"], r["wins"], r["matches"]))

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

    into = defaultdict(list)
    for i in items_en.values():
        for c in i.get("component_items") or []:
            if c in by_class:
                into[by_class[c]].append(i["id"])

    slot_order = {"weapon": 0, "vitality": 1, "spirit": 2}
    result, used_heroes, slugs = [], set(), set()
    for i in sorted(items_en.values(), key=lambda i: (slot_order.get(i.get("item_slot_type"), 3), i["cost"], i["name"])):
        t = total.get(i["id"])
        if not t or not t["matches"]:
            continue  # not in the shop of the last two weeks
        s = slug(i["name"])
        if s in slugs:
            s = f"{s}-{i['id']}"
        slugs.add(s)
        pl = items_pl.get(i["id"], i)
        top = sorted(per_hero[i["id"]], reverse=True)[:HEROES_SHOWN]
        used_heroes.update(h for _, h, _, _ in top)
        result.append({
            "id": i["id"],
            "slug": s,
            "en": i["name"],
            "pl": re.sub(r"^#\|[^|#]*\|#", "", pl.get("name") or i["name"]),
            "slot": i.get("item_slot_type") or "weapon",
            "tier": i.get("item_tier"),
            "cost": i["cost"],
            "active": bool(i.get("is_active_item")),
            "img": icon(i.get("shop_image_webp") or i.get("image_webp") or i.get("shop_image") or i.get("image"),
                        img / "items" / f"{i['id']}.webp"),
            "text": {"en": sections(i), "pl": sections(pl)},
            "from": [by_class[c] for c in i.get("component_items") or [] if c in by_class],
            "into": sorted(into.get(i["id"], []), key=lambda x: (items_en[x]["cost"], items_en[x]["name"])),
            "matches": t["matches"],
            "share": round(t["matches"] / players, 4) if players else 0,
            "win": round(t["wins"] / t["matches"], 4),
            "buy": round(t["buy"] / t["matches"] / 60, 1),
            "sold": round(t["sold"] / t["matches"], 3),
            "heroes": [{"id": h, "share": round(sh, 3), "win": round(w / m, 4), "matches": m} for sh, h, w, m in top],
        })
    known = {r["id"] for r in result}
    for r in result:
        r["from"] = [x for x in r["from"] if x in known]
        r["into"] = [x for x in r["into"] if x in known]
    hero_out = {}
    for h in sorted(used_heroes):
        hh = heroes[h]
        hs = slug(hh["name"])
        hero_out[str(h)] = {"name": hh["name"], "slug": hs,
                            "img": icon(hh["images"].get("icon_image_small_webp") or hh["images"].get("icon_image_small"),
                                        img / "heroes" / f"{hs}.webp")}
    day = datetime.fromtimestamp(now, timezone.utc).date().isoformat()
    data = {"date": day, "days": DAYS, "players": players, "heroes": hero_out, "items": result}
    Path(__file__).with_name("items.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    print(f"{len(result)} items, {len(hero_out)} heroes, {players} player matches, data up to {day}")
    if missing:
        print(f"{len(missing)} icons not downloaded (pages use the remote URL for them)")


if __name__ == "__main__":
    main()
