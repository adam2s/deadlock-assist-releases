"""Builds the Deadlock Assist landing page (PL at /, EN at /en/) into <out>/.

Usage: python3 -I site/build.py docs   (edit texts here, then rebuild; GitHub Pages serves docs/)
"""
import html
import json
import sys
from pathlib import Path

BASE = "https://adam2s.github.io/deadlock-assist-releases/"
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


PL = {
    "lang": "pl",
    "path": "",
    "locale": "pl_PL",
    "title": "Deadlock Assist – darmowa nakładka z kontrami i buildami do Deadlocka",
    "description": (
        "Darmowy doradca do Deadlocka dla Windows: kontrprzedmioty pod skład wroga, co kupić teraz, "
        "timery obozów i Mid Bossa oraz historia meczów z analizą farmy. Bez Overwolf, bez reklam, "
        "bez czytania pamięci gry."
    ),
    "nav": [("#funkcje", "Funkcje"), ("#bezpieczenstwo", "Bezpieczeństwo"), ("#faq", "FAQ")],
    "switch": ("en/", "English"),
    "eyebrow": "Darmowa nakładka do Deadlocka · Windows 10/11",
    "h1": "Kontry, buildy i timery w Deadlocku, podpowiadane w trakcie meczu",
    "lead": (
        "Deadlock Assist rozpoznaje bohaterów wroga i ich przedmioty, a potem mówi, co kupić, "
        "żeby ich skontrować. Pilnuje obozów w dżungli i Mid Bossa, a po meczu pokazuje, "
        "co poprawić. Za darmo i bez Overwolf."
    ),
    "cta": "Pobierz dla Windows",
    "cta_note": "Instalator .exe · aktualizuje się sam",
    "cta2": "Zobacz funkcje",
    "shot_alt": (
        "Nakładka Deadlock Assist nad grą: kontry na linii, panel Kup teraz z najlepszym przedmiotem "
        "na wroga oraz zegar z timerami obozów i Mid Bossa"
    ),
    "badges": ["Za darmo", "Bez reklam i konta", "Bez Overwolf", "Nie czyta pamięci gry"],
    "features_h": "Co robi Deadlock Assist",
    "features_lead": (
        "Wszystko, czego zwykle szukasz w przerwie między walkami na stronach z buildami i tier listami, "
        "masz na ekranie w chwili, gdy jest potrzebne."
    ),
    "features": [
        ("counter", "Kontrprzedmioty pod skład wroga",
         "Rozpoznaje sześciu wrogów z górnego paska i podpowiada przedmioty, które najlepiej na nich działają: "
         "Healbane na leczenie, Silencer na bohaterów od umiejętności, Spirit Resilience na obrażenia duchowe. "
         "Przy każdej kontrze widzisz cenę i powód."),
        ("cart", "„Kup teraz” i następne zakupy",
         "Plan buildu z tysięcy meczów graczy na Twoim bohaterze, dopasowany do tego, co już masz i na co Cię "
         "stać. Gdy masz dość dusz, aplikacja pokazuje jeden najlepszy zakup, a nie listę do przewijania."),
        ("lane", "Kontry na linii",
         "Do 10. minuty podpowiada tanie przedmioty na rywali z Twojej linii, bo to wtedy wygrywa się "
         "lub przegrywa farmę."),
        ("eye", "Zakupy wrogów na bieżąco",
         "Po wciśnięciu Tab zapamiętuje przedmioty przeciwników. Gdy ktoś kupi np. Leech albo Unstoppable, "
         "doradca od razu zmienia rady i ostrzega Cię w nakładce."),
        ("clock", "Zegar, timery obozów i Mid Boss",
         "Widzi na minimapie, które obozy w dżungli zostały zabite, i odlicza ich odrodzenie. "
         "Pilnuje też Mid Bossa, wzmocnień i urny dusz, z kierunkiem, w którą stronę iść."),
        ("chart", "Historia meczów i analiza",
         "Każdy mecz trafia do historii: wynik, skład, kolejność zakupów i farma minuta po minucie "
         "w porównaniu z typowym graczem. Na końcu dostajesz krótkie podsumowanie, co poprawić."),
        ("book", "Dane gry po polsku i angielsku",
         "Przeglądarka bohaterów i przedmiotów z filtrami typu „co kontruje leczenie” albo „przedmioty "
         "z wyciszeniem”. Po każdym patchu widzisz, co się zmieniło w Twoich bohaterach i przedmiotach."),
        ("auto", "Działa sama",
         "Mecz startuje, gdy zegar gry pokaże pierwszą minutę, a F10 go kończy i zapisuje. Nakładka nie "
         "przechwytuje myszy, a nowe wersje instalują się jednym kliknięciem."),
    ],
    "how_h": "Jak to działa",
    "how": [
        ("Zainstaluj", "Pobierz instalator, uruchom go i włącz Deadlocka w trybie okna bez ramek (Borderless)."),
        ("Graj", "Asystent sam wykryje start meczu, rozpozna bohaterów i pokaże kontry w nakładce. "
                 "Przytrzymaj Tab co jakiś czas, żeby odświeżyć przedmioty wszystkich graczy."),
        ("Popraw się", "Po meczu (F10) sprawdź w Historii farmę, zakupy i podsumowanie z tym, "
                       "co zrobić lepiej w kolejnym."),
    ],
    "gallery_h": "Jak to wygląda",
    "gallery": [
        ("nakladka-tab.png", "Nakładka po wciśnięciu Tab: przedmioty wszystkich graczy, kontry i timery",
         "Po Tab: zakupy wszystkich graczy i kontry na nie"),
        ("historia.png", "Historia meczów: wyniki, bohaterowie, przeciwnicy i kolejność zakupów",
         "Historia: wyniki, przeciwnicy i zakupy z każdego meczu"),
    ],
    "why_h": "Dlaczego Deadlock Assist",
    "why": [
        ("Osobna aplikacja, nie wtyczka Overwolf", "Lekki program (Tauri), który nie wymaga konta, "
         "nie wyświetla reklam i nie ładuje dodatkowej platformy w tle."),
        ("Rady w trakcie meczu, nie w przeglądarce", "Strony z buildami i tier listami są świetne przed meczem. "
         "Deadlock Assist reaguje na to, co dzieje się teraz: kto jest w drużynie wroga i co właśnie kupił."),
        ("Twoje dane zostają u Ciebie", "Historia meczów jest zapisywana lokalnie. Zrzuty ekranu służą tylko do "
         "odczytu i są usuwane po zapisaniu meczu."),
        ("Po polsku", "Interfejs, rady i opisy przedmiotów są po polsku, a dane gry możesz przełączyć na angielski."),
    ],
    "safe_h": "Bezpieczeństwo",
    "safe_lead": "Deadlock Assist działa jak program do nagrywania ekranu, a nie jak cheat.",
    "safe": [
        "Nie czyta pamięci gry, nie wstrzykuje kodu i nie modyfikuje plików Deadlocka.",
        "Nie wysyła do gry żadnych klawiszy ani kliknięć; nakładka przepuszcza mysz do gry.",
        "Robi zrzuty ekranu (tym samym mechanizmem co OBS czy Discord) i rozpoznaje na nich obraz.",
        "Z internetu pobiera tylko publiczne statystyki przedmiotów z deadlock-api.com.",
        "Każda aktualizacja jest podpisana; aplikacja odrzuca pliki bez ważnego podpisu.",
    ],
    "safe_note": (
        "To nieoficjalne narzędzie fanów. Valve nie publikuje listy dozwolonych programów zewnętrznych, "
        "więc korzystasz z niego na własną odpowiedzialność."
    ),
    "faq_h": "Najczęstsze pytania",
    "faq": [
        ("Czy za Deadlock Assist można dostać bana?",
         "Aplikacja nie dotyka procesu gry: nie czyta pamięci, nie wstrzykuje kodu i nie symuluje klawiszy, "
         "tylko analizuje zrzuty ekranu. Valve nie publikuje jednak listy dozwolonych narzędzi, więc nikt "
         "nie może dać gwarancji. Korzystasz z niej na własną odpowiedzialność."),
        ("Czy Deadlock Assist jest darmowy?",
         "Tak, w całości i bez reklam. Jeśli chcesz wesprzeć rozwój, możesz postawić autorowi kawę na Ko-fi."),
        ("Jakie są wymagania?",
         "Windows 10 lub 11 (64-bit) i Deadlock uruchomiony w trybie okna bez ramek (Borderless). "
         "W trybie pełnoekranowym system nie pokaże nakładki nad grą."),
        ("Czy działa w każdej rozdzielczości?",
         "Pozycje elementów są zmierzone na ekranie 1920×1200 i skalowane do wysokości ekranu. Jeśli coś "
         "nie jest rozpoznawane w Twojej rozdzielczości, zgłoś błąd ze zrzutem ekranu."),
        ("Skąd aplikacja wie, co kupić?",
         "Łączy statystyki przedmiotów z publicznego deadlock-api.com (co wygrywa na danym bohaterze i przeciw "
         "danym wrogom) z tym, co sama odczytuje z ekranu: składem wroga, zakupami przeciwników i Twoimi duszami."),
        ("Czy jest wersja po angielsku?",
         "Interfejs jest na razie po polsku. Dane gry, czyli nazwy i opisy bohaterów i przedmiotów, "
         "są dostępne po polsku i angielsku."),
        ("Jak zgłosić pomysł albo błąd?",
         "Kliknij „Zaproponuj zmianę” w aplikacji albo użyj formularzy na GitHubie. Każdy pomysł trafia na "
         "listę do wdrożenia."),
    ],
    "final_h": "Zagraj następny mecz z doradcą",
    "final_lead": "Instalacja zajmuje minutę. Aplikacja jest i zostanie darmowa.",
    "kofi": "Wesprzyj na Ko-fi",
    "links": [(IDEA, "Zaproponuj pomysł"), (BUG, "Zgłoś błąd"), (REPO + "/blob/main/SECURITY.md", "Bezpieczeństwo"),
              (REPO + "/releases", "Wszystkie wersje")],
    "footer": (
        "Deadlock jest znakiem towarowym Valve Corporation. Deadlock Assist to nieoficjalny projekt fanów, "
        "niezwiązany z Valve ani przez nią wspierany. Dane o przedmiotach pochodzą z deadlock-api.com."
    ),
    "skip": "Przejdź do treści",
    "smartscreen": (
        "Windows może pokazać „System Windows ochronił ten komputer”: kliknij „Więcej informacji”, "
        "a potem „Uruchom mimo to”."
    ),
}

EN = {
    "lang": "en",
    "path": "en/",
    "locale": "en_US",
    "title": "Deadlock Assist – free Deadlock overlay for counter items, builds and camp timers",
    "description": (
        "Free Deadlock helper for Windows: counter items for the enemy team, what to buy next, jungle camp "
        "and Mid Boss timers, and match history with farm analysis. No Overwolf, no ads, no memory reading."
    ),
    "nav": [("#features", "Features"), ("#safety", "Safety"), ("#faq", "FAQ")],
    "switch": ("../", "Polski"),
    "eyebrow": "Free Deadlock overlay · Windows 10/11",
    "h1": "Deadlock counter items, builds and timers, live in your match",
    "lead": (
        "Deadlock Assist recognises the enemy heroes and what they buy, then tells you what to buy to counter "
        "them. It tracks jungle camps and the Mid Boss, and after the match it shows you what to improve. "
        "Free, and no Overwolf."
    ),
    "cta": "Download for Windows",
    "cta_note": ".exe installer · updates itself",
    "cta2": "See features",
    "shot_alt": (
        "Deadlock Assist overlay in game: lane counters, the Buy now panel with the best item against the "
        "enemy, and a clock with jungle camp and Mid Boss timers"
    ),
    "badges": ["Free", "No ads, no account", "No Overwolf", "No memory reading"],
    "features_h": "What Deadlock Assist does",
    "features_lead": (
        "Everything you would normally look up on build and tier list sites between fights is on your screen "
        "the moment you need it."
    ),
    "features": [
        ("counter", "Counter items for the enemy team",
         "Recognises the six enemies from the top bar and suggests the items that work best against them: "
         "Healbane against healing, Silencer against ability heroes, Spirit Resilience against spirit damage. "
         "Each counter shows its price and the reason."),
        ("cart", "“Buy now” and next purchases",
         "An item build from thousands of matches on your hero, adjusted to what you already own and what you "
         "can afford. When you have the souls, it shows the single best purchase, not a list to scroll."),
        ("lane", "Lane counters",
         "Until minute 10 it suggests cheap items against your lane opponents, because that is when the farm "
         "is won or lost."),
        ("eye", "Enemy purchases, live",
         "Hold Tab and it remembers what every enemy has bought. When someone buys Leech or Unstoppable, the "
         "advice changes right away and the overlay warns you."),
        ("clock", "Clock, jungle camp and Mid Boss timers",
         "Spots killed jungle camps on the minimap and counts down their respawn. It also tracks the Mid Boss, "
         "power-ups and the soul urn, with the direction to go."),
        ("chart", "Match history and review",
         "Every match goes to your history: result, teams, purchase order and souls per minute compared with a "
         "typical player. At the end you get a short summary of what to improve."),
        ("book", "Hero and item browser",
         "Browse heroes and items with filters like “what counters healing” or “items with silence”. After "
         "every patch you see what changed for your heroes and items."),
        ("auto", "Runs by itself",
         "A match starts when the game clock shows the first minute, and F10 ends and saves it. The overlay "
         "never captures your mouse, and new versions install in one click."),
    ],
    "how_h": "How it works",
    "how": [
        ("Install", "Download the installer, run it and set Deadlock to borderless window mode."),
        ("Play", "The assistant detects the match start, recognises the heroes and shows counters in the "
                 "overlay. Hold Tab now and then to refresh every player's items."),
        ("Improve", "After the match (F10), check your farm, purchases and the summary of what to do better "
                    "in History."),
    ],
    "gallery_h": "What it looks like",
    "gallery": [
        ("nakladka-tab.png", "Overlay with Tab held: every player's items, counters and timers",
         "With Tab: every player's items and counters to them"),
        ("historia.png", "Match history: results, heroes, opponents and purchase order",
         "History: results, opponents and purchases from every match"),
    ],
    "why_h": "Why Deadlock Assist",
    "why": [
        ("A standalone app, not an Overwolf plugin", "A lightweight program (Tauri) with no account, no ads and "
         "no extra platform running in the background."),
        ("Advice during the match, not in a browser", "Build sites and tier lists are great before a match. "
         "Deadlock Assist reacts to what is happening now: who is on the enemy team and what they just bought."),
        ("Your data stays with you", "Match history is stored locally. Screenshots are only used for reading "
         "and are deleted once the match is saved."),
        ("Interface in Polish", "The interface and advice are in Polish for now; game data (hero and item names "
         "and descriptions) is available in English too."),
    ],
    "safe_h": "Safety",
    "safe_lead": "Deadlock Assist works like screen recording software, not like a cheat.",
    "safe": [
        "It does not read game memory, inject code or modify Deadlock's files.",
        "It sends no keys or clicks to the game; the overlay lets your mouse through.",
        "It takes screenshots (the same way OBS or Discord do) and recognises what is on them.",
        "The only thing it downloads is public item statistics from deadlock-api.com.",
        "Every update is signed, and the app rejects files without a valid signature.",
    ],
    "safe_note": (
        "This is an unofficial fan tool. Valve does not publish a list of allowed third-party programs, so you "
        "use it at your own risk."
    ),
    "faq_h": "Frequently asked questions",
    "faq": [
        ("Can I get banned for using Deadlock Assist?",
         "The app does not touch the game process: it does not read memory, inject code or simulate keys; it "
         "only analyses screenshots. Valve does not publish a list of allowed tools, though, so nobody can "
         "guarantee anything. You use it at your own risk."),
        ("Is Deadlock Assist free?",
         "Yes, completely, with no ads. If you want to support development, you can buy the author a coffee on Ko-fi."),
        ("What are the requirements?",
         "Windows 10 or 11 (64-bit), with Deadlock in borderless window mode. In exclusive fullscreen Windows "
         "cannot show an overlay on top of the game."),
        ("Does it work at any resolution?",
         "Element positions were measured at 1920×1200 and are scaled to your screen height. If something is not "
         "recognised at your resolution, report a bug with a screenshot."),
        ("How does it know what to buy?",
         "It combines item statistics from the public deadlock-api.com (what wins on your hero and against "
         "specific enemies) with what it reads from your screen: the enemy team, their purchases and your souls."),
        ("Is the app available in English?",
         "The interface is in Polish for now. Game data, meaning hero and item names and descriptions, is "
         "available in English and Polish."),
        ("How do I suggest an idea or report a bug?",
         "Click “Zaproponuj zmianę” (Suggest a change) in the app or use the forms on GitHub. Every idea goes on "
         "the list to build."),
    ],
    "final_h": "Play your next match with an advisor",
    "final_lead": "Installing takes a minute. The app is free and will stay free.",
    "kofi": "Support on Ko-fi",
    "links": [(IDEA, "Suggest an idea"), (BUG, "Report a bug"), (REPO + "/blob/main/SECURITY.md", "Security"),
              (REPO + "/releases", "All versions")],
    "footer": (
        "Deadlock is a trademark of Valve Corporation. Deadlock Assist is an unofficial fan project, not "
        "affiliated with or endorsed by Valve. Item data comes from deadlock-api.com."
    ),
    "skip": "Skip to content",
    "smartscreen": (
        "Windows may show “Windows protected your PC”: click “More info”, then “Run anyway”."
    ),
}

CSS = Path(__file__).with_name("style.css").read_text()


def e(s):
    return html.escape(s, quote=True)


def page(t):
    prefix = "" if t["path"] == "" else "../"
    url = BASE + t["path"]
    feat_id = "funkcje" if t["lang"] == "pl" else "features"
    safe_id = "bezpieczenstwo" if t["lang"] == "pl" else "safety"
    ld_app = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Deadlock Assist",
        "description": t["description"],
        "url": url,
        "applicationCategory": "GameApplication",
        "operatingSystem": "Windows 10, Windows 11",
        "inLanguage": t["lang"],
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "downloadUrl": DOWNLOAD,
        "screenshot": BASE + "nakladka.png",
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
    nav = "".join(f'<a href="{h}">{e(l)}</a>' for h, l in t["nav"])
    badges = "".join(f"<li>{e(b)}</li>" for b in t["badges"])
    feats = "".join(
        f'<article class="card">{icon(i)}<h3>{e(h)}</h3><p>{e(p)}</p></article>' for i, h, p in t["features"]
    )
    how = "".join(f"<li><h3>{e(h)}</h3><p>{e(p)}</p></li>" for h, p in t["how"])
    gallery = "".join(
        f'<figure><img src="{prefix}{f}" alt="{e(a)}" width="842" height="527" loading="lazy" decoding="async">'
        f"<figcaption>{e(c)}</figcaption></figure>"
        for f, a, c in t["gallery"]
    )
    why = "".join(f"<li><h3>{e(h)}</h3><p>{e(p)}</p></li>" for h, p in t["why"])
    safe = "".join(f"<li>{e(s)}</li>" for s in t["safe"])
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in t["faq"])
    links = "".join(f'<a href="{e(h)}" rel="noopener">{e(l)}</a>' for h, l in t["links"])
    cta = (
        f'<a class="btn" href="{DOWNLOAD}" rel="noopener">{icon("windows")}<span>{e(t["cta"])}</span></a>'
    )
    return f"""<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(t['title'])}</title>
<meta name="description" content="{e(t['description'])}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="pl" href="{BASE}">
<link rel="alternate" hreflang="en" href="{BASE}en/">
<link rel="alternate" hreflang="x-default" href="{BASE}en/">
<meta name="theme-color" content="#0e1014">
<link rel="icon" type="image/png" href="{prefix}icon.png">
<link rel="apple-touch-icon" href="{prefix}icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Deadlock Assist">
<meta property="og:title" content="{e(t['title'])}">
<meta property="og:description" content="{e(t['description'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}nakladka.png">
<meta property="og:image:alt" content="{e(t['shot_alt'])}">
<meta property="og:locale" content="{t['locale']}">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps(ld_app, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(ld_faq, ensure_ascii=False)}</script>
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">{e(t['skip'])}</a>
<header class="top wrap">
  <a class="logo" href="./"><img src="{prefix}icon.png" alt="" width="32" height="32">DEADLOCK <span>ASSIST</span></a>
  <nav aria-label="menu">{nav}<a class="lang" href="{t['switch'][0]}" hreflang="{'en' if t['lang'] == 'pl' else 'pl'}">{e(t['switch'][1])}</a></nav>
</header>
<main id="main">
<section class="hero wrap">
  <div class="hero-text">
    <p class="eyebrow">{e(t['eyebrow'])}</p>
    <h1>{e(t['h1'])}</h1>
    <p class="lead">{e(t['lead'])}</p>
    <div class="actions">{cta}<a class="btn ghost" href="#{feat_id}">{e(t['cta2'])}</a></div>
    <p class="note">{e(t['cta_note'])}</p>
    <ul class="badges">{badges}</ul>
  </div>
  <figure class="hero-shot"><img src="{prefix}nakladka.png" alt="{e(t['shot_alt'])}" width="842" height="527" fetchpriority="high"></figure>
</section>

<section id="{feat_id}" class="wrap">
  <h2>{e(t['features_h'])}</h2>
  <p class="section-lead">{e(t['features_lead'])}</p>
  <div class="grid">{feats}</div>
</section>

<section class="wrap">
  <h2>{e(t['how_h'])}</h2>
  <ol class="steps">{how}</ol>
</section>

<section class="wrap">
  <h2>{e(t['gallery_h'])}</h2>
  <div class="gallery">{gallery}</div>
</section>

<section class="wrap">
  <h2>{e(t['why_h'])}</h2>
  <ul class="why">{why}</ul>
</section>

<section id="{safe_id}" class="wrap safe">
  {icon('lock', 'ico big')}
  <div>
    <h2>{e(t['safe_h'])}</h2>
    <p class="section-lead">{e(t['safe_lead'])}</p>
    <ul class="checks">{safe}</ul>
    <p class="note">{e(t['safe_note'])}</p>
  </div>
</section>

<section id="faq" class="wrap">
  <h2>{e(t['faq_h'])}</h2>
  <div class="faq">{faq}</div>
</section>

<section class="wrap final">
  <h2>{e(t['final_h'])}</h2>
  <p class="section-lead">{e(t['final_lead'])}</p>
  <div class="actions center">{cta}<a class="btn gold" href="{KOFI}" rel="noopener">{icon('heart')}<span>{e(t['kofi'])}</span></a></div>
  <p class="note">{e(t['smartscreen'])}</p>
</section>
</main>
<footer class="wrap foot">
  <nav aria-label="links">{links}</nav>
  <p>{e(t['footer'])}</p>
</footer>
</body>
</html>
"""


def main():
    out = Path(sys.argv[1])
    (out / "en").mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page(PL))
    (out / "en" / "index.html").write_text(page(EN))
    alt = (
        f'    <xhtml:link rel="alternate" hreflang="pl" href="{BASE}"/>\n'
        f'    <xhtml:link rel="alternate" hreflang="en" href="{BASE}en/"/>\n'
    )
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        f"  <url>\n    <loc>{BASE}</loc>\n{alt}  </url>\n"
        f"  <url>\n    <loc>{BASE}en/</loc>\n{alt}  </url>\n"
        "</urlset>\n"
    )
    (out / ".nojekyll").write_text("")


main()
