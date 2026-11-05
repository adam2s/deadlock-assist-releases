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
        "timery obozów i Mid Bossa oraz analiza farmy po meczu. Bez Overwolf i bez reklam."
    ),
    "nav": [("#funkcje", "Funkcje"), ("#skutecznosc", "Skuteczność"), ("#bezpieczenstwo", "Bezpieczeństwo"),
            ("#faq", "FAQ")],
    "switch": ("en/", "English"),
    "eyebrow": "Darmowa nakładka do Deadlocka · Windows 10/11",
    "h1": "Kontry, buildy i timery w Deadlocku, w trakcie meczu",
    "lead": "Widzi skład wroga i jego zakupy, a potem mówi, co kupić. Za darmo, bez Overwolf.",
    "cta": "Pobierz dla Windows",
    "cta_note": "Instalator .exe · aktualizuje się sam",
    "cta2": "Zobacz funkcje",
    "shot_alt": (
        "Nakładka Deadlock Assist nad grą: kontry na linii, panel Kup teraz z najlepszym przedmiotem "
        "na wroga oraz zegar z timerami obozów i Mid Bossa"
    ),
    "badges": ["Za darmo", "Bez reklam i konta", "Bez Overwolf", "Nie czyta pamięci gry", "PL / EN"],
    "features_h": "Funkcje",
    "features_lead": "",
    "features": [
        ("counter", "Kontry na skład wroga", "Healbane na leczenie, Silencer na umiejętności, z ceną i powodem."),
        ("cart", "„Kup teraz”", "Jeden najlepszy zakup na teraz, dopasowany do Twojego buildu i dusz."),
        ("eye", "Zakupy wrogów", "Po Tab widzi, co kupił wróg, i od razu zmienia rady."),
        ("lane", "Kontry na linii", "Do 10. minuty tanie przedmioty na rywali z Twojej linii."),
        ("clock", "Timery", "Obozy w dżungli, Mid Boss, wzmocnienia i urna, z kierunkiem."),
        ("chart", "Analiza meczu", "Farma minuta po minucie i co poprawić w kolejnym meczu."),
    ],
    "proof_h": "Czy doradca naprawdę pomaga?",
    "proof_lead": "Test na 2020 meczach z wysokich rang (Emissary+), 33 811 zakupów.",
    "proof": [
        ("81%", 81, 62, "trafnych kontr", "Podpowiedzi, które przeciw temu składowi wygrywają częściej niż typowy przedmiot.",
         "wcześniej 62%"),
        ("29%", 29, 25, "zgodności z topem", "Zakupów graczy z wysokich rang w pierwszej piątce doradcy.",
         "wcześniej 25%"),
        ("+3,2 pkt", None, None, "więcej wygranych", "Gracze z tą samą farmą, którzy kupili coś z pierwszej piątki.",
         "przy równej farmie"),
    ],
    "proof_note": "Wyniki z cudzych meczów, nie gwarancja wygranej. Tryb „Zrównoważony”, wersja 1.2.6.",
    "how_h": "Jak zacząć",
    "how": [
        ("Zainstaluj", "Deadlock w trybie okna bez ramek (Borderless)."),
        ("Graj", "Mecz wykrywa się sam. Co jakiś czas przytrzymaj Tab."),
        ("Popraw się", "Po meczu (F10) sprawdź podsumowanie w Historii."),
    ],
    "gallery_h": "Jak to wygląda",
    "gallery": [
        ("nakladka-tab.png", "Nakładka po wciśnięciu Tab: przedmioty wszystkich graczy, kontry i timery",
         "Tab: zakupy graczy i kontry"),
        ("historia.png", "Historia meczów: wyniki, bohaterowie, przeciwnicy i kolejność zakupów",
         "Historia meczów"),
    ],
    "safe_h": "Bezpieczeństwo",
    "safe_lead": "Działa jak nagrywanie ekranu, nie jak cheat.",
    "safe": [
        "Nie czyta pamięci gry i nie zmienia jej plików.",
        "Nie wysyła klawiszy ani kliknięć do gry.",
        "Pobiera tylko publiczne statystyki z deadlock-api.com.",
        "Każda aktualizacja jest podpisana.",
    ],
    "safe_note": "Nieoficjalne narzędzie fanów. Valve nie publikuje listy dozwolonych programów.",
    "faq_h": "FAQ",
    "faq": [
        ("Czy można dostać bana?",
         "Aplikacja nie dotyka procesu gry, tylko analizuje zrzuty ekranu. Valve nie daje jednak gwarancji, "
         "więc korzystasz na własną odpowiedzialność."),
        ("Czy jest darmowy?", "Tak, w całości i bez reklam. Rozwój możesz wesprzeć na Ko-fi."),
        ("Jakie są wymagania?", "Windows 10 lub 11 (64-bit) i Deadlock w trybie okna bez ramek (Borderless)."),
        ("Skąd wie, co kupić?",
         "Ze statystyk deadlock-api.com i z tego, co widzi na ekranie: składu wroga, jego zakupów i Twoich dusz."),
        ("Czy jest po angielsku?", "Tak. Język przełączasz w nagłówku aplikacji (PL / EN)."),
    ],
    "final_h": "Zagraj następny mecz z doradcą",
    "final_lead": "Instalacja zajmuje minutę.",
    "kofi": "Wesprzyj na Ko-fi",
    "links": [(IDEA, "Zaproponuj pomysł"), (BUG, "Zgłoś błąd"), (REPO + "/blob/main/SECURITY.md", "Bezpieczeństwo"),
              (REPO + "/releases", "Wszystkie wersje")],
    "footer": (
        "Deadlock jest znakiem towarowym Valve Corporation. Deadlock Assist to nieoficjalny projekt fanów, "
        "niezwiązany z Valve. Dane o przedmiotach: deadlock-api.com."
    ),
    "skip": "Przejdź do treści",
    "smartscreen": "Ostrzeżenie Windows? Kliknij „Więcej informacji” → „Uruchom mimo to”.",
}

EN = {
    "lang": "en",
    "path": "en/",
    "locale": "en_US",
    "title": "Deadlock Assist – free Deadlock overlay for counter items, builds and camp timers",
    "description": (
        "Free Deadlock helper for Windows: counter items for the enemy team, what to buy next, jungle camp "
        "and Mid Boss timers, and post-match farm review. No Overwolf, no ads."
    ),
    "nav": [("#features", "Features"), ("#results", "Results"), ("#safety", "Safety"), ("#faq", "FAQ")],
    "switch": ("../", "Polski"),
    "eyebrow": "Free Deadlock overlay · Windows 10/11",
    "h1": "Deadlock counter items, builds and timers, live in your match",
    "lead": "It sees the enemy team and what they buy, then tells you what to buy. Free, no Overwolf.",
    "cta": "Download for Windows",
    "cta_note": ".exe installer · updates itself",
    "cta2": "See features",
    "shot_alt": (
        "Deadlock Assist overlay in game: lane counters, the Buy now panel with the best item against the "
        "enemy, and a clock with jungle camp and Mid Boss timers"
    ),
    "badges": ["Free", "No ads, no account", "No Overwolf", "No memory reading", "EN / PL"],
    "features_h": "Features",
    "features_lead": "",
    "features": [
        ("counter", "Counters for the enemy team", "Healbane for healing, Silencer for abilities, with price and reason."),
        ("cart", "“Buy now”", "The single best purchase right now, fitted to your build and souls."),
        ("eye", "Enemy purchases", "Hold Tab and it sees what enemies bought, then updates the advice."),
        ("lane", "Lane counters", "Until minute 10, cheap items against your lane opponents."),
        ("clock", "Timers", "Jungle camps, Mid Boss, power-ups and the urn, with directions."),
        ("chart", "Match review", "Farm minute by minute and what to improve next match."),
    ],
    "proof_h": "Does the advisor actually help?",
    "proof_lead": "Tested on 2,020 high-rank matches (Emissary+), 33,811 purchases.",
    "proof": [
        ("81%", 81, 62, "good counters", "Suggestions that win more often against that enemy team than a typical item.",
         "before: 62%"),
        ("29%", 29, 25, "match top players", "High-rank purchases that were in the advisor's top 5.",
         "before: 25%"),
        ("+3.2 pts", None, None, "more wins", "Players with equal farm who bought an item from the top 5.",
         "at equal farm"),
    ],
    "proof_note": "Results from other players' matches, not a guarantee. “Balanced” mode, version 1.2.6.",
    "how_h": "Get started",
    "how": [
        ("Install", "Set Deadlock to borderless window mode."),
        ("Play", "Matches are detected by themselves. Hold Tab now and then."),
        ("Improve", "After the match (F10), check the summary in History."),
    ],
    "gallery_h": "What it looks like",
    "gallery": [
        ("nakladka-tab.png", "Overlay with Tab held: every player's items, counters and timers",
         "Tab: player items and counters"),
        ("historia.png", "Match history: results, heroes, opponents and purchase order",
         "Match history"),
    ],
    "safe_h": "Safety",
    "safe_lead": "Works like screen recording, not like a cheat.",
    "safe": [
        "Does not read game memory or change game files.",
        "Sends no keys or clicks to the game.",
        "Downloads only public stats from deadlock-api.com.",
        "Every update is signed.",
    ],
    "safe_note": "Unofficial fan tool. Valve does not publish a list of allowed programs.",
    "faq_h": "FAQ",
    "faq": [
        ("Can I get banned?",
         "The app does not touch the game process; it only analyses screenshots. Valve gives no guarantees, "
         "so you use it at your own risk."),
        ("Is it free?", "Yes, completely, with no ads. You can support development on Ko-fi."),
        ("What are the requirements?", "Windows 10 or 11 (64-bit), with Deadlock in borderless window mode."),
        ("How does it know what to buy?",
         "From deadlock-api.com stats and what it sees on screen: the enemy team, their purchases and your souls."),
        ("Is it in English?", "Yes. Switch the language in the app header (PL / EN)."),
    ],
    "final_h": "Play your next match with an advisor",
    "final_lead": "Installing takes a minute.",
    "kofi": "Support on Ko-fi",
    "links": [(IDEA, "Suggest an idea"), (BUG, "Report a bug"), (REPO + "/blob/main/SECURITY.md", "Security"),
              (REPO + "/releases", "All versions")],
    "footer": (
        "Deadlock is a trademark of Valve Corporation. Deadlock Assist is an unofficial fan project, not "
        "affiliated with Valve. Item data: deadlock-api.com."
    ),
    "skip": "Skip to content",
    "smartscreen": "Windows warning? Click “More info” → “Run anyway”.",
}

CSS = Path(__file__).with_name("style.css").read_text()


def e(s):
    return html.escape(s, quote=True)


def page(t):
    prefix = "" if t["path"] == "" else "../"
    url = BASE + t["path"]
    feat_id = "funkcje" if t["lang"] == "pl" else "features"
    safe_id = "bezpieczenstwo" if t["lang"] == "pl" else "safety"
    proof_id = "skutecznosc" if t["lang"] == "pl" else "results"
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
    def stat(n, now, before, lab, text, was):
        meter = (
            f'<div class="meter" aria-hidden="true"><i style="width:{now}%"></i><b style="left:{before}%"></b></div>'
            if now is not None
            else ""
        )
        return (
            f'<li class="stat"><p class="stat-num">{e(n)}</p><p class="stat-label">{e(lab)}</p>{meter}'
            f'<p>{e(text)}</p><p class="stat-before">{e(was)}</p></li>'
        )

    proof = "".join(stat(*p) for p in t["proof"])
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
  <div class="grid">{feats}</div>
</section>

<section id="{proof_id}" class="wrap">
  <h2>{e(t['proof_h'])}</h2>
  <p class="section-lead">{e(t['proof_lead'])}</p>
  <ul class="stats">{proof}</ul>
  <p class="note">{e(t['proof_note'])}</p>
</section>

<section class="wrap">
  <h2>{e(t['how_h'])}</h2>
  <ol class="steps">{how}</ol>
</section>

<section class="wrap">
  <h2>{e(t['gallery_h'])}</h2>
  <div class="gallery">{gallery}</div>
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
