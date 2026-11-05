"""Builds the Deadlock Assist landing page (PL at /, EN at /en/) into <out>/.

Usage: python3 -I site/build.py docs   (edit texts here, then rebuild; GitHub Pages serves docs/)
The changelog page reads site/changelog.json. The app's release workflow refreshes it with
site/sync_changelog.py on every new version; the push to site/ then rebuilds and publishes the site.
"""
import html
import json
import re
import sys
from pathlib import Path

DOMAIN = "deadlock-assist.com"
BASE = f"https://{DOMAIN}/"
DOWNLOAD = "https://github.com/adam2s/deadlock-assist-releases/releases/latest"
REPO = "https://github.com/adam2s/deadlock-assist-releases"
KOFI = "https://ko-fi.com/deadlockassist"
IDEA = REPO + "/issues/new?template=pomysl.yml"
BUG = REPO + "/issues/new?template=blad.yml"

# Inline icons (24×24, stroke = currentColor).
ICONS = {
    "counter": '<path d="M12 3 4 6v6c0 4.5 3.4 8.3 8 9 4.6-.7 8-4.5 8-9V6l-8-3Z"/><path d="m9 12 2 2 4-4"/>',
    "cart": '<circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M3 4h2l2.4 11h11.2L21 7H6.3"/>',
    "lane": '<path d="M4 20 10 4M20 20 14 4M12 6v2M12 11v2M12 16v2"/>',
    "eye": '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
    "clock": '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2.5M9 2h6"/>',
    "chart": '<path d="M4 20V4M4 20h16"/><path d="m7 15 4-4 3 3 5-6"/>',
    "book": '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2V5Z"/><path d="M19 19v2H6"/><path d="M9 7h6M9 11h6"/>',
    "auto": '<path d="M20 12a8 8 0 1 1-2.3-5.6"/><path d="M20 4v5h-5"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "download": '<path d="M12 3v12m0 0-5-5m5 5 5-5M4 21h16"/>',
    "windows": '<path d="M3 5.5 10.5 4.5v7H3v-6ZM12 4.3 21 3v8.5h-9V4.3ZM3 12.5h7.5v7L3 18.5v-6ZM12 12.5h9V21l-9-1.3v-7.2Z" fill="currentColor" stroke="none"/>',
    "heart": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10Z"/>',
}


def icon(name, cls="ico"):
    return (
        f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'
    )


NB = "\u00a0"


def e(s):
    return html.escape(s, quote=True)


PL = {
    "lang": "pl",
    "path": "",
    "locale": "pl_PL",
    "title": "Deadlock Assist – kontry, buildy i timery do Deadlocka (za darmo)",
    "description": (
        "Darmowa nakładka do Deadlocka na Windows: kontry na skład wroga, co kupić teraz, timery obozów "
        "i Mid Bossa, analiza meczu. Bez Overwolf i reklam."
    ),
    "ids": {"features": "funkcje", "gallery": "w-akcji", "results": "skutecznosc", "safety": "bezpieczenstwo",
            "start": "start", "faq": "faq"},
    "nav": [("funkcje", "Funkcje"), ("skutecznosc", "Skuteczność"), ("bezpieczenstwo", "Bezpieczeństwo"),
            ("faq", "FAQ")],
    "switch": ("en/", "English", "English version"),
    "counters": {
        "path": "kontry/", "nav": "Kontry",
        "index_title": "Kontry na bohaterów Deadlocka – najlepsze przedmioty na każdego",
        "index_desc": "Jakie przedmioty kupić przeciw każdemu bohaterowi Deadlocka. Dane z meczów rang Emissary+ "
                      "z ostatnich 14 dni, odświeżane co tydzień.",
        "index_h1": "Kontry na bohaterów Deadlocka",
        "index_lead": "Wybierz bohatera wroga i zobacz, z jakimi przedmiotami gracze najczęściej z nim wygrywają.",
        "title": "Kontry i build {hero} w Deadlocku – najlepsze przedmioty",
        "desc": "Typowy build {hero} i najlepsze kontry: {top}. Mecze Emissary+ z 14 dni, co tydzień nowe.",
        "h1": "Kontry na {hero}",
        "lead": "Co kupuje większość graczy {hero} i czym najlepiej to skontrować.",
        "build_h": "Typowy build {hero}",
        "build_note": "Przedmioty, które kupuje i zatrzymuje większość graczy {hero}, w kolejności zakupu. "
                      "Procent: ilu graczy go kupuje.",
        "best_h": "Najlepsze kontry na {hero}",
        "more": "Więcej kontr",
        "min": "min",
        "home_h": "Przykład: kontry na {hero}",
        "home_lead": "Typowy build najczęściej granego bohatera i dwa przedmioty, z którymi najczęściej się z nim wygrywa.",
        "home_legend": "Minuta zakupu · % graczy, którzy go kupują. {pts} = o tyle częściej wygrywa się z {hero} z {item}.",
        "home_all": "Kontry na wszystkich {n} bohaterów",
        "home_one": "Cała strona {hero}",
        "data": "{n} zakupów, mecze Emissary+, ostatnie 14 dni (stan na {date})",
        "edge_h": "Przewaga nad {hero}",
        "explain": "{pts} = z {item} wygrywa się z {hero} o {num} punktu procentowego częściej niż zwykle, "
                   "w porównaniu z przedmiotami w tej samej cenie.",
        "million": "mln", "alt": "PL",
        "slots": {"weapon": "Broń", "vitality": "Witalność", "spirit": "Duch"},
        "cta_h": "Kontry na cały skład, na żywo w meczu",
        "cta_p": "Doradca czyta wrogów z ekranu i mówi, co kupić teraz.",
        "others": "Kontry na innych bohaterów",
        "souls": "dusz",
    },
    "patches": {
        "path": "patche/", "nav": "Patche",
        "index_title": "Patche i aktualizacje Deadlocka – zmiany bohaterów i przedmiotów (patch notes)",
        "index_desc": "Patch notes Deadlocka w jednym miejscu: każda aktualizacja ze zmianami bohaterów, umiejętności "
                      "i przedmiotów, z ikonami, od najnowszej.",
        "index_h1": "Patche i aktualizacje Deadlocka",
        "index_lead": "Każda aktualizacja gry z podziałem na bohaterów, ich umiejętności i przedmioty.",
        "title": "Patch Deadlocka {date} – zmiany bohaterów i przedmiotów",
        "desc": "Zmiany w Deadlocku z {date}: {names}. Wszystkie zmiany bohaterów, umiejętności i przedmiotów z ikonami.",
        "h1": "Patch {date}",
        "latest": "Najnowszy patch", "open": "Zobacz wszystkie zmiany",
        "general": "Zmiany ogólne", "items": "Przedmioty", "heroes": "Bohaterowie",
        "n_heroes": ("bohater", "bohaterów", "bohaterów"), "n_items": ("przedmiot", "przedmioty", "przedmiotów"),
        "n_general": ("zmiana ogólna", "zmiany ogólne", "zmian ogólnych"),
        "hero_lab": "Hero Labs", "second": "Aktualizacja {n}",
        "slots": {"weapon": "Broń", "vitality": "Witalność", "spirit": "Duch"}, "jump": "Przejdź do bohatera", "years": "Lata",
        "summary": "Patch z {date} zmienia {parts}.", "and": "i",
        "most": "Najwięcej zmian: {list}.",
        "parts": {"heroes": ("bohatera", "bohaterów", "bohaterów"), "items": ("przedmiot", "przedmioty", "przedmiotów"),
                  "general": ("zmianę ogólną", "zmiany ogólne", "zmian ogólnych")},
        "lang_note": "Treść zmian po angielsku, tak jak w oficjalnych notatkach.",
        "source": "Oficjalne ogłoszenie", "archive": "Archiwum deadlock-wiki",
        "hero_gen": "Bohater", "counters": "Kontry na {hero}",
        "older": "Starszy patch", "newer": "Nowszy patch", "all": "Wszystkie patche",
        "souls": "dusz", "updated": "Aktualizowane codziennie, ostatnio {date}.",
        "on_page": "Na tej stronie",
        "cta_h": "Co kupić po tym patchu?", "cta_p": "Doradca w grze liczy kontry na aktualnych danych i mówi, co kupić teraz.",
        "hero_recent": "Ostatnie zmiany bohatera {hero}: {date}", "cta_index": "Co kupić po najnowszym patchu?",
    },
    "changes": {
        "path": "zmiany/", "nav": "Zmiany", "title": "Lista zmian Deadlock Assist – nowe wersje nakładki do Deadlocka",
        "description": "Co nowego w każdej wersji Deadlock Assist, nakładki do Deadlocka z kontrami, buildami i timerami.",
        "h1": "Lista zmian", "lead": "Co nowego w każdej wersji.",
        "version": "Wersja", "older": "Starsze wersje", "home": "Strona główna", "latest": "Najnowsza",
        "highlight": "Najważniejsze: od wersji 1.2.6 doradca trafia 81% kontr (wcześniej 62%).",
        "cta_note": "Aplikacja aktualizuje się sama. Pobierasz ją tylko raz.",
        "months": ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia",
                   "września", "października", "listopada", "grudnia"],
    },
    "eyebrow": "Nakładka do Deadlocka · Windows 10/11",
    "h1": "Kontry na skład wroga w Deadlocku, na żywo",
    "lead": "Czyta z ekranu skład i zakupy wrogów, podpowiada, co kupić, i pilnuje timerów obozów i Mid Bossa.",
    "proof_line": ("81%", "trafnych kontr w teście na 2020 meczach"),
    "cta": "Pobierz dla Windows",
    "cta_short": "Pobierz",
    "cta_note": "Deadlock w oknie bez ramek · aktualizuje się sama",
    "hero_note": "Deadlock w oknie bez ramek · aktualizuje się sama",
    "cta2": "Zobacz w akcji",
    "shot_alt": (
        "Nakładka Deadlock Assist w Deadlocku: kontry na linii, panel Kup teraz z najlepszym przedmiotem "
        "na wroga oraz zegar z timerami obozów i Mid Bossa"
    ),
    "badges": ["Za darmo", "Bez reklam i konta", "Bez Overwolf", "Nie czyta pamięci gry"],
    "features_h": "Kontry, buildy i timery",
    "features": [
        ("counter", "Kontry na skład wroga", "Healbane na leczenie, Silencer na umiejętności. Z ceną i powodem."),
        ("cart", "„Kup teraz”", "Jeden najlepszy zakup na teraz, dopasowany do Twojego buildu i dusz."),
        ("eye", "Zakupy wrogów", "Po Tab widzi, co kupił wróg, i od razu zmienia rady."),
        ("lane", "Kontry na linii", "Do 10. minuty tanie przedmioty na rywali z Twojej linii."),
        ("clock", "Timery obozów i Mid Bossa", "Obozy w dżungli, Mid Boss, power-upy i urna, ze strzałką kierunku."),
        ("chart", "Analiza meczu", "Farma minuta po minucie i co poprawić w kolejnym meczu."),
    ],
    "gallery_h": "Nakładka w grze",
    "gallery": [
        ("deadlock-overlay-tab.webp", "deadlock-overlay-tab.webp",
         "Nakładka Deadlock Assist po wciśnięciu Tab: przedmioty wszystkich graczy i kontry na każdego wroga",
         "Tab: co kupił każdy wróg i czym go skontrować"),
        ("deadlock-match-history.webp", "deadlock-match-history@2x.webp",
         "Historia meczów Deadlock Assist: wyniki, przeciwnicy, farma i kolejność zakupów",
         "Historia: farma na minutę i kolejność zakupów"),
    ],
    "proof_h": "Czy doradca naprawdę pomaga?",
    "proof_lead": "Test na 2020 meczach z rang Emissary i wyżej, 33 811 zakupów.",
    "proof": [
        ("81%", 81, 62, "trafnych kontr", "Podpowiedzi, które na ten skład wygrywają częściej niż przeciętny przedmiot.",
         "poprzednia wersja: 62%"),
        ("29%", 29, 25, "zakupów w top 5 doradcy", "Tyle realnych zakupów graczy było w pierwszej piątce podpowiedzi.",
         "poprzednia wersja: 25%"),
        ("+3,2 p.p.", None, None, "wyższy odsetek wygranych", "Gracze, którzy kupili coś z top 5, wygrywali częściej.",
         "przy tej samej farmie"),
    ],
    "proof_note": "Wyniki z cudzych meczów, nie gwarancja wygranej. Wersja 1.2.6.",
    "safe_h": "Bezpieczeństwo",
    "safe_lead": "Działa jak nagrywanie ekranu, nie jak cheat.",
    "safe": [
        "Nie czyta pamięci gry i nie zmienia jej plików.",
        "Nie wysyła klawiszy ani kliknięć do gry.",
        "Pobiera tylko publiczne statystyki z deadlock-api.com.",
        "Każda aktualizacja jest podpisana.",
    ],
    "safe_note": "Nieoficjalne narzędzie fanów. Valve nie publikuje listy dozwolonych programów.",
    "how_h": "Jak zacząć",
    "how": [
        ("Zainstaluj", "Uruchom instalator i ustaw w Deadlocku tryb okna bez ramek (Borderless)."),
        ("Graj", "Mecz wykrywa się sam. Co jakiś czas przytrzymaj Tab."),
        ("Analizuj", "Po meczu wciśnij F10 i zobacz podsumowanie w Historii."),
    ],
    "faq_h": "Pytania o Deadlock Assist",
    "faq": [
        ("Czy można dostać bana?",
         "Aplikacja nie dotyka procesu gry: robi tylko zrzuty ekranu, jak OBS czy Discord. Valve nie zatwierdza "
         "żadnych zewnętrznych narzędzi, więc korzystasz na własną odpowiedzialność."),
        ("Działa w pełnym ekranie?",
         "Nie. Ustaw w Deadlocku tryb okna bez ramek (Borderless), inaczej nakładka nie będzie widoczna."),
        ("Dlaczego Windows pokazuje ostrzeżenie?",
         "To SmartScreen przy nowych programach. Kliknij „Więcej informacji” → „Uruchom mimo to”. Każda aktualizacja "
         "jest podpisana."),
        ("Skąd wie, co kupić?",
         "Ze statystyk deadlock-api.com i z tego, co widzi na ekranie: składu wroga, jego zakupów i Twoich dusz."),
        ("Jakie są wymagania?",
         "Windows 10 lub 11 (64-bit) i Deadlock w trybie okna bez ramek. Interfejs PL lub EN, do przełączenia w aplikacji."),
    ],
    "final_h": "Zagraj następny mecz z doradcą",
    "final_lead": "Instalacja zajmuje minutę.",
    "kofi": "Wesprzyj na Ko-fi",
    "links": [(IDEA, "Zaproponuj pomysł"), (BUG, "Zgłoś błąd"), (REPO + "/blob/main/SECURITY.md", "Zgłoś lukę"),
              (REPO + "/releases", "Wszystkie wersje")],
    "footer": (
        "Deadlock jest znakiem towarowym Valve Corporation. Deadlock Assist to nieoficjalny projekt fanów, "
        "niezwiązany z Valve. Dane o przedmiotach: deadlock-api.com."
    ),
    "skip": "Przejdź do treści",
    "smartscreen": "Windows ostrzega? „Więcej informacji” → „Uruchom mimo to”.",
    "feature_list": "Kontry na skład wroga; Kup teraz; Zakupy wrogów; Kontry na linii; Timery obozów i Mid Bossa; Analiza meczu",
    "nf_h": "Nie ma takiej strony",
    "nf_link": "Wróć na stronę główną",
}

EN = {
    "lang": "en",
    "path": "en/",
    "locale": "en_US",
    "title": "Deadlock Counter Items & Build Overlay – Deadlock Assist",
    "description": (
        "Free Deadlock overlay for Windows: counter items vs the enemy team, what to buy now, jungle camp & Mid Boss "
        "timers, match review. No Overwolf, no ads."
    ),
    "ids": {"features": "features", "gallery": "in-action", "results": "results", "safety": "safety",
            "start": "get-started", "faq": "faq"},
    "nav": [("features", "Features"), ("results", "Results"), ("safety", "Safety"), ("faq", "FAQ")],
    "switch": ("../", "Polski", "Wersja polska"),
    "counters": {
        "path": "en/counters/", "nav": "Counters",
        "index_title": "Deadlock Counter Items for Every Hero – Best Items to Buy",
        "index_desc": "Which items to buy against every Deadlock hero. Data from Emissary+ matches of the last 14 days, "
                      "refreshed every week.",
        "index_h1": "Counter items for every hero",
        "index_lead": "Pick the enemy hero and see which items players win with most against them.",
        "title": "{hero} Build & Counter Items in Deadlock – Best Items vs {hero}",
        "desc": "Typical {hero} build and best counters: {top}. Emissary+ matches, last 14 days, updated weekly.",
        "h1": "{hero} counter items",
        "lead": "What most {hero} players buy, and the best items to counter it.",
        "build_h": "Typical {hero} build",
        "build_note": "Items most {hero} players buy and keep, in buying order. Percent: how many players buy it.",
        "best_h": "Best counters to {hero}",
        "more": "More counters",
        "min": "min",
        "home_h": "Example: {hero} counters",
        "home_lead": "The most played hero's typical build and the two items that win most against it.",
        "home_legend": "Buy minute · % of players who buy it. {pts} = how much more often players with {item} beat {hero}.",
        "home_all": "Counters for all {n} heroes",
        "home_one": "Full {hero} page",
        "data": "{n} purchases, Emissary+ matches, last 14 days (as of {date})",
        "edge_h": "Edge vs {hero}",
        "explain": "{pts} = players with {item} beat {hero} {num} percentage points more often than usual, "
                   "compared with items at the same price.",
        "million": "M", "alt": "",
        "slots": {"weapon": "Weapon", "vitality": "Vitality", "spirit": "Spirit"},
        "cta_h": "Counters for the whole enemy team, live",
        "cta_p": "The advisor reads the enemies from your screen and tells you what to buy now.",
        "others": "Counters for other heroes",
        "souls": "souls",
    },
    "patches": {
        "path": "en/patch-notes/", "nav": "Patch notes",
        "index_title": "Deadlock Patch Notes – Every Update, Hero & Item Change",
        "index_desc": "Every Deadlock patch in one place: hero, ability and item changes with icons, newest update first.",
        "index_h1": "Deadlock patch notes",
        "index_lead": "Every game update, split into heroes, their abilities and items.",
        "title": "Deadlock Patch Notes {date} – Hero & Item Changes",
        "desc": "Deadlock changes from {date}: {names}. Every hero, ability and item change with icons.",
        "h1": "Patch {date}",
        "latest": "Latest patch", "open": "See all changes",
        "general": "General changes", "items": "Items", "heroes": "Heroes",
        "n_heroes": ("hero", "heroes", "heroes"), "n_items": ("item", "items", "items"),
        "n_general": ("general change", "general changes", "general changes"),
        "hero_lab": "Hero Labs", "second": "Update {n}",
        "slots": {"weapon": "Weapon", "vitality": "Vitality", "spirit": "Spirit"}, "jump": "Jump to a hero", "years": "Years",
        "summary": "The {date} patch changes {parts}.", "and": "and",
        "most": "Most changes: {list}.",
        "parts": {"heroes": ("hero", "heroes", "heroes"), "items": ("item", "items", "items"),
                  "general": ("general change", "general changes", "general changes")},
        "lang_note": "",
        "source": "Official post", "archive": "deadlock-wiki archive",
        "hero_gen": "Hero", "counters": "{hero} counters",
        "older": "Older patch", "newer": "Newer patch", "all": "All patches",
        "souls": "souls", "updated": "Updated daily, last on {date}.",
        "on_page": "On this page",
        "cta_h": "What to buy after this patch?", "cta_p": "The in-game advisor counts counters on current data and tells you what to buy now.",
        "hero_recent": "Last {hero} changes: {date}", "cta_index": "What to buy after the latest patch?",
    },
    "changes": {
        "path": "en/changes/", "nav": "Changes", "title": "Deadlock Assist Changelog – Overlay Updates & Release Notes",
        "description": "What’s new in every version of Deadlock Assist, the Deadlock overlay with counter items, builds and timers.",
        "h1": "Changelog", "lead": "What's new in every version.",
        "version": "Version", "older": "Older versions", "home": "Home", "latest": "Latest",
        "highlight": "Highlight: since version 1.2.6 the advisor gets 81% of counters right (was 62%).",
        "cta_note": "The app updates itself. You only download it once.",
        "months": ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                   "October", "November", "December"],
    },
    "eyebrow": "Deadlock overlay · Windows 10/11",
    "h1": "Deadlock counter items for the enemy team, live",
    "lead": "Reads the enemy team and their items from your screen, tells you what to buy and tracks camp and Mid Boss timers.",
    "proof_line": ("81%", "good counters, tested on 2,020 matches"),
    "cta": "Download for Windows",
    "cta_short": "Download",
    "cta_note": "Deadlock in borderless window · updates itself",
    "hero_note": "Deadlock in borderless window · updates itself",
    "cta2": "See it in action",
    "shot_alt": (
        "Deadlock Assist overlay in Deadlock: lane counters, the Buy now panel with the best item against the "
        "enemy, and a clock with jungle camp and Mid Boss timers"
    ),
    "badges": ["Free", "No ads, no account", "No Overwolf", "No memory reading"],
    "features_h": "Counter items, builds and timers",
    "features": [
        ("counter", "Counter items for the enemy team", "Healbane vs healing, Silencer vs abilities. With price and reason."),
        ("cart", "“Buy now”", "The single best purchase right now, fitted to your build and souls."),
        ("eye", "Enemy purchases", "Hold Tab and it sees what enemies bought, then updates the advice."),
        ("lane", "Lane counters", "Until minute 10, cheap items against your lane opponents."),
        ("clock", "Camp and Mid Boss timers", "Jungle camps, Mid Boss, power-ups and the urn, with a direction arrow."),
        ("chart", "Match review", "Farm minute by minute and what to improve next match."),
    ],
    "gallery_h": "In-game overlay",
    "gallery": [
        ("deadlock-overlay-tab.webp", "deadlock-overlay-tab.webp",
         "Deadlock Assist overlay with Tab held: every player's items and counters to each enemy",
         "Tab: what every enemy bought and how to counter it"),
        ("deadlock-match-history.webp", "deadlock-match-history@2x.webp",
         "Deadlock Assist match history: results, opponents, farm and purchase order",
         "History: farm per minute and purchase order"),
    ],
    "proof_h": "Does the advisor actually help?",
    "proof_lead": "Tested on 2,020 Emissary+ matches, 33,811 purchases.",
    "proof": [
        ("81%", 81, 62, "good counters", "Picks that win more often vs that team than an average item.",
         "previous version: 62%"),
        ("29%", 29, 25, "of real buys in its top 5", "Share of players' actual purchases that were in the advisor's top 5.",
         "previous version: 25%"),
        ("+3.2 pp", None, None, "higher win rate", "Players who bought from the top 5 won more often.",
         "at equal farm"),
    ],
    "proof_note": "Results from other players' matches, not a guarantee. Version 1.2.6.",
    "safe_h": "Safety",
    "safe_lead": "Works like screen recording, not like a cheat.",
    "safe": [
        "Does not read game memory or change game files.",
        "Sends no keys or clicks to the game.",
        "Downloads only public stats from deadlock-api.com.",
        "Every update is signed.",
    ],
    "safe_note": "Unofficial fan tool. Valve does not publish a list of allowed programs.",
    "how_h": "Get started",
    "how": [
        ("Install", "Run the installer and set Deadlock to borderless window mode."),
        ("Play", "It detects the match on its own. Hold Tab now and then."),
        ("Review", "After the match, press F10 for the summary in History."),
    ],
    "faq_h": "Deadlock Assist FAQ",
    "faq": [
        ("Can I get banned?",
         "It never touches the game process; it only takes screenshots, like OBS or Discord. Valve doesn't approve "
         "any third-party tools, so use it at your own risk."),
        ("Does it work in fullscreen?",
         "No. Set Deadlock to borderless window, otherwise the overlay can't show."),
        ("Why does Windows show a warning?",
         "SmartScreen flags new apps. Click “More info” → “Run anyway”. Every update is signed."),
        ("How does it know what to buy?",
         "From deadlock-api.com stats and what it sees on screen: the enemy team, their purchases and your souls."),
        ("What are the requirements?",
         "Windows 10 or 11 (64-bit) and Deadlock in borderless window. Interface in English or Polish, switchable in the app."),
    ],
    "final_h": "Play your next match with an advisor",
    "final_lead": "Installing takes a minute.",
    "kofi": "Support on Ko-fi",
    "links": [(IDEA, "Suggest an idea"), (BUG, "Report a bug"), (REPO + "/blob/main/SECURITY.md", "Report a vulnerability"),
              (REPO + "/releases", "All versions")],
    "footer": (
        "Deadlock is a trademark of Valve Corporation. Deadlock Assist is an unofficial fan project, not "
        "affiliated with Valve. Item data: deadlock-api.com."
    ),
    "skip": "Skip to content",
    "smartscreen": "Windows warning? “More info” → “Run anyway”.",
    "feature_list": "Counter items vs the enemy team; Buy now advisor; Enemy purchases; Lane counters; Jungle camp and Mid Boss timers; Match review",
    "nf_h": "Page not found",
    "nf_link": "Back to the home page",
}

CSS = Path(__file__).with_name("style.css").read_text()
FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&amp;display=swap" '
    'media="print" onload="this.media=\'all\'">\n'
    '<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&amp;display=swap"></noscript>'
)


def typeset(s, lang):
    """Glues what must not end a line: Polish one-letter words and short prepositions, numbers, · and →."""
    if lang == "pl":
        s = re.sub(r"(?<![\w-])([aiouwz]|na|do|od|po|ze|we|że|co|to|nie|ma|jak) ", "\\1" + NB, s, flags=re.I)
    s = re.sub(r"(\d) (\d{3})\b", "\\1" + NB + "\\2", s)
    s = re.sub(r"\b(Windows|Tier|minute|minuty|top)\s(\d)", "\\1" + NB + "\\2", s)
    s = re.sub(r"(\d+\.) (minuty)", "\\1" + NB + "\\2", s)
    s = re.sub(r"([„“])([^”]{1,24})”", lambda m: m.group(1) + m.group(2).replace(" ", NB) + "”", s)
    s = re.sub(r"(?<=\w)'(?=\w)|(?<=s)'(?=\s)", "’", s)
    s = re.sub(r"(?<![\d.,])(\d{1,3}) (?=[^\W\d_])", "\\1" + NB, s)
    return s.replace(" ·", NB + "·").replace(" → ", NB + "→" + NB).replace(" p.p.", NB + "p.p.").replace(" pp", NB + "pp")


def unit(n):
    """Smaller unit after a big stat number: 81<span>%</span>, +3,2<span> p.p.</span>."""
    return re.sub(r"(%|\u00a0p\.p\.|\u00a0pp)$", r'<span class="u">\1</span>', n)


CHANGELOG = json.loads(Path(__file__).with_name("changelog.json").read_text())

# Shorter text for the website than in the app, and without developer-only lines; other versions show as in the app.
SITE_CHANGES = {
    "1.2.9": {"pl": ["Przycisk „Strona” w aplikacji otwiera deadlock-assist.com."],
              "en": ["“Website” button in the app opens deadlock-assist.com."]},
    "1.2.5": {"pl": ["Przycisk „Zaproponuj zmianę” (zgłoszenie na GitHubie) i „☕ Wesprzyj” w oknie aplikacji."],
              "en": ["“Suggest a change” button (GitHub idea form) and “☕ Support” in the app window."]},
    "1.2.8": {"pl": ["Cała aplikacja i nakładka po angielsku (przełącznik PL / EN). Na start język jak w Windows."],
              "en": ["Full English app and overlay (PL / EN switch). Starts in your Windows language."]},
    "1.2.7": {"pl": ["Historia: przy każdej podpowiedzi widać, skąd się wzięła („Twój build” / „Na wrogów”) i dlaczego."],
              "en": ["History: each suggestion shows where it came from (“Your build” / “Vs enemies”) and why."]},
    "1.2.6": {"pl": ["Doradca porównuje przedmioty przy równej farmie: 81% trafnych kontr zamiast 62% (test na 2020 meczach).",
                     "29% prawdziwych zakupów graczy jest w top 5 doradcy (wcześniej 25%).",
                     "Karta „Kup teraz” ma dwa wiersze: „Twój build” i „Na wrogów”. Do 10:00 kontruje wrogów z Twojej linii.",
                     "Karta pokazuje wroga z dużą przewagą dusz i przedmiot przeciw niemu.",
                     "Trzy tryby doradcy: „Mój build”, „Zrównoważony”, „Kontry”."],
              "en": ["The advisor compares items at equal farm: 81% good counters instead of 62% (test on 2,020 matches).",
                     "29% of players' real buys are in the advisor's top 5 (was 25%).",
                     "The “Buy now” card has two rows: “Your build” and “Vs enemies”. Until 10:00 it counters your lane.",
                     "The card shows an enemy far ahead in souls and an item against them.",
                     "Three advisor modes: “My build”, “Balanced”, “Counters”."]},
    "1.2.4": {"pl": ["Zakładka „Nakładka”: podgląd ekranu na środku, kliknięcie panelu przewija do jego ustawień.",
                     "Zegar w nakładce: „Co teraz” ze strzałką kierunku, obozy z paskiem do odrodzenia."],
              "en": ["“Overlay” tab: screen preview in the middle; clicking a panel scrolls to its settings.",
                     "Overlay clock: “What now” with a direction arrow, camps with a respawn bar."]},
    "1.2.3": {"pl": ["Wykres farmy nie gubi już prawdziwych odczytów, gdy dusze szybko rosną."],
              "en": ["The farm chart no longer drops real readings when souls grow fast."]},
    "1.2.2": {"pl": ["Historia: wykres farmy minuta po minucie dla każdego gracza i obu drużyn.",
                     "Historia: przyrost farmy co 5 minut i podsumowanie meczu z tym, co poprawić."],
              "en": ["History: minute-by-minute farm chart for every player and both teams.",
                     "History: farm gain every 5 minutes and a match summary with what to improve."]},
    "1.2.1": {"pl": ["Szybsze działanie w tle."], "en": ["Faster in the background."]},
    "1.1.9": {"pl": ["Poprawka błędu przy starcie aplikacji."], "en": ["Fixed an error at app start."]},
    "1.1.8": {"pl": ["Poprawki instalatora."], "en": ["Installer fixes."]},
}


def site_changes(r, lang):
    return SITE_CHANGES.get(r["version"], {}).get(lang) or r[lang]


def download_btn(t, label, cls="btn"):
    """Download link to the latest release."""
    ico = icon("windows") if cls == "btn" else ""
    text = f"<span>{label}</span>" if ico else label
    return f'<a class="{cls}" href="{DOWNLOAD}" rel="noopener">{ico}{text}</a>'


def head(t, url, title, desc, pl_url, en_url, prefix, extra=""):
    alt_locale = "en_US" if t["lang"] == "pl" else "pl_PL"
    og_image = BASE + "deadlock-overlay-counters.jpg"
    return f"""<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="pl" href="{pl_url}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="x-default" href="{en_url}">
<meta name="theme-color" content="#0e1014">
<link rel="icon" type="image/png" sizes="32x32" href="{prefix}favicon-32.png">
<link rel="icon" type="image/png" sizes="256x256" href="{prefix}icon.png">
<link rel="apple-touch-icon" href="{prefix}apple-touch-icon.png">
{extra}<meta property="og:type" content="website">
<meta property="og:site_name" content="Deadlock Assist">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="842">
<meta property="og:image:height" content="527">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:alt" content="{e(t['shot_alt'])}">
<meta property="og:locale" content="{t['locale']}">
<meta property="og:locale:alternate" content="{alt_locale}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{og_image}">
<meta name="twitter:image:alt" content="{e(t['shot_alt'])}">
{FONTS}
"""


def foot(t, T, switch_href):
    lang = t["lang"]
    links = f'<a href="{BASE}{t["counters"]["path"]}">{T(t["counters"]["index_h1"])}</a>'
    links += f'<a href="{BASE}{t["patches"]["path"]}">{T(t["patches"]["index_h1"])}</a>'
    links += f'<a href="{BASE}{t["changes"]["path"]}">{T(t["changes"]["h1"])}</a>'
    links += "".join(f'<a href="{e(h)}" rel="noopener">{T(l)}</a>' for h, l in t["links"])
    links += f'<a href="{switch_href}" hreflang="{"en" if lang == "pl" else "pl"}">{T(t["switch"][2])}</a>'
    return f"""<footer class="wrap foot">
  <nav aria-label="links">{links}</nav>
  <p>{T(t['footer'])}</p>
</footer>
</body>
</html>
"""


def page(t):
    lang = t["lang"]
    T = lambda s: html.escape(typeset(s, lang), quote=True)  # noqa: E731
    prefix = "" if t["path"] == "" else "../"
    url = BASE + t["path"]
    ids = t["ids"]
    ld_app = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Deadlock Assist",
        "description": t["description"],
        "url": url,
        "applicationCategory": "GameApplication",
        "operatingSystem": "Windows 10, Windows 11",
        "inLanguage": ["pl", "en"],
        "isAccessibleForFree": True,
        "softwareVersion": CHANGELOG[0]["version"],
        "dateModified": CHANGELOG[0]["date"],
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "downloadUrl": DOWNLOAD,
        "featureList": t["feature_list"],
        "screenshot": [BASE + "deadlock-overlay-counters.jpg", BASE + "deadlock-overlay-tab.webp",
                       BASE + "deadlock-match-history.webp"],
        "image": BASE + "icon.png",
        "author": {"@type": "Person", "name": "adam2s", "url": "https://github.com/adam2s"},
    }
    ld_faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]
        ],
    }
    nav = "".join(f'<a href="#{i}">{T(l)}</a>' for i, l in t["nav"])
    badges = "".join(f"<li>{T(b)}</li>" for b in t["badges"])
    feats = "".join(
        f'<article class="card">{icon(i)}<h3>{T(h)}</h3><p>{T(p)}</p></article>' for i, h, p in t["features"]
    )
    how = "".join(f"<li><h3>{T(h)}</h3><p>{T(p)}</p></li>" for h, p in t["how"])
    gallery = "".join(
        f'<figure><a href="{prefix}{full}" target="_blank" rel="noopener">'
        f'<img src="{prefix}{f}" alt="{T(a)}" width="842" height="527" loading="lazy" decoding="async"></a>'
        f"<figcaption>{T(c)}</figcaption></figure>"
        for f, full, a, c in t["gallery"]
    )

    def stat(n, now, before, lab, text, was):
        meter = ""
        side = "left" if (before or 0) < 35 else "right" if (before or 0) > 65 else "mid"
        if now is not None:
            meter = (
                f'<div class="meter" role="img" aria-label="{T(n)} · {T(was)}"><i style="width:{now}%"></i>'
                f'<b style="left:{before}%"></b></div>'
                f'<div class="meter-legend" aria-hidden="true"><span class="{side}" style="left:{before}%">{T(was)}</span></div>'
            )
        elif was:
            meter = f'<p class="stat-ref">{T(was)}</p>'
        return (
            f'<li class="stat"><p class="stat-num">{unit(T(n))}</p><p class="stat-label">{T(lab)}</p>{meter}'
            f"<p>{T(text)}</p></li>"
        )

    proof = "".join(stat(*p) for p in t["proof"])
    safe = "".join(f"<li>{T(s)}</li>" for s in t["safe"])
    faq = "".join(f"<details><summary>{T(q)}</summary><p>{T(a)}</p></details>" for q, a in t["faq"])
    cta = download_btn(t, T(t["cta"]))
    preload = f'<link rel="preload" as="image" type="image/webp" href="{prefix}deadlock-overlay-counters.webp" fetchpriority="high">\n'
    return head(t, url, t["title"], t["description"], BASE, BASE + "en/", prefix, preload) + f"""<script type="application/ld+json">{json.dumps(ld_app, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(ld_faq, ensure_ascii=False)}</script>
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">{T(t['skip'])}</a>
<header class="top wrap">
  <a class="logo" href="./"><img src="{prefix}favicon-32.png" srcset="{prefix}icon.png 2x" alt="" width="32" height="32">DEADLOCK <span>ASSIST</span></a>
  <nav aria-label="menu">{nav}<a href="{t['counters']['path'].removeprefix('en/')}">{T(t['counters']['nav'])}</a><a href="{t['patches']['path'].removeprefix('en/')}">{T(t['patches']['nav'])}</a><a href="{t['changes']['path'].removeprefix('en/')}">{T(t['changes']['nav'])}</a><a class="lang" href="{t['switch'][0]}" hreflang="{'en' if lang == 'pl' else 'pl'}"><span class="long">{T(t['switch'][1])}</span><span class="short">{'EN' if lang == 'pl' else 'PL'}</span></a>{download_btn(t, T(t['cta_short']), 'btn sm')}</nav>
</header>
<main id="main">
<section class="hero wrap">
  <div class="hero-text">
    <p class="eyebrow">{' · '.join(f'<span class="nw">{T(x)}</span>' for x in t['eyebrow'].split(' · '))}</p>
    <h1>{T(t['h1'])}</h1>
    <p class="lead">{T(t['lead'])}</p>
    <p class="proof-line"><a href="#{ids['results']}"><strong>{T(t['proof_line'][0])}</strong> {T(t['proof_line'][1])}</a></p>
    <div class="actions">{cta}<a class="btn ghost" href="#{ids['gallery']}">{T(t['cta2'])}</a></div>
    <p class="note">{T(t['hero_note'])}<span class="desk"><br>{T(t['smartscreen'])}</span></p>
    <ul class="badges">{badges}</ul>
  </div>
  <figure class="hero-shot"><picture><source type="image/webp" srcset="{prefix}deadlock-overlay-counters.webp"><img src="{prefix}deadlock-overlay-counters.jpg" alt="{T(t['shot_alt'])}" width="842" height="527" fetchpriority="high"></picture></figure>
</section>

<section id="{ids['features']}" class="wrap">
  <h2>{T(t['features_h'])}</h2>
  <div class="grid">{feats}</div>
</section>

<section id="{ids['gallery']}" class="wrap">
  <h2>{T(t['gallery_h'])}</h2>
  <div class="gallery">{gallery}</div>
</section>

<section id="{ids['results']}" class="wrap results">
  <h2>{T(t['proof_h'])}</h2>
  <p class="section-lead">{T(t['proof_lead'])}</p>
  <ul class="stats">{proof}</ul>
  <p class="note">{T(t['proof_note'])}</p>
</section>

{home_counters(t, prefix, T)}
<section id="{ids['safety']}" class="wrap">
  <div class="safe">
    <h2>{icon('lock')}{T(t['safe_h'])}</h2>
    <p class="section-lead">{T(t['safe_lead'])}</p>
    <ul class="checks">{safe}</ul>
    <p class="note">{T(t['safe_note'])}</p>
  </div>
</section>

<section id="{ids['start']}" class="wrap">
  <h2>{T(t['how_h'])}</h2>
  <ol class="steps">{how}</ol>
</section>

<section id="{ids['faq']}" class="wrap">
  <h2>{T(t['faq_h'])}</h2>
  <div class="faq">{faq}</div>
</section>

<section class="wrap final">
  <h2>{T(t['final_h'])}</h2>
  <p class="section-lead">{T(t['final_lead'])}</p>
  <div class="actions center">{cta}<a class="btn kofi" href="{KOFI}" rel="noopener">{icon('heart')}<span>{T(t['kofi'])}</span></a></div>
  <p class="note">{T(t['cta_note'])}<br>{T(t['smartscreen'])}</p>
</section>
</main>
""" + foot(t, T, t["switch"][0])


COUNTERS_FILE = Path(__file__).with_name("counters.json")
COUNTERS = json.loads(COUNTERS_FILE.read_text()) if COUNTERS_FILE.exists() else None
OUT = Path("docs")


def sub_header(t, T, prefix, home, switch_url):
    """Header of the pages under the home page: logo, home link, language switch, download."""
    other = "en" if t["lang"] == "pl" else "pl"
    return f"""<a class="skip" href="#main">{T(t['skip'])}</a>
<header class="top wrap">
  <a class="logo" href="{home}"><img src="{prefix}favicon-32.png" srcset="{prefix}icon.png 2x" alt="" width="32" height="32">DEADLOCK <span>ASSIST</span></a>
  <nav aria-label="menu"><a href="{home}">{T(t['changes']['home'])}</a><a class="lang" href="{switch_url}" hreflang="{other}"><span class="long">{T(t['switch'][1])}</span><span class="short">{other.upper()}</span></a>{download_btn(t, T(t['cta_short']), 'btn sm')}</nav>
</header>"""


def img_src(kind, key, remote, prefix):
    """The icon saved next to the pages, or the remote one until it is downloaded."""
    local = f"img/{kind}/{key}.webp"
    return "/" + local if (OUT / local).exists() else remote


def millions(n, lang):
    """Purchase count rounded to millions, so the sentence needs no plural forms."""
    c = (PL if lang == "pl" else EN)["counters"]
    v = f"{n / 1e6:.1f}".replace(".", "," if lang == "pl" else ".")
    return v + (NB if lang == "pl" else "") + c["million"]


def long_date(d, lang):
    y, m, day = (int(x) for x in d.split("-"))
    month = (PL if lang == "pl" else EN)["changes"]["months"][m - 1]
    return f"{day}{NB}{month} {y}" if lang == "pl" else f"{month}{NB}{day}, {y}"


def build_strip(t, hero, prefix, T):
    """The hero's typical build as a row of item tiles."""
    c = t["counters"]
    items = COUNTERS["items"]
    out = []
    for b in hero.get("build", []):
        it = items[str(b["id"])]
        slot = it.get("slot") or "weapon"
        img = f'<img src="{img_src("items", b["id"], it["img"], prefix)}" alt="" width="40" height="40" loading="lazy" decoding="async">'
        out.append(f'<li class="slot-{slot}">{img}<span class="bt"><b>{e(it["en"])}</b>'
                   f'<small>{round(b["min"])}{NB}{c["min"]} · {round(100 * b["share"])}%</small></span></li>')
    return f'<ol class="build">{"".join(out)}</ol>'


def counter_rows(t, hero, prefix, T, start, stop):
    """Counter items of the hero as ranked rows."""
    lang = t["lang"]
    c = t["counters"]
    items = COUNTERS["items"]
    top = max(i["points"] for i in hero["items"])
    rows = []
    for rank, i in enumerate(hero["items"][start:stop], start + 1):
        it = items[str(i["id"])]
        slot = it.get("slot") or "weapon"
        alt = f' · {c["alt"]}: {e(it["pl"])}' if lang == "pl" and it["pl"] != it["en"] else ""
        rows.append(
            f'<li class="ci slot-{slot}"><span class="rank">{rank}</span>'
            f'<img src="{img_src("items", i["id"], it["img"], prefix)}" alt="" width="40" height="40" loading="lazy" decoding="async">'
            f'<span class="ci-name"><strong>{e(it["en"])}</strong><small>{T(c["slots"].get(slot, slot))} · {cost(it["cost"], lang)} {T(c["souls"])}{alt}</small></span>'
            f'<span class="ci-edge"><b>{pts(i["points"], lang)}</b><i style="width:{max(8, round(100 * i["points"] / top))}%"></i></span></li>'
        )
    return "".join(rows)


def pts(p, lang):
    sep = "," if lang == "pl" else "."
    return f"+{p:.1f}".replace(".", sep) + NB + ('<span class="u">p.p.</span>' if lang == "pl" else '<span class="u">pp</span>')


def cost(n, lang):
    return f"{n:,}".replace(",", NB if lang == "pl" else ",")


def home_counters(t, prefix, T):
    """Home page example: the most played hero's build and its two best counters."""
    if not COUNTERS:
        return ""
    c = t["counters"]
    hero = max(COUNTERS["heroes"], key=lambda h: h["matches"])
    name = hero["name"]
    link = c["path"].removeprefix("en/")
    first = COUNTERS["items"][str(hero["items"][0]["id"])]["en"]
    legend = T(c["home_legend"].format(pts="{pts}", hero=name, item=first)).replace(
        "{pts}", f'<strong>{pts(hero["items"][0]["points"], t["lang"])}</strong>', 1)
    return f"""<section id="{'kontry' if t['lang'] == 'pl' else 'counters'}" class="wrap home-counters">
  <h2>{T(c['home_h'].format(hero=name))}</h2>
  <p class="section-lead">{T(c['home_lead'])}</p>
  <h3 class="ci-cap">{T(c['build_h'].format(hero=name))}</h3>
  {build_strip(t, hero, prefix, T)}
  <h3 class="ci-cap">{T(c['best_h'].format(hero=name))}</h3>
  <ol class="ci-list">{counter_rows(t, hero, prefix, T, 0, 2)}</ol>
  <p class="note">{legend}</p>
  <div class="actions"><a class="btn ghost" href="{link}">{T(c['home_all'].format(n=len(COUNTERS['heroes'])))}</a><a class="more-link" href="{link}{hero['slug']}/">{T(c['home_one'].format(hero=name))} →</a></div>
</section>
"""


def counters_index(t):
    lang = t["lang"]
    c = t["counters"]
    T = lambda s: html.escape(typeset(s, lang), quote=True)  # noqa: E731
    prefix = "../" * c["path"].count("/")
    url = BASE + c["path"]
    home = BASE + t["path"]
    other = EN if lang == "pl" else PL
    cards = "".join(
        f'<li><a href="{h["slug"]}/"><img src="{img_src("heroes", h["slug"], h["img"], prefix)}" alt="" width="48" height="48" '
        f'loading="lazy" decoding="async"><span>{e(h["name"])}</span></a></li>'
        for h in COUNTERS["heroes"]
    )
    ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Deadlock Assist", "item": home},
            {"@type": "ListItem", "position": 2, "name": c["index_h1"], "item": url},
        ],
    }
    return head(t, url, c["index_title"], c["index_desc"], BASE + PL["counters"]["path"], BASE + EN["counters"]["path"],
                prefix) + f"""<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{CSS}</style>
</head>
<body>
{sub_header(t, T, prefix, home, BASE + other["counters"]["path"])}
<main id="main" class="wrap counters">
  <h1>{T(c['index_h1'])}</h1>
  <p class="section-lead">{T(c['index_lead'])}</p>
  <p class="meta">{T(c['data'].format(n=millions(sum(h['matches'] for h in COUNTERS['heroes']), lang), date=long_date(COUNTERS['date'], lang)))}</p>
  <ul class="hero-grid">{cards}</ul>
</main>
""" + foot(t, T, BASE + other["counters"]["path"])


def recent_patch(t, hero, T):
    """Link from a counter page to the latest patch that changed the hero."""
    if not PATCHES:
        return ""
    for p in PATCHES["patches"]:
        if any(PATCHES["heroes"][str(h["id"])]["slug"] == hero["slug"] for h in p["heroes"]):
            c = t["patches"]
            return (f'\n  <p class="pn-recent"><a href="{patch_url(t, p)}#hero-{hero["slug"]}">'
                    f'{T(c["hero_recent"].format(hero=hero["name"], date=patch_label(t, p)))} →</a></p>')
    return ""


def counter_page(t, hero):
    lang = t["lang"]
    c = t["counters"]
    T = lambda s: html.escape(typeset(s, lang), quote=True)  # noqa: E731
    prefix = "../" * (c["path"].count("/") + 1)
    path = f'{c["path"]}{hero["slug"]}/'
    url = BASE + path
    home = BASE + t["path"]
    other = EN if lang == "pl" else PL
    name = hero["name"]
    items = COUNTERS["items"]
    sep = "," if lang == "pl" else "."
    first = items[str(hero["items"][0]["id"])]
    num = f'{hero["items"][0]["points"]:.1f}'.replace(".", sep)
    explain = T(c["explain"].format(pts="{pts}", item=first["en"], hero=name, num=num)).replace(
        "{pts}", f'<strong>{pts(hero["items"][0]["points"], lang)}</strong>', 1)
    rest = len(hero["items"]) - 2
    top3 = ", ".join(items[str(i["id"])]["en"] for i in hero["items"][:3])
    others = "".join(
        f'<li><a href="../{h["slug"]}/"><img src="{img_src("heroes", h["slug"], h["img"], prefix)}" alt="" width="32" height="32" '
        f'loading="lazy" decoding="async">{e(h["name"])}</a></li>'
        for h in COUNTERS["heroes"] if h["slug"] != hero["slug"]
    )
    n_others = len(COUNTERS["heroes"]) - 1

    def list_item(n, i):
        it = items[str(i["id"])]
        img = img_src("items", i["id"], it["img"], prefix)
        li = {"@type": "ListItem", "position": n, "name": it["en"], "image": BASE + img[1:] if img.startswith("/") else img}
        if lang == "pl" and it["pl"] != it["en"]:
            li["alternateName"] = it["pl"]
        return li
    ld = [
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Deadlock Assist", "item": home},
                {"@type": "ListItem", "position": 2, "name": c["index_h1"], "item": BASE + c["path"]},
                {"@type": "ListItem", "position": 3, "name": name, "item": url},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": c["h1"].format(hero=name),
            "itemListOrder": "https://schema.org/ItemListOrderDescending",
            "itemListElement": [list_item(n, i) for n, i in enumerate(hero["items"], 1)],
        },
    ]
    n = millions(hero["matches"], lang)
    return head(t, url, c["title"].format(hero=name), c["desc"].format(hero=name, top=top3),
                f'{BASE}{PL["counters"]["path"]}{hero["slug"]}/', f'{BASE}{EN["counters"]["path"]}{hero["slug"]}/',
                prefix) + f"""<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{CSS}</style>
</head>
<body>
{sub_header(t, T, prefix, home, f'{BASE}{other["counters"]["path"]}{hero["slug"]}/')}
<main id="main" class="wrap counters">
  <nav class="crumbs" aria-label="breadcrumbs"><a href="../">{T(c['index_h1'])}</a> › {e(name)}</nav>
  <div class="hero-head"><img src="{img_src("heroes", hero["slug"], hero["img"], prefix)}" alt="" width="64" height="64"><h1>{T(c['h1'].format(hero=name))}</h1></div>
  <p class="section-lead">{T(c['lead'].format(hero=name))}</p>
  <p class="meta">{T(c['data'].format(n=n, date=long_date(COUNTERS['date'], lang)))}</p>{recent_patch(t, hero, T)}
  <h2 class="ci-cap">{T(c['build_h'].format(hero=name))}</h2>
  {build_strip(t, hero, prefix, T)}
  <p class="note">{T(c['build_note'].format(hero=name))}</p>
  <h2 class="ci-cap" id="edge">{T(c['best_h'].format(hero=name))}</h2>
  <ol class="ci-list" aria-labelledby="edge">{counter_rows(t, hero, prefix, T, 0, 2)}</ol>
  <p class="note">{explain}</p>
  <details class="ci-more"><summary>{T(c['more'])} ({rest})</summary><ol class="ci-list" start="3">{counter_rows(t, hero, prefix, T, 2, None)}</ol></details>
  <section class="ci-cta"><h2>{T(c['cta_h'])}</h2><p>{T(c['cta_p'])}</p><div class="actions">{download_btn(t, T(t['cta']))}</div></section>
  <details class="ci-others"><summary><h2>{T(c['others'])} ({n_others})</h2></summary><ul>{others}</ul></details>
</main>
""" + foot(t, T, f'{BASE}{other["counters"]["path"]}{hero["slug"]}/')


def changes_page(t, shown=4):
    """Changelog page from site/changelog.json: the newest versions open, the rest folded."""
    lang = t["lang"]
    c = t["changes"]
    T = lambda s: html.escape(typeset(s, lang), quote=True)  # noqa: E731
    prefix = "../" * c["path"].count("/")
    url = BASE + c["path"]
    pl_url, en_url = BASE + PL["changes"]["path"], BASE + EN["changes"]["path"]
    home = BASE + t["path"]

    def when(d):
        y, m, day = (int(x) for x in d.split("-"))
        month = c["months"][m - 1]
        return f"{day}{NB}{month} {y}" if lang == "pl" else f"{month}{NB}{day}, {y}"

    def release(r):
        items = "".join(f"<li>{T(x)}</li>" for x in site_changes(r, lang))
        tag = f' <span class="tag">{T(c["latest"])}</span>' if r is CHANGELOG[0] else ""
        return (f'<article class="release" id="v{r["version"]}"><h2>{T(c["version"])} {r["version"]}{tag}'
                f' <time datetime="{r["date"]}">{when(r["date"])}</time></h2><ul>{items}</ul></article>')

    newest = "".join(release(r) for r in CHANGELOG[:shown])
    rest = CHANGELOG[shown:]
    older = (f'<details class="older"><summary>{T(c["older"])} ({rest[-1]["version"]}–{rest[0]["version"]})</summary>'
             + "".join(release(r) for r in rest) + "</details>") if rest else ""
    ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Deadlock Assist", "item": home},
            {"@type": "ListItem", "position": 2, "name": c["h1"], "item": url},
        ],
    }
    switch = (EN if lang == "pl" else PL)["changes"]["path"]
    return head(t, url, c["title"], c["description"], pl_url, en_url, prefix) + f"""<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">{T(t['skip'])}</a>
<header class="top wrap">
  <a class="logo" href="{home}"><img src="{prefix}favicon-32.png" srcset="{prefix}icon.png 2x" alt="" width="32" height="32">DEADLOCK <span>ASSIST</span></a>
  <nav aria-label="menu"><a href="{home}">{T(c['home'])}</a><a class="lang" href="{BASE}{switch}" hreflang="{'en' if lang == 'pl' else 'pl'}"><span class="long">{T(t['switch'][1])}</span><span class="short">{'EN' if lang == 'pl' else 'PL'}</span></a>{download_btn(t, T(t['cta_short']), 'btn sm')}</nav>
</header>
<main id="main" class="wrap changes">
  <h1>{T(c['h1'])}</h1>
  <p class="section-lead">{T(c['lead'])}</p>
  <p class="highlight"><a href="#v1.2.6">{T(c['highlight']).replace('81%', '<strong>81%</strong>', 1)}</a></p>
  {newest}
  {older}
  <div class="end"><p class="note">{T(c['cta_note'])}</p><div class="actions">{download_btn(t, T(t['cta']))}</div></div>
</main>
""" + foot(t, T, BASE + switch)


PATCHES_FILE = Path(__file__).with_name("patches.json")
PATCHES = json.loads(PATCHES_FILE.read_text()) if PATCHES_FILE.exists() else None
NUM = r"[+\-−]?\d[\d.,]*(?:[/+]\d[\d.,]*)*(?:%|s|m|k|m/s)?"
THIN = 3  # patches with fewer changed lines are not worth a search result: noindex, left out of the sitemap


def plural(n, forms, lang):
    """1 bohater, 2 bohaterów → Polish needs three forms; English two."""
    if lang != "pl":
        return forms[0] if n == 1 else forms[1]
    if n == 1:
        return forms[0]
    return forms[1] if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14) else forms[2]


def note_line(s):
    """One line of the official notes: old value muted, new value bold ("from <s>26s</s> to <b>28s</b>")."""
    s = e(s)
    if "→" in s or "-&gt;" in s:  # ranges like "18m→54m": the text already shows the change
        return s
    # "from 6s Unstoppable to 5s": a few words may sit between the old value and "to"
    return re.sub(rf"\bfrom ({NUM})((?: [A-Za-z][\w-]*){{0,3}})? to ({NUM})(?![\w.])",
                  r'from <span class="was">\1</span>\2 to <b class="now">\3</b>', s)


def short_date(d, lang):
    y, m, day = d.split("-")
    return f"{int(day)}.{m}.{y}" if lang == "pl" else f"{y}-{m}-{day}"


def general_count(p):
    return sum(len(x) for g in p["general"] for x in g["paras"])


def hero_count(h):
    return len(h["lines"]) + sum(len(a["lines"]) for a in h["abilities"])


def is_thin(p):
    return general_count(p) + sum(len(i["lines"]) for i in p["items"]) + sum(hero_count(h) for h in p["heroes"]) < THIN


def patch_names(p):
    """Heroes first, then items: what the patch is about, for titles and descriptions."""
    out = [PATCHES["heroes"][str(h["id"])]["name"] for h in p["heroes"]]
    out += [PATCHES["items"][str(i["id"])]["en"] for i in p["items"]]
    return out


def patch_counts(t, p, T):
    c = t["patches"]
    lang = t["lang"]
    parts = []
    for n, forms in ((len(p["heroes"]), c["n_heroes"]), (len(p["items"]), c["n_items"]), (general_count(p), c["n_general"])):
        if n:
            parts.append(f"{n}{NB}{plural(n, forms, lang).replace(' ', NB)}")
    return " · ".join(parts)


def patch_kind(t, p):
    """What tells a patch apart from another one on the same day: Hero Labs, or the second update that day."""
    c = t["patches"]
    if p.get("hero_lab"):
        return c["hero_lab"]
    m = re.search(r"-(\d+)$", p["slug"][10:])
    return c["second"].format(n=int(m.group(1)) + 1) if m else None


def patch_label(t, p):
    """"16 września 2026", or "18 października 2024 (Aktualizacja 2)" for a second patch that day."""
    kind = patch_kind(t, p)
    when = long_date(p["date"], t["lang"])
    return f"{when} ({kind})" if kind else when


def summary(t, p):
    """Two sentences of the page's own: how much the patch changes and what changed most."""
    c = t["patches"]
    lang = t["lang"]
    parts = [f"{n} {plural(n, c['parts'][k], lang)}" for k, n in
             (("heroes", len(p["heroes"])), ("items", len(p["items"])), ("general", general_count(p))) if n]
    joined = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + f" {c['and']} " + parts[-1]
    out = c["summary"].format(date=long_date(p["date"], lang), parts=joined)
    sizes = [(hero_count(h), PATCHES["heroes"][str(h["id"])]["name"]) for h in p["heroes"]]
    sizes += [(len(i["lines"]), PATCHES["items"][str(i["id"])]["en"]) for i in p["items"]]
    sizes = sorted((x for x in sizes if x[0] > 1), key=lambda x: (-x[0], x[1]))[:4]
    if sizes:
        out += " " + c["most"].format(list=", ".join(f"{name} ({n})" for n, name in sizes))
    return out


def hero_img(h, prefix, size, extra=""):
    hh = PATCHES["heroes"][str(h["id"])]
    return (f'<img src="{img_src("heroes", hh["slug"], hh["img"], prefix)}" alt="{extra}" width="{size}" height="{size}" '
            f'loading="lazy" decoding="async">')


def icon_strip(p, prefix, limit=12):
    """Portraits of the changed heroes, then item icons, as one row."""
    imgs = []
    for h in p["heroes"]:
        hh = PATCHES["heroes"][str(h["id"])]
        imgs.append(f'<img class="ps-h" src="{img_src("heroes", hh["slug"], hh["img"], prefix)}" alt="{e(hh["name"])}" title="{e(hh["name"])}" '
                    f'width="32" height="32" loading="lazy" decoding="async">')
    for i in p["items"]:
        it = PATCHES["items"][str(i["id"])]
        imgs.append(f'<img class="ps-i slot-{it["slot"]}" src="{img_src("items", i["id"], it["img"], prefix)}" alt="{e(it["en"])}" '
                    f'title="{e(it["en"])}" width="32" height="32" loading="lazy" decoding="async">')
    more = len(imgs) - limit
    tail = f'<span class="ps-more">+{more}</span>' if more > 0 else ""
    return f'<span class="ps">{"".join(imgs[:limit])}{tail}</span>' if imgs else ""


def patch_url(t, p):
    return f'{BASE}{t["patches"]["path"]}{p["slug"]}/'


def patches_index(t):
    lang = t["lang"]
    c = t["patches"]
    T = lambda s: html.escape(typeset(s, lang), quote=True)  # noqa: E731
    prefix = "../" * c["path"].count("/")
    url = BASE + c["path"]
    home = BASE + t["path"]
    other = EN if lang == "pl" else PL
    ps = PATCHES["patches"]
    first = ps[0]
    kind = patch_kind(t, first)
    featured = (
        f'<a class="pn-feat" href="{first["slug"]}/"><span class="pn-feat-top"><span class="tag">{T(c["latest"])}</span>'
        f'{f"<span class=pn-kind>{T(kind)}</span>" if kind else ""}</span>'
        f'<strong>{long_date(first["date"], lang)}</strong>'
        f'<span class="pn-count">{T(patch_counts(t, first, T))}</span>{icon_strip(first, prefix, 16)}'
        f'<span class="more-link">{T(c["open"])} →</span></a>'
    )
    rows, year = [], None
    this_year = first["date"][:4]
    for p in ps[1:]:
        y = p["date"][:4]
        if y != year:
            if year:
                rows.append("</ol>" if year == this_year else "</ol></details>")
            n = sum(1 for x in ps[1:] if x["date"][:4] == y)
            # The current year stays open; older years fold so the page does not run for metres.
            rows.append(f'<h2 class="ci-cap pn-year" id="y{y}">{y}</h2><ol class="pn-list">' if y == this_year else
                        f'<details class="pn-old" id="y{y}"><summary><h2 class="pn-year">{y}</h2><span>{n}</span></summary><ol class="pn-list">')
            year = y
        k = patch_kind(t, p)
        rows.append(
            f'<li><a href="{p["slug"]}/"><time datetime="{p["date"]}">{long_date(p["date"], lang)}</time>'
            f'<span class="pn-meta">{f"<span class=pn-kind>{T(k)}</span>" if k else ""}<span class="pn-count">{T(patch_counts(t, p, T))}</span></span>'
            f'{icon_strip(p, prefix, 8)}</a></li>'
        )
    if year:
        rows.append("</ol>" if year == this_year else "</ol></details>")
    counts = {}
    for x in ps:
        counts[x["date"][:4]] = counts.get(x["date"][:4], 0) + 1
    years = "".join(f'<a href="#y{y}">{y} <span>{n}</span></a>' for y, n in counts.items())
    ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Deadlock Assist", "item": home},
            {"@type": "ListItem", "position": 2, "name": c["index_h1"], "item": url},
        ],
    }
    return head(t, url, c["index_title"], c["index_desc"], BASE + PL["patches"]["path"], BASE + EN["patches"]["path"],
                prefix) + f"""<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{CSS}</style>
</head>
<body class="dl">
{sub_header(t, T, prefix, home, BASE + other["patches"]["path"])}
<main id="main" class="wrap patches pn-index">
  <h1>{T(c['index_h1'])}</h1>
  <p class="section-lead">{T(c['index_lead'])}</p>
  <aside class="pn-nav pn-side"><nav class="pn-toc" aria-label="{T(c['years'])}">{years}</nav>
    <div class="pn-side-cta"><p>{T(c['cta_index'])}</p>{download_btn(t, T(t['cta_short']), 'btn sm')}</div></aside>
  {featured}
  {"".join(rows)}
  <p class="note">{T(c['updated'].format(date=long_date(PATCHES['date'], lang)))} <a href="{PATCHES['source']}" rel="noopener">{T(c['archive'])}</a></p>
</main>
<script>function o(){{var d=document.getElementById(location.hash.slice(1));if(d&&d.tagName==="DETAILS")d.open=true}}addEventListener("hashchange",o);o()</script>
""" + foot(t, T, BASE + other["patches"]["path"])


def patch_page(t, p, older, newer):
    lang = t["lang"]
    c = t["patches"]
    T = lambda s: html.escape(typeset(s, lang), quote=True)  # noqa: E731
    prefix = "../" * (c["path"].count("/") + 1)
    url = patch_url(t, p)
    home = BASE + t["path"]
    other = EN if lang == "pl" else PL
    label = patch_label(t, p)
    counter_slugs = {h["slug"] for h in COUNTERS["heroes"]} if COUNTERS else set()

    def ul(lines):
        return "<ul>" + "".join(f"<li>{note_line(x)}</li>" for x in lines) + "</ul>"

    sections, toc, jump = [], [], ""
    # Heroes first: most readers come for their hero; then items, then everything else.
    if p["heroes"]:
        cards = []
        for h in p["heroes"]:
            hh = PATCHES["heroes"][str(h["id"])]
            link = (f'<a class="more-link" href="{BASE}{t["counters"]["path"]}{hh["slug"]}/">{T(c["counters"].format(hero=hh["name"]))} →</a>'
                    if hh["slug"] in counter_slugs else "")
            body = ul(h["lines"]) if h["lines"] else ""
            for a in h["abilities"]:
                if "id" not in a:  # "Gun", "Rocket Jumping": a part of the hero without an ability icon
                    body += f'<div class="pn-ab pn-part"><h4>{e(a["name"])}</h4>{ul(a["lines"])}</div>'
                    continue
                ab = PATCHES["abilities"][str(a["id"])]
                alt = f' <small lang="pl">{e(ab["pl"])}</small>' if lang == "pl" and ab["pl"] != ab["en"] else ""
                body += (f'<div class="pn-ab"><h4><img src="{img_src("abilities", a["id"], ab["img"], prefix)}" alt="" width="28" height="28" '
                         f'loading="lazy" decoding="async">{e(ab["en"])}{alt}</h4>{ul(a["lines"])}</div>')
            cards.append(f'<article class="pn-card pn-hero" id="hero-{hh["slug"]}"><header>{hero_img(h, prefix, 40)}'
                         f'<span><h3>{e(hh["name"])}</h3>{link}</span></header>{body}</article>')
        sections.append(f'<section id="heroes" class="pn-sec"><h2>{T(c["heroes"])}</h2><div class="pn-heroes">{"".join(cards)}</div></section>')
        toc.append(("heroes", c["heroes"], len(p["heroes"])))
        if len(p["heroes"]) > 1:
            jump = f'<nav class="pn-jump" aria-label="{T(c["jump"])}">' + "".join(
                f'<a href="#hero-{PATCHES["heroes"][str(h["id"])]["slug"]}" title="{e(PATCHES["heroes"][str(h["id"])]["name"])}">'
                f'{hero_img(h, prefix, 36, e(PATCHES["heroes"][str(h["id"])]["name"]))}</a>' for h in p["heroes"]) + "</nav>"
    if p["items"]:
        groups = []
        for slot in ("weapon", "vitality", "spirit"):
            cards = []
            for i in p["items"]:
                it = PATCHES["items"][str(i["id"])]
                if it["slot"] != slot:
                    continue
                alt = f'<small lang="pl">{e(it["pl"])}</small>' if lang == "pl" and it["pl"] != it["en"] else ""
                price = f'<small>{cost(it["cost"], lang)} {T(c["souls"])}</small>' if it.get("cost") else ""
                cards.append(
                    f'<article class="pn-card slot-{slot}"><header>'
                    f'<img src="{img_src("items", i["id"], it["img"], prefix)}" alt="" width="44" height="44" loading="lazy" decoding="async">'
                    f'<span><h4>{e(it["en"])}</h4>{alt}{price}</span></header>{ul(i["lines"])}</article>'
                )
            if cards:
                groups.append(f'<h3 class="pn-slot slot-{slot}">{T(c["slots"][slot])} <span>{len(cards)}</span></h3>'
                              f'<div class="pn-grid">{"".join(cards)}</div>')
        sections.append(f'<section id="items" class="pn-sec"><h2>{T(c["items"])}</h2>{"".join(groups)}</section>')
        toc.append(("items", c["items"], len(p["items"])))
    if p["general"]:
        parts = []
        single = len(p["general"]) == 1
        for g in p["general"]:
            h = f"<h3>{e(g['head'])}</h3>" if g["head"] and not single else ""
            parts.append(h + "".join(ul(x) for x in g["paras"]))
        sections.append(f'<section id="general" class="pn-sec"><h2>{T(c["general"])}</h2><div class="pn-general">{"".join(parts)}</div></section>')
        toc.append(("general", c["general"], general_count(p)))
    toc_html = "".join(f'<a href="#{i}">{T(l)} <span>{n}</span></a>' for i, l, n in toc)
    source = f'<a href="{e(p["link"])}" rel="noopener">{T(c["source"])}</a> · ' if p.get("link") else ""
    lang_note = f' {T(c["lang_note"])}' if c["lang_note"] else ""
    pager = ""
    if older:
        pager += f'<a class="pn-prev" href="../{older["slug"]}/"><small>← {T(c["older"])}</small>{patch_label(t, older)}</a>'
    if newer:
        pager += f'<a class="pn-next" href="../{newer["slug"]}/"><small>{T(c["newer"])} →</small>{patch_label(t, newer)}</a>'
    names = [n for _, n in sorted(((hero_count(h), PATCHES["heroes"][str(h["id"])]["name"]) for h in p["heroes"]),
                                     key=lambda x: (-x[0], x[1]))]  # the most changed first: they make the click
    names += [n for _, n in sorted(((len(i["lines"]), PATCHES["items"][str(i["id"])]["en"]) for i in p["items"]),
                                   key=lambda x: (-x[0], x[1]))]
    names_txt = ", ".join(names[:6]) + ("…" if len(names) > 6 else "") if names else c["general"].lower()
    plain = label.replace(NB, " ")
    title = c["title"].format(date=plain)
    desc = c["desc"].format(date=short_date(p["date"], lang) if lang == "pl" else plain, names=names_txt).replace("….", "…")
    ld = [
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Deadlock Assist", "item": home},
                {"@type": "ListItem", "position": 2, "name": c["index_h1"], "item": BASE + c["path"]},
                {"@type": "ListItem", "position": 3, "name": c["h1"].format(date=plain), "item": url},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": desc,
            "datePublished": p["date"],
            "dateModified": p["date"],
            "inLanguage": lang,
            "url": url,
            "about": {"@type": "VideoGame", "name": "Deadlock", "publisher": "Valve"},
            "author": {"@type": "Organization", "name": "Deadlock Assist", "url": BASE},
            "image": BASE + "deadlock-overlay-counters.jpg",
        },
    ]
    robots = '<meta name="robots" content="noindex, follow">\n' if is_thin(p) else ""
    return head(t, url, title, desc, patch_url(PL, p), patch_url(EN, p), prefix, robots) + f"""<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{CSS}</style>
</head>
<body class="dl">
{sub_header(t, T, prefix, home, patch_url(other, p))}
<main id="main" class="wrap patches patch">
  <nav class="crumbs" aria-label="breadcrumbs"><a href="../">{T(c['index_h1'])}</a> › {label}</nav>
  <h1>{T(c['h1'].format(date=label))}</h1>
  <p class="pn-sum">{T(summary(t, p))}</p>
  <p class="note pn-src">{source}<a href="{PATCHES['source']}" rel="noopener">{T(c['archive'])}</a>.{lang_note}</p>
  {f'<div class="pn-nav"><nav class="pn-toc" aria-label="{T(c["on_page"])}">{toc_html}</nav>{jump}</div>' if len(toc) > 1 or jump else ""}
  {"".join(sections)}
  <section class="ci-cta"><h2>{T(c['cta_h'])}</h2><p>{T(c['cta_p'])}</p><div class="actions">{download_btn(t, T(t['cta']))}</div></section>
  <nav class="pn-pager" aria-label="{T(c['all'])}">{pager}</nav>
  <p><a class="more-link" href="../">{T(c['all'])} ({len(PATCHES['patches'])}) →</a></p>
</main>
<script>(function(){{var j=document.querySelectorAll(".pn-jump a");if(!j.length||!("IntersectionObserver" in window))return;
var by={{}};j.forEach(function(a){{by[a.hash.slice(1)]=a}});
var io=new IntersectionObserver(function(es){{es.forEach(function(x){{if(!x.isIntersecting)return;j.forEach(function(a){{a.classList.remove("active")}});if(by[x.target.id])by[x.target.id].classList.add("active")}})}},{{rootMargin:"-30% 0px -60% 0px"}});
document.querySelectorAll(".pn-hero").forEach(function(h){{io.observe(h)}})}})()</script>
""" + foot(t, T, patch_url(other, p))


def not_found():
    rows = "".join(
        f'<p><a class="btn" href="{BASE}{t["path"]}">{e(t["nf_link"])}</a></p>'
        f'<p><a class="btn ghost" href="{BASE}{t["counters"]["path"]}">{e(t["counters"]["index_h1"])}</a></p>'
        for t in (PL, EN)
    )
    return f"""<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>404 – Deadlock Assist</title>
<link rel="icon" type="image/png" sizes="32x32" href="{BASE}favicon-32.png">
<style>{CSS}</style>
</head>
<body>
<main class="wrap final" style="padding:96px 0">
  <p class="stat-num">404</p>
  <h1>{e(PL['nf_h'])} · {e(EN['nf_h'])}</h1>
  <div class="actions center" style="margin-top:28px">{rows}</div>
</main>
</body>
</html>
"""


def main():
    global OUT
    out = OUT = Path(sys.argv[1])
    (out / "en").mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page(PL))
    (out / "en" / "index.html").write_text(page(EN))
    (out / "404.html").write_text(not_found())
    for t in (PL, EN):
        (out / t["changes"]["path"]).mkdir(parents=True, exist_ok=True)
        (out / t["changes"]["path"] / "index.html").write_text(changes_page(t))
        if PATCHES:
            base = out / t["patches"]["path"]
            base.mkdir(parents=True, exist_ok=True)
            (base / "index.html").write_text(patches_index(t))
            ps = PATCHES["patches"]
            for n, pt in enumerate(ps):
                (base / pt["slug"]).mkdir(exist_ok=True)
                older = ps[n + 1] if n + 1 < len(ps) else None
                newer = ps[n - 1] if n else None
                (base / pt["slug"] / "index.html").write_text(patch_page(t, pt, older, newer))
        if COUNTERS:
            base = out / t["counters"]["path"]
            base.mkdir(parents=True, exist_ok=True)
            (base / "index.html").write_text(counters_index(t))
            for hero in COUNTERS["heroes"]:
                (base / hero["slug"]).mkdir(exist_ok=True)
                (base / hero["slug"] / "index.html").write_text(counter_page(t, hero))
    def entry(pl, en, day):
        alt = (
            f'    <xhtml:link rel="alternate" hreflang="pl" href="{BASE}{pl}"/>\n'
            f'    <xhtml:link rel="alternate" hreflang="en" href="{BASE}{en}"/>\n'
            f'    <xhtml:link rel="alternate" hreflang="x-default" href="{BASE}{en}"/>\n'
        )
        return "".join(f"  <url>\n    <loc>{BASE}{p}</loc>\n    <lastmod>{day}</lastmod>\n{alt}  </url>\n" for p in (pl, en))

    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + entry("", "en/", CHANGELOG[0]["date"])
        + entry(PL["changes"]["path"], EN["changes"]["path"], CHANGELOG[0]["date"])
        + (entry(PL["patches"]["path"], EN["patches"]["path"], PATCHES["patches"][0]["date"])
           + "".join(entry(f'{PL["patches"]["path"]}{p["slug"]}/', f'{EN["patches"]["path"]}{p["slug"]}/', p["date"])
                     for p in PATCHES["patches"] if not is_thin(p)) if PATCHES else "")
        + (entry(PL["counters"]["path"], EN["counters"]["path"], COUNTERS["date"])
           + "".join(entry(f'{PL["counters"]["path"]}{h["slug"]}/', f'{EN["counters"]["path"]}{h["slug"]}/', COUNTERS["date"])
                     for h in COUNTERS["heroes"]) if COUNTERS else "")
        + "</urlset>\n"
    )
    (out / ".nojekyll").write_text("")
    (out / "CNAME").write_text(DOMAIN + "\n")
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n")


main()
