"""Builds the Deadlock Assist landing page (PL at /, EN at /en/) into <out>/.

Usage: python3 -I site/build.py docs   (edit texts here, then rebuild; GitHub Pages serves docs/)
The changelog page reads site/changelog.json: refresh it with site/sync_changelog.py after an app release.
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
# Visit counter without cookies (goatcounter.com, site code "deadlock-assist"); "" turns it off.
GOATCOUNTER = "https://deadlock-assist.goatcounter.com/count"
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
        "niezwiązany z Valve. Dane o przedmiotach: deadlock-api.com. Statystyki odwiedzin bez cookies: GoatCounter."
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
    "changes": {
        "path": "en/changes/", "nav": "Changes", "title": "Deadlock Assist Changelog – Overlay Updates & Release Notes",
        "description": "What's new in every version of Deadlock Assist, the Deadlock overlay with counter items, builds and timers.",
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
        "affiliated with Valve. Item data: deadlock-api.com. Cookie-free visit stats: GoatCounter."
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
        s = re.sub(r"(?<![\w-])([aiouwzAIOUWZ]|na|do|od|po|ze|we|że|co|to|nie|ma|jak) ", "\\1" + NB, s)
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


def counter():
    return f'<script data-goatcounter="{GOATCOUNTER}" async src="https://gc.zgo.at/count.js"></script>\n' if GOATCOUNTER else ""


def download_btn(t, label, cls="btn"):
    """Download link; GoatCounter counts its clicks as "download"."""
    ico = icon("windows") if cls == "btn" else ""
    text = f"<span>{label}</span>" if ico else label
    return (f'<a class="{cls}" href="{DOWNLOAD}" rel="noopener" data-goatcounter-click="download" '
            f'data-goatcounter-title="{t["lang"]}">{ico}{text}</a>')


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
{counter()}"""


def foot(t, T, switch_href):
    lang = t["lang"]
    links = f'<a href="{BASE}{t["changes"]["path"]}">{T(t["changes"]["h1"])}</a>'
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
  <nav aria-label="menu">{nav}<a href="{t['changes']['path'].removeprefix('en/')}">{T(t['changes']['nav'])}</a><a class="lang" href="{t['switch'][0]}" hreflang="{'en' if lang == 'pl' else 'pl'}"><span class="long">{T(t['switch'][1])}</span><span class="short">{'EN' if lang == 'pl' else 'PL'}</span></a>{download_btn(t, T(t['cta_short']), 'btn sm')}</nav>
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
  <p class="highlight"><a href="#v1.2.6">{T(c['highlight'])}</a></p>
  {newest}
  {older}
  <div class="end"><p class="note">{T(c['cta_note'])}</p><div class="actions">{download_btn(t, T(t['cta']))}</div></div>
</main>
""" + foot(t, T, BASE + switch)


def not_found():
    rows = "".join(
        f'<p><a class="btn" href="{BASE}{t["path"]}">{e(t["nf_link"])}</a></p>' for t in (PL, EN)
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
    out = Path(sys.argv[1])
    (out / "en").mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page(PL))
    (out / "en" / "index.html").write_text(page(EN))
    (out / "404.html").write_text(not_found())
    for t in (PL, EN):
        (out / t["changes"]["path"]).mkdir(parents=True, exist_ok=True)
        (out / t["changes"]["path"] / "index.html").write_text(changes_page(t))
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
        + "</urlset>\n"
    )
    (out / ".nojekyll").write_text("")
    (out / "CNAME").write_text(DOMAIN + "\n")
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n")


main()
