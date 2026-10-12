# -*- coding: utf-8 -*-
"""Builds the S99 Marketing static website.

    python3 build.py            -> dist/     (upload this folder to Cloudflare Pages)
    python3 build.py --preview  -> preview/  (same site, links point at index.html files)

Change SITE_URL once the domain is bought.
"""
import html
import json
import os
import shutil
import sys
from datetime import date

from content import COMPANY, UI, HOME, PACKAGES, SERVICES

SITE_URL = "https://ahmedphotographey-svg.github.io/s99-marketing-agency"   # <-- change to the real domain when it is ready
BASE_PATH = "/" + SITE_URL.split("://", 1)[1].partition("/")[2].strip("/") + "/" if "/" in SITE_URL.split("://", 1)[1] else "/"
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
PREVIEW = "--preview" in sys.argv
OUT = os.path.join(HERE, "preview" if PREVIEW else "dist")


def e(s):
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------- paths
def page_file(lang, kind, slug=None):
    base = "" if lang == "en" else "ar/"
    if kind == "home":
        return base + "index.html"
    return base + "services/%s/index.html" % slug


def page_url(lang, kind, slug=None):
    f = page_file(lang, kind, slug)
    return SITE_URL + "/" + f[: -len("index.html")]


def rel(from_file, to_file):
    """Relative link from one generated file to another."""
    from_dir = os.path.dirname(from_file)
    r = os.path.relpath(to_file, from_dir or ".").replace(os.sep, "/")
    if not PREVIEW and r.endswith("index.html"):
        r = r[: -len("index.html")] or "./"
    return r


def root_of(from_file):
    d = os.path.dirname(from_file)
    return "" if not d else "../" * (d.count("/") + 1)


# ---------------------------------------------------------------- icons
ICONS = {
    "phone": '<rect x="5" y="2" width="14" height="20" rx="3"/><path d="M9 7h6M9 11h6M9 15h3"/>',
    "camera": '<path d="M3 7h12v10H3z"/><path d="M15 10l6-3v10l-6-3"/>',
    "people": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M18.5 14.5c1.9.9 3 2.9 3 5.5"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/><path d="M12 13.5l1 2 2.2.3-1.6 1.5.4 2.2-2-1.1-2 1.1.4-2.2-1.6-1.5 2.2-.3z"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "call": '<path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2z"/>',
    "wa": '<path d="M4 20l1.3-3.9A8.5 8.5 0 1 1 8 19z"/><path d="M9 9.5c.3 2 2.5 4.3 5.5 5l1-1.5-2-1-1 .8c-1-.4-2-1.4-2.3-2.3l.8-1-1-2z"/>',
    "eye": '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "heart": '<path d="M12 20s-7.5-4.6-9.3-9.2C1.6 7.9 3.4 4.5 6.8 4.5c2.1 0 3.5 1.2 5.2 3 1.7-1.8 3.1-3 5.2-3 3.4 0 5.2 3.4 4.1 6.3C19.5 15.4 12 20 12 20z"/>',
    "share": '<path d="M14 5l7 7-7 7"/><path d="M21 12H10c-4 0-7 3-7 7"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "close": '<path d="M6 6l12 12M18 6L6 18"/>',
    "bulb": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
    "bolt": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    "team": '<circle cx="12" cy="7" r="3"/><path d="M6 21v-1a6 6 0 0 1 12 0v1"/><circle cx="4.5" cy="10" r="2"/><circle cx="19.5" cy="10" r="2"/>',
    "spark": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/>',
    "film": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 4v16M17 4v16M3 9h4M3 15h4M17 9h4M17 15h4"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
}


def icon(name, size=24, color="#4A9BD4", sw=1.6, cls=""):
    c = (' class="%s"' % cls) if cls else ""
    return ('<svg%s width="%d" height="%d" viewBox="0 0 24 24" fill="none" stroke="%s" stroke-width="%s" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>') % (c, size, size, color, sw, ICONS[name])


PLAY_ICON = '<svg width="18" height="18" viewBox="0 0 24 24" fill="#FFFFFF" aria-hidden="true"><path d="M7 4.5v15l13-7.5z"/></svg>'
WHY_ICONS = ["bulb", "bolt", "team", "spark", "film", "chart"]
RESULT_ICONS = ["eye", "heart", "share"]


# ---------------------------------------------------------------- shared chrome
def head(lang, f, title, desc, alt_en, alt_ar, extra_ld):
    root = root_of(f)
    canonical = alt_en if lang == "en" else alt_ar
    ld = "".join('<script type="application/ld+json">%s</script>\n' % json.dumps(x, ensure_ascii=False) for x in extra_ld)
    return f"""<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canonical)}">
<link rel="alternate" hreflang="en" href="{e(alt_en)}">
<link rel="alternate" hreflang="ar" href="{e(alt_ar)}">
<link rel="alternate" hreflang="x-default" href="{e(alt_en)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="S99 Marketing">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{SITE_URL}/assets/img/og-image.jpg">
<meta property="og:locale" content="{'ar_EG' if lang == 'ar' else 'en_US'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#000000">
<link rel="icon" href="{root}assets/img/favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="{root}assets/img/favicon-48.png">
<link rel="apple-touch-icon" href="{root}assets/img/apple-touch-icon.png">
<link rel="preload" href="{root}assets/fonts/{'cairo-arabic' if lang == 'ar' else 'montserrat-latin'}-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{root}assets/css/site.css">
{ld}"""


def wrap_doc(lang, f, head_html, body_html, fragment=False):
    d = "rtl" if lang == "ar" else "ltr"
    if fragment:  # artifact preview main page: the host adds doctype/html/head/body
        return head_html + body_html
    return f"""<!doctype html>
<html lang="{lang}" dir="{d}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{head_html}</head>
<body>
{body_html}</body>
</html>
"""


def site_open(lang, f):
    u = UI[lang]
    root = root_of(f)
    return (f'<div id="site" data-lang="{lang}" data-root="{root}" data-wa="{COMPANY["whatsapp"]}" '
            f'data-t-missing="{e(u["video_missing"])}" data-t-reel="{"ريل" if lang == "ar" else "Reel"}" '
            f'data-t-play="{e(u["play_reel"])}" data-t-featured="{e(u["featured"])}" data-t-watch="{e(u["watch_film"])}" '
            f'data-t-all-clients="{e(u["all_clients"])}" data-t-all="{e(u["all"])}">\n'
            f'<a class="skip" href="#main">{e(u["skip"])}</a>\n')


def header(lang, f, other_file, current=None):
    u = UI[lang]
    home = page_file(lang, "home")
    root = root_of(f)
    on_home = f == home
    links = []
    for key, label in u["nav"]:
        href = ("#" + key) if on_home else (rel(f, home) + "#" + key)
        cur = ' aria-current="page"' if current == key else ""
        links.append(f'<a href="{href}"{cur}>{e(label)}</a>')
    contact = "#contact" if on_home else rel(f, home) + "#contact"
    other_lang = "ar" if lang == "en" else "en"
    return f"""<header class="site-header">
<nav class="wrap nav" aria-label="{'القائمة الرئيسية' if lang == 'ar' else 'Main'}">
<a class="brand" href="{rel(f, home)}" aria-label="S99 Marketing"><img src="{root}assets/img/logo-nav.png" alt="S99 Marketing" width="90" height="42"></a>
<div class="nav-links" id="nav-links">{''.join(links)}</div>
<div class="nav-actions">
<a class="lang" href="{rel(f, other_file)}" hreflang="{other_lang}" lang="{other_lang}" title="{e(u['switch_title'])}">{e(u['switch_label'])}</a>
<a class="btn btn--primary btn--sm" href="{contact}">{e(u['book'])}</a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav-links" aria-label="{e(u['menu'])}">{icon('menu', 22, '#FFFFFF', 1.8)}</button>
</div>
</nav>
</header>
"""


def social_links():
    names = [("instagram", "Instagram"), ("facebook", "Facebook"), ("tiktok", "TikTok")]
    return "".join(f'<a href="{COMPANY[k]}" rel="noopener" target="_blank">{n}</a>' for k, n in names if COMPANY[k])


def footer(lang, f):
    u = UI[lang]
    root = root_of(f)
    home = page_file(lang, "home")
    svc_links = "".join(f'<a href="{rel(f, page_file(lang, "svc", s["slug"]))}">{e(s[lang]["name"])}</a>' for s in SERVICES)
    co_links = "".join(f'<a href="{rel(f, home)}#{k}">{e(lbl)}</a>' for k, lbl in u["nav"])
    return f"""<footer class="site-footer">
<div class="wrap">
<div class="footer-top">
<div class="footer-brand"><img src="{root}assets/img/logo-full.png" alt="S99 Marketing — Strategy. Content. Growth." width="180" height="102" loading="lazy"><p>{e(u['footer_tag'])}</p></div>
<div class="footer-cols">
<nav aria-label="{e(u['footer_services'])}"><b>{e(u['footer_services'])}</b>{svc_links}</nav>
<nav aria-label="{e(u['footer_company'])}"><b>{e(u['footer_company'])}</b>{co_links}</nav>
<nav aria-label="Social"><b>{e(u['footer_follow'])}</b>{social_links()}</nav>
</div>
</div>
<div class="footer-bottom"><span>{e(u['rights'])}</span><span>{e(u['address'])} · <span dir="ltr">{COMPANY['phone_display']}</span></span></div>
</div>
</footer>
<a class="wa-float" href="https://wa.me/{COMPANY['whatsapp']}" target="_blank" rel="noopener" aria-label="{e(u['whatsapp_us'])}">{icon('wa', 26, '#000000', 1.8)}</a>
<div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Video" hidden>
<button class="lb-close" type="button" aria-label="{e(u['close_video'])}">{icon('close', 20, '#FFFFFF', 2)}</button>
<div class="lb-body"><div class="lb-frame"></div><div class="lb-caption"><b></b><span></span><a class="lb-yt" href="#" target="_blank" rel="noopener" hidden>{"شاهد على YouTube" if lang == "ar" else "Watch on YouTube"}</a></div></div>
</div>
</div>
<script src="{root}assets/js/site.js" defer></script>
"""


def business_ld():
    return {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "@id": SITE_URL + "/#business",
        "name": "S99 Marketing Agency",
        "alternateName": "S99 Marketing",
        "description": "Creative marketing and media production agency in Egypt and Saudi Arabia.",
        "url": SITE_URL + "/",
        "logo": SITE_URL + "/assets/img/icon-512.png",
        "image": SITE_URL + "/assets/img/og-image.jpg",
        "telephone": COMPANY["phone_intl"],
        "email": COMPANY["email"],
        "foundingDate": "2024",
        "founder": {"@type": "Person", "name": "Ahmed Saleh"},
        "address": {"@type": "PostalAddress", "streetAddress": "Arab League Street, Agouza", "addressLocality": "Giza", "addressRegion": "Giza", "addressCountry": "EG"},
        "areaServed": [{"@type": "Country", "name": "Egypt"}, {"@type": "Country", "name": "Saudi Arabia"}],
        "openingHours": "Su-Th 12:00-20:00",
        "sameAs": [COMPANY[k] for k in ("instagram", "facebook", "tiktok") if COMPANY[k]],
        "knowsLanguage": ["ar", "en"],
    }


# ---------------------------------------------------------------- home page
def build_home(lang):
    h = HOME[lang]
    u = UI[lang]
    f = page_file(lang, "home")
    other = page_file("ar" if lang == "en" else "en", "home")
    root = root_of(f)
    fm = h["form"]

    strip = "".join(f"<li>{e(x)}</li>" for x in h["strip"])
    stats = "".join(f'<div class="stat"><span class="num" dir="ltr">{e(n)}</span><span class="label-up">{e(l)}</span></div>' for n, l in h["stats"])
    cards = ""
    for i, s in enumerate(SERVICES, 1):
        c = s[lang]
        cards += (f'<a class="svc-card" href="{rel(f, page_file(lang, "svc", s["slug"]))}">'
                  f'<span class="top">{icon(s["icon"], 40, "#4A9BD4", 1.5)}<span class="outline-num" aria-hidden="true">0{i}</span></span>'
                  f'<h3 class="h3">{e(c["name"])}</h3><p>{e(c["card"])}</p>'
                  f'<span class="more">{e(u["explore"])} <span class="flip" aria-hidden="true">→</span></span></a>')
    extras = "".join(f'<span class="chip">{e(x)}</span>' for x in h["extras"])
    why = "".join(f'<div class="why-item"><span class="icon-badge">{icon(WHY_ICONS[i], 22)}</span><h3 class="h3">{e(t)}</h3><p>{e(d)}</p></div>' for i, (t, d) in enumerate(h["why"]))
    markets = "".join(f'<div class="market"><h3>{icon("pin", 28)}{e(t)}</h3><p>{e(d)}</p></div>' for t, d in h["markets"])
    network = "".join(f'<span class="chip">{e(x)}</span>' for x in h["network"])
    options = "".join(f"<option>{e(x)}</option>" for x in fm["services"])

    body = site_open(lang, f) + header(lang, f, other) + f"""<main id="main">
<section class="hero" aria-labelledby="hero-h">
<div class="wrap">
<div class="hero-title"><div>
<p class="hero-label">{e(h['hero_label'])}</p>
<h1 id="hero-h">{e(h['hero_h1'])}</h1>
</div></div>
<p class="hero-p">{e(h['hero_p'])}</p>
<div class="hero-actions">
<a class="btn btn--primary" href="#contact">{e(h['hero_cta'])}</a>
<button class="play-btn" type="button" id="showreel-btn"><span class="ring">{PLAY_ICON}</span>{e(h['hero_reel'])}</button>
</div>
</div>
</section>

<section class="strip" aria-label="{'عملاء مختارون' if lang == 'ar' else 'Selected clients'}"><ul class="wrap">{strip}</ul></section>

<section id="about" class="section"><div class="wrap about">
<div class="about-text">
<h2 class="h2">{e(h['about_h'])}</h2>
<p class="lead">{e(h['about_lead'])}</p>
<p class="muted">{e(h['about_p'])}</p>
<div class="founder"><span class="founder-mark" aria-hidden="true">{icon('team', 22)}</span><div><span class="label-up">{e(h['founder_label'])}</span><b>{e(h['founder_name'])}</b></div></div>
</div>
<div class="stats">{stats}</div>
</div></section>

<section id="services" class="section section--alt"><div class="wrap">
<div class="sec-head"><div><p class="eyebrow">{e(h['services_eyebrow'])}</p><h2 class="h2">{e(h['services_h'])}</h2></div><p>{e(h['services_p'])}</p></div>
<div class="cards-3">{cards}</div>
<div class="chips">{extras}</div>
</div></section>

<section id="work" class="section" style="padding-bottom:40px">
<div class="wrap sec-head"><div><p class="eyebrow">{e(h['reels_eyebrow'])}</p><h2 class="h2">{e(h['reels_h'])}</h2></div><p>{e(h['reels_p'])}</p></div>
<div class="rail" id="reels" aria-label="{e(h['reels_h'])}"></div>
<div class="wrap" id="reels-more-wrap" hidden>
<div class="reel-grid" id="reels-more" hidden></div>
<button class="btn btn--ghost" type="button" id="reels-more-btn" aria-expanded="false" aria-controls="reels-more" data-more="{e(h['more_reels'])}" data-less="{e(h['less_reels'])}">{e(h['more_reels'])}</button>
</div>
</section>

<section class="section" style="padding-block:40px 120px" aria-labelledby="films-h"><div class="wrap">
<div class="sec-head"><div><p class="eyebrow">{e(h['films_eyebrow'])}</p><h2 class="h2" id="films-h">{e(h['films_h'])}</h2></div><p>{e(h['films_p'])}</p></div>
<div id="featured" data-bts-h="{e(h['bts_h'])}" data-bts-p="{e(h['bts_p'])}"></div>
<div class="films" id="films"></div>
</div></section>

<section class="section section--alt"><div class="wrap why">
<div class="why-intro"><h2><span>{e(h['why_h1'])}</span><span>{e(h['why_h2'])}</span><span>{e(h['why_h3'])}</span></h2><span class="bar"></span><p>{e(h['why_p'])}</p></div>
<div class="why-grid">{why}</div>
</div></section>

<section id="influencers" class="section" aria-labelledby="inf-h">
<div class="wrap sec-head"><div><p class="eyebrow">{e(h['inf_eyebrow'])}</p><h2 class="h2" id="inf-h">{e(h['inf_h'])}</h2></div><p>{e(h['inf_p'])}</p></div>
<div class="rail" id="inf-rail" aria-label="{e(h['inf_h'])}"></div>
<div class="wrap"><a class="btn btn--ghost" href="{rel(f, page_file(lang, 'svc', 'influencer-marketing'))}">{e(h['inf_all'])} <span class="flip" aria-hidden="true">→</span></a></div>
</section>

<section class="section"><div class="wrap">
<div class="sec-head sec-head--center"><div><p class="eyebrow">{e(h['markets_eyebrow'])}</p><h2 class="h2">{e(h['markets_h'])}</h2></div></div>
<div class="markets">{markets}</div>
<div class="network"><span class="label-up">{e(h['network_label'])}</span>{network}</div>
</div></section>

<section id="clients" class="section section--alt"><div class="wrap">
<div class="sec-head"><div><p class="eyebrow">{e(h['clients_eyebrow'])}</p><h2 class="h2">{e(h['clients_h'])}</h2></div><p>{e(h['clients_p'])}</p></div>
<div class="clients-img"><img src="{root}assets/img/clients-logos.webp" alt="{e(h['clients_alt'])}" width="1600" height="900" loading="lazy"></div>
</div></section>

<section id="contact" class="section"><div class="wrap contact">
<div class="contact-info">
<div style="display:flex;flex-direction:column;gap:14px"><p class="eyebrow">{e(h['contact_eyebrow'])}</p><h2 class="h2">{e(h['contact_h'])}</h2></div>
<div class="contact-lines">
<a class="contact-line" href="tel:{COMPANY['phone_intl']}"><span class="dot">{icon('call', 22, '#000000', 1.8)}</span><span dir="ltr">{COMPANY['phone_display']}</span></a>
<a class="contact-line" href="mailto:{COMPANY['email']}"><span class="dot">{icon('mail', 22, '#000000', 1.8)}</span>{COMPANY['email']}</a>
<span class="contact-line"><span class="dot">{icon('pin', 22, '#000000', 1.8)}</span>{e(u['address'])}</span>
</div>
<a class="btn btn--light" style="align-self:flex-start" href="https://wa.me/{COMPANY['whatsapp']}" target="_blank" rel="noopener">{icon('wa', 20, '#000000', 1.8)}{e(h['contact_wa'])}</a>
</div>
<form class="form" id="contact-form" novalidate data-intro="{e(fm['intro'])}" data-required="{e(fm['required'])}" data-l-name="{e(fm['name'])}" data-l-company="{e(fm['company'])}" data-l-phone="{e(fm['phone'])}" data-l-service="{e(fm['service'])}">
<div class="form-grid">
<label class="field" for="cf-name">{e(fm['name'])}<input id="cf-name" name="cf-name" type="text" autocomplete="name" required></label>
<label class="field" for="cf-company">{e(fm['company'])}<input id="cf-company" name="cf-company" type="text" autocomplete="organization"></label>
<label class="field" for="cf-phone">{e(fm['phone'])}<input id="cf-phone" name="cf-phone" type="tel" autocomplete="tel" dir="ltr" required></label>
<label class="field" for="cf-service">{e(fm['service'])}<select id="cf-service" name="cf-service">{options}</select></label>
</div>
<label class="field" for="cf-message">{e(fm['message'])}<textarea id="cf-message" name="cf-message" rows="5"></textarea></label>
<p class="form-error" role="alert"></p>
<button class="btn btn--primary" type="submit" style="align-self:flex-start">{icon('wa', 20, '#FFFFFF', 1.8)}{e(fm['send'])}</button>
<p class="form-note">{e(fm['note'])}</p>
</form>
</div></section>
</main>
""" + footer(lang, f)

    site_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "S99 Marketing", "url": SITE_URL + "/", "inLanguage": lang}
    hd = head(lang, f, h["title"], h["description"], page_url("en", "home"), page_url("ar", "home"), [business_ld(), site_ld])
    return f, wrap_doc(lang, f, hd, body, fragment=(PREVIEW and lang == "en"))


# ---------------------------------------------------------------- service pages
def build_service(lang, s):
    c = s[lang]
    u = UI[lang]
    f = page_file(lang, "svc", s["slug"])
    other = page_file("ar" if lang == "en" else "en", "svc", s["slug"])
    root = root_of(f)
    home = page_file(lang, "home")
    img = lambda n: f"{root}assets/img/work/{n}.webp"

    hero_imgs = "".join(f'<img src="{img(n)}" alt="" loading="{"eager" if i == 0 else "lazy"}">' for i, n in enumerate(s["hero_images"]))
    chips = "".join(f'<span class="chip">{e(x)}</span>' for x in c["chips"])
    inc = "".join(f'<div class="inc"><h3 class="h3">{e(t)}</h3><p>{e(d)}</p></div>' for t, d in c["included"])
    steps = "".join(f'<li><span class="outline-num" aria-hidden="true">0{i}</span><h3 class="h3">{e(t)}</h3><p>{e(d)}</p></li>' for i, (t, d) in enumerate(c["process"], 1))
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in c["faq"])
    others = "".join(f'<a href="{rel(f, page_file(lang, "svc", o["slug"]))}">{e(o[lang]["name"])} <span class="flip" aria-hidden="true">→</span></a>' for o in SERVICES if o["slug"] != s["slug"])

    pk = ""
    if s["packages"]:
        P = PACKAGES[lang]
        cards = ""
        for name, sub, pop, items in P["items"]:
            li = "".join(f"<li>{e(x)}</li>" for x in items)
            badge = f'<span class="badge">{e(P["popular"])}</span>' if pop else ""
            btn = "btn--primary" if pop else "btn--ghost"
            cards += (f'<div class="pkg{" pkg--pop" if pop else ""}">{badge}<div><h3>{e(name)}</h3><p class="muted" style="font-size:14px">{e(sub)}</p></div>'
                      f'<ul>{li}</ul><a class="btn {btn}" href="{rel(f, home)}#contact">{e(u["quote"])}</a></div>')
        pk = f"""<section id="packages" class="section"><div class="wrap">
<div class="sec-head sec-head--center"><div><p class="eyebrow">{e(P['eyebrow'])}</p><h2 class="h2">{e(P['h'])}</h2></div></div>
<div class="pkgs">{cards}</div>
</div></section>
"""

    body = site_open(lang, f) + header(lang, f, other, current="services") + f"""<main id="main">
<section class="section" style="padding-top:56px"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="{rel(f, home)}">{e(u['home'])}</a><span aria-hidden="true">/</span><a href="{rel(f, home)}#services">{e(u['services'])}</a><span aria-hidden="true">/</span><span aria-current="page" style="color:#fff">{e(c['name'])}</span></nav>
<div class="svc-hero">
<div class="svc-hero-text">
<h1>{e(c['h1'])}</h1>
<p>{e(c['intro'])}</p>
<div class="hero-actions" style="margin:0"><a class="btn btn--primary" href="{rel(f, home)}#contact">{e(u['quote'])}</a><a class="btn btn--ghost" href="https://wa.me/{COMPANY['whatsapp']}" target="_blank" rel="noopener">{e(u['whatsapp_us'])}</a></div>
<div class="chips">{chips}</div>
</div>
<div class="svc-hero-img">{hero_imgs}</div>
</div>
</div></section>

<section id="clients-work" class="section section--alt"><div class="wrap">
<div class="sec-head"><div><p class="eyebrow">{e(c['name'])}</p><h2 class="h2">{e(c['work_h'])}</h2></div><p>{e(c['work_p'])}</p></div>
<div class="filters" id="svc-filters" role="group" aria-label="{e(c['work_h'])}" style="margin-bottom:28px"></div>
<div class="svc-work svc-work--{s['work']}" id="svc-work" data-kind="{s['work']}"></div>
</div></section>

<section class="section"><div class="wrap">
<div class="sec-head"><div><p class="eyebrow">{e(c['name'])}</p><h2 class="h2">{e(c['included_h'])}</h2></div></div>
<div class="inc-grid{' inc-grid--3' if len(c['included']) % 3 == 0 and len(c['included']) % 4 else ''}">{inc}</div>
</div></section>

<section class="section section--alt"><div class="wrap">
<div class="sec-head"><div><h2 class="h2">{e(c['process_h'])}</h2></div></div>
<ol class="steps">{steps}</ol>
</div></section>
{pk}
<section class="section section--alt"><div class="wrap">
<div class="sec-head sec-head--center"><div><h2 class="h2">{'أسئلة شائعة' if lang == 'ar' else 'Questions we get asked'}</h2></div></div>
<div class="faq">{faq}</div>
</div></section>

<section class="section cta-band"><div class="wrap">
<div class="text"><h2 class="h2">{e(c['cta_h'])}</h2><p>{e(c['cta_p'])}</p></div>
<div class="actions"><a class="btn btn--light" href="https://wa.me/{COMPANY['whatsapp']}" target="_blank" rel="noopener">{icon('wa', 20, '#000000', 1.8)}{e(u['whatsapp_us'])}</a><a class="btn btn--ghost" href="{rel(f, home)}#contact">{e(u['quote'])}</a></div>
</div></section>

<section class="section" style="padding-block:72px"><div class="wrap">
<p class="eyebrow" style="margin-bottom:18px">{'خدمات أخرى' if lang == 'ar' else 'Other services'}</p>
<div class="more-svcs">{others}</div>
</div></section>
</main>
""" + footer(lang, f)

    service_ld = {"@context": "https://schema.org", "@type": "Service", "name": c["name"], "description": c["description"],
                  "provider": {"@id": SITE_URL + "/#business"}, "areaServed": ["EG", "SA"], "url": page_url(lang, "svc", s["slug"])}
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in c["faq"]]}
    crumbs_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": u["home"], "item": page_url(lang, "home")},
        {"@type": "ListItem", "position": 2, "name": c["name"], "item": page_url(lang, "svc", s["slug"])}]}
    hd = head(lang, f, c["title"], c["description"], page_url("en", "svc", s["slug"]), page_url("ar", "svc", s["slug"]), [business_ld(), service_ld, faq_ld, crumbs_ld])
    return f, wrap_doc(lang, f, hd, body)


def build_404():
    f = "404.html"
    hd = (f'<title>Page not found | S99 Marketing</title><meta name="robots" content="noindex">'
          f'<link rel="icon" href="{BASE_PATH}assets/img/favicon.ico"><link rel="stylesheet" href="{BASE_PATH}assets/css/site.css">')
    body = f"""<main class="section" style="min-height:80vh;display:flex;align-items:center"><div class="wrap" style="display:flex;flex-direction:column;gap:24px;align-items:flex-start">
<img src="{BASE_PATH}assets/img/logo-nav.png" alt="S99 Marketing" width="120" height="56">
<p class="num" style="font-size:120px">404</p>
<h1 class="h2">Page not found</h1><p class="muted" lang="ar" dir="rtl" style="font-family:Cairo,sans-serif;font-size:20px">الصفحة غير موجودة</p>
<div style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn--primary" href="{BASE_PATH}">Home</a><a class="btn btn--ghost" href="{BASE_PATH}ar/" lang="ar" style="font-family:Cairo,sans-serif;letter-spacing:0">الرئيسية</a></div>
</div></main>"""
    return f, wrap_doc("en", f, hd, body)


# ---------------------------------------------------------------- SEO files
def seo_files():
    today = date.today().isoformat()
    urls = [("home", None)] + [("svc", s["slug"]) for s in SERVICES]
    items = []
    for kind, slug in urls:
        en, ar = page_url("en", kind, slug), page_url("ar", kind, slug)
        for loc in (en, ar):
            items.append(f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{today}</lastmod>
    <xhtml:link rel="alternate" hreflang="en" href="{en}"/>
    <xhtml:link rel="alternate" hreflang="ar" href="{ar}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{en}"/>
  </url>""")
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
               'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(items) + "\n</urlset>\n")
    robots = f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n"
    headers = ("/assets/*\n  Cache-Control: public, max-age=2592000\n\n"
               "/data/*\n  Cache-Control: no-cache\n\n"
               "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n")
    return {"sitemap.xml": sitemap, "robots.txt": robots, "_headers": headers}


# ---------------------------------------------------------------- main
def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT)
    pages = []
    for lang in ("en", "ar"):
        pages.append(build_home(lang))
        for s in SERVICES:
            pages.append(build_service(lang, s))
    if not PREVIEW:
        pages.append(build_404())
        pages.append((".nojekyll", ""))
        for name, text in seo_files().items():
            pages.append((name, text))
    for f, text in pages:
        p = os.path.join(OUT, f)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
    print("Built %d files into %s" % (len(pages), OUT))


if __name__ == "__main__":
    main()
