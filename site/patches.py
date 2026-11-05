"""Deadlock patch notes, for the "Patche Deadlocka" / "Deadlock patch notes" pages.

Usage: python3 -I site/patches.py docs [assets.json]
       (downloads new patches and icons, writes site/patch-notes/<date>.txt, site/patches.json and docs/img/)

Patch texts: the deadlock-wiki archive of the official notes (github.com/deadlock-wiki/deadlock-data, MIT),
one plain-text file per patch. Each patch is downloaded once and kept in site/patch-notes/, so the archive
only has to answer for new ones; the newest few are downloaded again in case they were corrected.

Every line is matched to a hero, one of its abilities or an item by the name it starts with
("- Baba: Threadsap - Cooldown increased…", "- Healbane: …"), using the names and icons from
deadlock-api (the same source as the counter pages). Lines that name nothing stay under general changes.
The optional assets.json ({"heroes": […], "items": […], "items_pl": […]} in deadlock-api's shape) replaces
the download, for building without network access.
"""
import json
import re
import sys
import time
import urllib.request
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.deadlock-api.com/v1"
ARCHIVE = "https://raw.githubusercontent.com/deadlock-wiki/deadlock-data/master/data/changelogs"
STEAM_NEWS = "https://store.steampowered.com/news/app/1422450/view/{}"
REFRESH = 3  # the newest patches are downloaded again: the archive sometimes fixes them a day later
HERE = Path(__file__).parent
RAW = HERE / "patch-notes"
SLOTS = ("weapon", "vitality", "spirit")


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


def key(name):
    """Name as it is compared: case, apostrophes, & and spacing do not matter."""
    s = name.casefold().replace("’", "'").replace("&", "and")
    return re.sub(r"\s+", " ", s).strip()


class Names:
    """Heroes, abilities and items by the names the notes use."""

    def __init__(self, heroes, items, items_pl):
        self.heroes = {h["id"]: h for h in heroes}
        # Items no longer in the shop stay: older patches name them.
        self.items = {i["id"]: i for i in items if i.get("type") == "upgrade" and i.get("name")
                      and i.get("item_slot_type") in SLOTS}
        self.abilities = {}
        for i in items:
            hero = i.get("hero") or (i.get("heroes") or [None])[0]
            if i.get("type") == "ability" and hero in self.heroes and i.get("name"):
                self.abilities[i["id"]] = dict(i, hero=hero)
        self.pl = {i["id"]: i.get("name") for i in items_pl}
        self.hero_by = {key(h["name"]): h["id"] for h in heroes}
        for h in heroes:  # "Doorman: …" for The Doorman
            if key(h["name"]).startswith("the "):
                self.hero_by.setdefault(key(h["name"])[4:], h["id"])
        self.item_by = {key(i["name"]): i["id"] for i in self.items.values()}
        self.ability_of = {}  # hero id -> {name key: ability id}
        by_name = {}
        for a in self.abilities.values():
            self.ability_of.setdefault(a["hero"], {})[key(a["name"])] = a["id"]
            by_name.setdefault(key(a["name"]), set()).add(a["id"])
        # An ability name alone ("Malice: …") points to its hero only when no other hero has one like it.
        self.ability_by = {k: next(iter(v)) for k, v in by_name.items() if len(v) == 1}

    def starts(self, text, table):
        """(id, rest) when text starts with one of the names in table, longest name first."""
        words = text.split(" ")
        for n in range(min(len(words), 6), 0, -1):
            i = table.get(key(" ".join(words[:n]).rstrip(":,")))
            if i is not None:
                return i, " " + " ".join(words[n:]) if n < len(words) else ""
        return None


def clean(s):
    s = re.sub(r"\{\{[^{}|]*\|([^{}]*)\}\}", r"\1", s)  # wiki templates, should any slip into the text
    return re.sub(r"\s+", " ", s).strip()


def lines_of(text):
    """[(section header or None, paragraph number, line)]: bullets, with wrapped lines joined to their bullet."""
    out = []
    head, para, open_bullet = None, 0, False
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            para += 1
            open_bullet = False
            continue
        m = re.fullmatch(r"\[\s*(.*?)\s*\]", s)
        if m:
            head, para, open_bullet = clean(m.group(1)), para + 1, False
            continue
        b = re.match(r"^[-*•]\s*(.*)$", s)
        if b:
            out.append([head, para, clean(b.group(1))])
            open_bullet = True
        elif open_bullet and out:
            out[-1][2] = clean(out[-1][2] + " " + s)
        else:
            out.append([head, para, clean(s)])
    return [tuple(x) for x in out if x[2]]


def strip_sep(rest):
    return re.sub(r"^\s*[:\-–—]\s*", "", rest).strip()


def parse(text, names):
    general = OrderedDict()  # (header, paragraph) -> lines
    items = OrderedDict()
    heroes = OrderedDict()

    def hero_line(hid, rest):
        h = heroes.setdefault(hid, {"id": hid, "lines": [], "abilities": OrderedDict()})
        rest = strip_sep(rest)
        found = names.starts(rest, names.ability_of.get(hid, {}))
        if found:
            aid, more = found
            more = strip_sep(more)
            # "Chimera Mk1 weapon scaling increased…" under the Chimera Mk1 heading: "Weapon scaling increased…"
            h["abilities"].setdefault(aid, []).append(more[:1].upper() + more[1:] if more else rest)
        else:
            m = re.match(r"^([A-Z][\w'.]*(?: [\w'.]+){0,2})\s+[-–]\s+(.+)$", rest)
            if m:  # "Gun - Base bullet damage…": a part of the hero that is not an ability gets its own group too
                h["abilities"].setdefault(m.group(1), []).append(m.group(2)[:1].upper() + m.group(2)[1:])
            else:
                h["lines"].append(rest)

    for head, para, line in lines_of(text):
        m = re.match(r"^(.{1,40}?)\s*:\s+(.+)$", line)
        prefix, rest = (m.group(1), m.group(2)) if m else (None, None)
        if prefix:
            hid = names.hero_by.get(key(prefix))
            if hid is None:  # "The Magnificent Sinclair: …"
                hid = next((h for n, h in names.hero_by.items() if key(prefix).endswith(" " + n)), None)
            if hid is None:  # "Kelvin Beam: Arctic Beam…": a hero name and a slip
                found = names.starts(prefix, names.hero_by)
                if found and names.starts(found[1].strip() + " " + rest, names.ability_of.get(found[0], {})):
                    hid, rest = found[0], found[1].strip() + " " + rest
            if hid is not None:
                hero_line(hid, rest)
                continue
            iid = names.item_by.get(key(prefix))
            if iid is not None:
                items.setdefault(iid, []).append(rest)
                continue
            aid = names.ability_by.get(key(prefix))
            if aid is not None:
                hero_line(names.abilities[aid]["hero"], prefix + " - " + rest)
                continue
        found = names.starts(line, names.item_by)
        if found and found[1][:1] in (" ", ""):
            items.setdefault(found[0], []).append(line)
            continue
        general.setdefault((head, para), []).append(line)

    groups = []
    for (head, _), ls in general.items():
        if groups and groups[-1]["head"] == head:
            groups[-1]["paras"].append(ls)
        else:
            groups.append({"head": head, "paras": [ls]})
    slot_order = {s: n for n, s in enumerate(SLOTS)}
    item_list = sorted(({"id": i, "lines": ls} for i, ls in items.items()),
                       key=lambda x: (slot_order[names.items[x["id"]]["item_slot_type"]], names.items[x["id"]].get("cost") or 0,
                                      names.items[x["id"]]["name"]))
    hero_list = [{"id": h["id"], "lines": h["lines"],
                  "abilities": [{"id": a, "lines": ls} if isinstance(a, int) else {"name": a, "lines": ls}
                                for a, ls in h["abilities"].items()]}
                 for h in sorted(heroes.values(), key=lambda h: names.heroes[h["id"]]["name"])]
    return {"general": groups, "items": item_list, "heroes": hero_list}


def title_of(cfg, day):
    t = (cfg.get("title") or "").strip()
    t = re.sub(r"\s*[-–]\s*\d{1,2}-\d{1,2}-\d{4}$", "", t)  # "Minor Update - 10-05-2026": the page shows the date
    return t or None


def link_of(cfg):
    if cfg.get("source_id") and "steam" in (cfg.get("link") or ""):
        return STEAM_NEWS.format(cfg["source_id"])
    return cfg.get("link")


def load_assets(arg):
    if arg:
        a = json.loads(Path(arg).read_text())
        return a["heroes"], a["items"], a.get("items_pl", [])
    heroes = get_json(f"{API}/assets/heroes")
    items = get_json(f"{API}/assets/items")
    items_pl = get_json(f"{API}/assets/items?language=polish")
    return heroes, items, items_pl


def main():
    out = Path(sys.argv[1])
    configs = get_json(f"{ARCHIVE}/changelog_configs.json")
    RAW.mkdir(exist_ok=True)
    days = sorted(configs)
    for n, day in enumerate(days):
        path = RAW / f"{day}.txt"
        if path.exists() and n < len(days) - REFRESH:
            continue
        try:
            text = get(f"{ARCHIVE}/raw/{day}.txt").decode("utf-8")
        except OSError:
            if path.exists():
                continue
            raise
        path.write_text(text.replace("\r\n", "\n"))

    heroes, items, items_pl = load_assets(sys.argv[2] if len(sys.argv) > 2 else None)
    names = Names(heroes, items, items_pl)

    patches = []
    used_h, used_i, used_a = set(), set(), set()
    for day in reversed(days):
        path = RAW / f"{day}.txt"
        if not path.exists():
            continue
        p = parse(path.read_text(), names)
        if not (p["general"] or p["items"] or p["heroes"]):
            continue
        used_i.update(i["id"] for i in p["items"])
        for h in p["heroes"]:
            used_h.add(h["id"])
            used_a.update(a["id"] for a in h["abilities"] if "id" in a)
        cfg = configs[day]
        patches.append({"slug": day.lower().replace("_herolab", "-hero-labs").replace("_", "-"),
                        "date": cfg.get("date") or day[:10], "title": title_of(cfg, day), "link": link_of(cfg),
                        "hero_lab": bool(cfg.get("is_hero_lab")), **p})

    img = out / "img"
    for d in ("heroes", "items", "abilities"):
        (img / d).mkdir(parents=True, exist_ok=True)
    missing = []

    def icon(url, path):
        """Saves the icon next to the pages; the pages fall back to the remote URL while it is missing."""
        if url and not path.exists() and url.startswith("https://") and ".invalid/" not in url:
            if missing:  # the icon server is unreachable: do not wait on every icon
                missing.append(url)
                return url
            try:
                path.write_bytes(get(url, attempts=2))
            except OSError:
                missing.append(url)
        return url

    hero_out = {}
    for hid in sorted(used_h):
        h = names.heroes[hid]
        s = slug(h["name"])
        hero_out[str(hid)] = {"name": h["name"], "slug": s,
                              "img": icon(h["images"].get("icon_image_small_webp") or h["images"].get("icon_image_small"),
                                          img / "heroes" / f"{s}.webp")}
    item_out = {}
    for iid in sorted(used_i):
        it = names.items[iid]
        item_out[str(iid)] = {"en": it["name"], "pl": names.pl.get(iid) or it["name"], "cost": it.get("cost"),
                              "slot": it["item_slot_type"], "tier": it.get("item_tier"),
                              "img": icon(it.get("shop_image_webp") or it.get("image_webp") or it.get("image"),
                                          img / "items" / f"{iid}.webp")}
    ability_out = {}
    for aid in sorted(used_a):
        a = names.abilities[aid]
        ability_out[str(aid)] = {"en": a["name"], "pl": names.pl.get(aid) or a["name"], "hero": a["hero"],
                                 "img": icon(a.get("image_webp") or a.get("image"), img / "abilities" / f"{aid}.webp")}

    day = datetime.now(timezone.utc).date().isoformat()
    data = {"date": day, "source": "https://github.com/deadlock-wiki/deadlock-data",
            "heroes": hero_out, "items": item_out, "abilities": ability_out, "patches": patches}
    (HERE / "patches.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    lines = sum(len(x) for p in patches for g in p["general"] for x in g["paras"])
    print(f"{len(patches)} patches ({patches[0]['date'] if patches else '-'} newest), {len(hero_out)} heroes, "
          f"{len(item_out)} items, {len(ability_out)} abilities, {lines} general lines")
    if missing:
        print(f"{len(missing)} icons not downloaded (pages use the remote URL for them)")


if __name__ == "__main__":
    main()
