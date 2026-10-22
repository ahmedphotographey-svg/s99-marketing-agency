# -*- coding: utf-8 -*-
"""Builds the S99 Marketing static website.

    python3 build.py            -> dist/     (upload this folder to Cloudflare Pages)
    python3 build.py --preview  -> preview/  (same site, links point at index.html files)

Change SITE_URL once the domain is bought.
"""
import html
import hashlib
import json
import os
import shutil
import sys
from datetime import date

from content import COMPANY, UI, HOME, PACKAGES, SERVICES
from content_home import HOME2, CLIENT_LOGOS

SITE_URL = os.environ.get("SITE_URL", "https://ahmedphotographey-svg.github.io/s99-marketing-agency")   # <-- change to the real domain when it is ready
BASE_PATH = "/" + SITE_URL.split("://", 1)[1].partition("/")[2].strip("/") + "/" if "/" in SITE_URL.split("://", 1)[1] else "/"
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
def asset_version(path):
    with open(os.path.join(SRC, "assets", path), "rb") as source:
        return hashlib.sha256(source.read()).hexdigest()[:12]

CSS_VERSION = asset_version("css/site.css")
JS_VERSION = asset_version("js/site.js")
SUPPORT_VERSION = asset_version("js/support.js")
PREVIEW = "--preview" in sys.argv
OUT = os.environ.get("OUT_DIR") or os.path.join(HERE, "preview" if PREVIEW else "dist")


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
<link rel="stylesheet" href="{root}assets/css/site.css?v={CSS_VERSION}">
<script>document.documentElement.classList.add('js')</script>
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


def phone_fields(prefix, ar):
    countries = [("20", "مصر", "Egypt"), ("966", "السعودية", "Saudi Arabia"), ("971", "الإمارات", "UAE"), ("973", "البحرين", "Bahrain"), ("968", "عمان", "Oman"), ("962", "الأردن", "Jordan"), ("965", "الكويت", "Kuwait"), ("974", "قطر", "Qatar"), ("1", "أمريكا / كندا", "US / Canada"), ("44", "بريطانيا", "UK")]
    opts = ''.join(f'<option value="{code}">{arabic if ar else english} (+{code})</option>' for code, arabic, english in countries)
    return f'''<div class="phone-fields"><label class="field">{'كود الدولة (إجباري)' if ar else 'Country code (required)'}<select name="{prefix}-country" autocomplete="tel-country-code" required><option value="">{'اختر الدولة' if ar else 'Select country'}</option>{opts}</select></label><label class="field">{'رقم الموبايل (إجباري)' if ar else 'Mobile number (required)'}<input name="{prefix}-phone" id="{prefix}-phone" type="tel" inputmode="tel" autocomplete="tel-national" dir="ltr" maxlength="20" required aria-describedby="{prefix}-phone-help"><small id="{prefix}-phone-help">{'اكتب الرقم بدون كود الدولة.' if ar else 'Enter the number without the country code.'}</small></label></div>'''


def support_markup(ar):
    label = 'اسأل دعم S99' if ar else 'Ask S99 support'
    support_icon = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 13v-2a8 8 0 0 1 16 0v2"/><rect x="2" y="11" width="4" height="7" rx="2"/><rect x="18" y="11" width="4" height="7" rx="2"/><path d="M20 18v1a2 2 0 0 1-2 2h-4"/><path d="M10 21h4"/></svg>'
    return f'''<button class="support-launch" id="support-launch" type="button" aria-expanded="false" aria-controls="support-panel">{support_icon}<span>{label}</span></button>
<section class="support-panel" id="support-panel" role="dialog" aria-labelledby="support-title" hidden>
<header><div><b id="support-title">{label}</b><small>{'مساعد معلومات الشركة' if ar else 'Company information assistant'}</small></div><button type="button" id="support-close" aria-label="{'إغلاق' if ar else 'Close'}">×</button></header>
<form id="support-identity"><p>{'أهلاً بيك! عرّفنا بنفسك عشان نقدر نكمل معاك.' if ar else 'Welcome! Introduce yourself so we can help you.'}</p><label class="field">{'الاسم (إجباري)' if ar else 'Name (required)'}<input name="visitor-name" autocomplete="name" maxlength="100" minlength="2" required></label>{phone_fields('visitor', ar)}<p class="form-error" role="alert"></p><button type="submit" class="btn btn--primary">{'ابدأ المحادثة' if ar else 'Start conversation'}</button><small>{'بياناتك بتفضل في المحادثة دي، وبتُرفق برسالتك لما تختار التواصل على واتساب. الموقع لا يحفظها.' if ar else 'Your details stay in this conversation and are included when you choose WhatsApp. This site does not store them.'}</small></form>
<div id="support-chat" hidden>
<div class="support-messages" id="support-messages" role="log" aria-live="polite" aria-relevant="additions"></div>
<div class="support-topics"><button type="button" data-topic="company">{'عن الشركة' if ar else 'About S99'}</button><button type="button" data-topic="achievements">{'إنجازاتنا' if ar else 'Our work'}</button><button type="button" data-topic="services">{'الخدمات' if ar else 'Services'}</button></div>
<form id="support-question"><label for="support-input" class="sr-only">{'سؤالك' if ar else 'Your question'}</label><input id="support-input" maxlength="600" placeholder="{'اكتب سؤالك…' if ar else 'Ask a question…'}" required><button type="submit">{'اسأل' if ar else 'Ask'}</button></form>
<div class="support-handoff" id="support-handoff" hidden><a class="btn btn--primary" id="support-wa" target="_blank" rel="noopener">{'كمل التفاصيل على واتساب' if ar else 'Continue on WhatsApp'}</a><button type="button" id="support-callback">{'سيب رقمك للتواصل' if ar else 'Request a callback'}</button></div>
<form id="support-lead" hidden><label class="field">{'الاسم' if ar else 'Name'}<input name="lead-name" autocomplete="name" maxlength="100" required></label>{phone_fields('lead', ar)}<p class="form-error" role="alert"></p><button class="btn btn--primary" type="submit">{'إرسال طلب التواصل على واتساب' if ar else 'Send callback request on WhatsApp'}</button><small>{'هيفتح واتساب بطلبك جاهز. اضغط إرسال هناك؛ الرقم لا يُحفظ على الموقع.' if ar else 'WhatsApp opens with your request ready. Press Send there; this site does not store your number.'}</small></form>
</div></section>'''


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
{support_markup(lang == 'ar')}
<div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Video" hidden>
<button class="lb-close" type="button" aria-label="{e(u['close_video'])}">{icon('close', 20, '#FFFFFF', 2)}</button>
<div class="lb-body"><div class="lb-frame"></div><div class="lb-caption"><b></b><span></span></div></div>
</div>
</div>
<script src="{root}assets/js/site.js?v={JS_VERSION}" defer></script>
<script src="{root}assets/js/support.js?v={SUPPORT_VERSION}" defer></script>
"""


def business_ld():
    return {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "@id": SITE_URL + "/#business",
        "name": "S99 Marketing Agency",
        "alternateName": "S99 Marketing",
        "description": "Creative marketing and media production agency based in Cairo, Egypt, serving brands in Egypt, Saudi Arabia, Bahrain and the UAE.",
        "url": SITE_URL + "/",
        "logo": SITE_URL + "/assets/img/icon-512.png",
        "image": SITE_URL + "/assets/img/og-image.jpg",
        "telephone": COMPANY["phone_intl"],
        "email": COMPANY["email"],
        "foundingDate": "2024",
        "founder": {"@type": "Person", "name": "Ahmed Saleh"},
        "address": {"@type": "PostalAddress", "streetAddress": "Arab League Street, Agouza", "addressLocality": "Giza", "addressRegion": "Giza", "addressCountry": "EG"},
        "areaServed": [{"@type": "Country", "name": n} for n in ("Egypt", "Saudi Arabia", "Bahrain", "United Arab Emirates")],
        "openingHours": "Su-Th 12:00-20:00",
        "sameAs": [COMPANY[k] for k in ("instagram", "facebook", "tiktok") if COMPANY[k]],
        "knowsLanguage": ["ar", "en"],
    }


# ---------------------------------------------------------------- home page
def _work_data():
    with open(os.path.join(SRC, "data", "work.json"), encoding="utf-8") as fh:
        return json.load(fh)


def _num_html(value, suffix):
    """Counter markup: plain numbers count up in JS, anything else (a placeholder) is shown as-is."""
    v = str(value)
    if v.isdigit():
        return f'<span class="num" dir="ltr" data-count="{v}" data-suffix="{e(suffix)}">{e(v + suffix)}</span>'
    return f'<span class="num num--todo" dir="ltr">{e(v)}</span>'


CHECK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
CROSS = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>'


def build_home(lang):
    h = HOME[lang]
    h2 = HOME2[lang]
    u = UI[lang]
    ar = lang == "ar"
    f = page_file(lang, "home")
    other = page_file("ar" if lang == "en" else "en", "home")
    root = root_of(f)
    fm = h["form"]
    work = _work_data()

    # --- client logo lines (MG): two rows moving in opposite directions
    def logo_row(items):
        return "".join(f'<li class="mq-logo-{slug}"><img src="{root}assets/img/logos/{slug}.webp" alt="{e(name)}" width="{w}" height="{hh}" loading="lazy" decoding="async"></li>' for slug, name, w, hh in items)
    half = (len(CLIENT_LOGOS) + 1) // 2
    row1, row2 = logo_row(CLIENT_LOGOS[:half]), logo_row(CLIENT_LOGOS[half:])

    # --- portfolio coverflow: finished work (productions, posts, reels)
    def L(it, k):
        return (it.get(k + "_ar") or it.get(k, "")) if ar else it.get(k, "")
    prod = [x for x in work.get("production", []) if x.get("poster")]
    prod = ([x for x in prod if x.get("video") or x.get("youtube")] + [x for x in prod if not (x.get("video") or x.get("youtube"))])[:12]
    soc = [x for x in work.get("social", []) if x.get("image")][:8]
    reels = [x for x in work.get("reels", []) if x.get("youtube") and not x.get("video") and x.get("top", True)]
    infl = [{"client": x["influencer"], "client_ar": x.get("influencer_ar", ""), "type": " · ".join(v for v in (x["client"], x["country"]) if v),
             "type_ar": " · ".join(v for v in (x.get("client_ar") or x["client"], x.get("country_ar") or x["country"]) if v), "poster": x.get("poster", ""),
             "video": x.get("video", ""), "youtube": x.get("youtube", ""), "vertical": x.get("vertical", True)}
            for x in work.get("influencers", []) if x.get("poster") and (x.get("video") or x.get("youtube"))]
    seen = {}
    infl = [x for x in infl if seen.setdefault(x["type"].split(" · ")[0], []).append(1) or len(seen[x["type"].split(" · ")[0]]) <= 2]  # 2 per campaign
    # only finished client work (videos) in the coverflow
    # vertical client videos only; the wide films live in the films section
    cf_items = [("p", x) for x in work.get("production", []) if x.get("video") and x.get("poster") and x.get("vertical") is not False]
    cards = []
    for i, (k, it) in enumerate(cf_items):
        name, typ = L(it, "client"), L(it, "type")
        attrs = f' data-name="{e(name)}" data-type="{e(typ)}"'
        if k == "r":
            vid = it["youtube"].rstrip("/").split("/")[-1].split("?")[0].split("v=")[-1]
            media = (f'<span class="ph" aria-hidden="true">{e(it["client"])}</span>'
                     f'<img class="yt-cover" src="https://i.ytimg.com/vi/{e(vid)}/oar2.jpg" data-fallback="https://i.ytimg.com/vi/{e(vid)}/hqdefault.jpg" alt="" loading="lazy">')
            attrs += f' data-youtube="{e(it["youtube"])}" data-vertical="1"'
        else:
            src = it.get("poster") or it.get("image")
            media = f'<img src="{root}{e(src)}" alt="{e(name + " — " + typ)}" loading="lazy" decoding="async">'
            if it.get("youtube"):
                attrs += f' data-youtube="{e(it["youtube"])}"'
            elif it.get("video"):
                attrs += f' data-video="{e(it["video"])}"'
            attrs += f' data-img="{e(src)}"' + (' data-vertical="1"' if it.get("vertical") else "")
        tag = "" if k == "s" else f'<span class="cf-play" aria-hidden="true">{PLAY_ICON}</span>' if (k == "r" or it.get("video") or it.get("youtube")) else ""
        cards.append(f'<button class="cf-card" type="button" data-i="{i}"{attrs} aria-label="{e(name + " — " + typ)}">{media}{tag}</button>')
    cf_cards = "".join(cards)
    first_name, first_type = (L(cf_items[0][1], "client"), L(cf_items[0][1], "type")) if cf_items else ("", "")
    ribbon = "".join(f"<span>{e(w)}</span>" for w in h2["ribbon"]) * 3

    # --- about counters (24K)
    counters = "".join(f'<div class="stat reveal">{_num_html(v, s)}<span class="label-up">{e(l)}</span></div>' for v, s, l in h2["counters"])

    # --- specialists layers (ARQQA)
    layers = "".join(f'<li class="layer reveal" style="--d:{i * 90}ms"><span class="layer-n" dir="ltr">0{i + 1}</span><div><h3 class="h3">{e(t)}</h3><p>{e(d)}</p></div></li>'
                     for i, (t, d) in enumerate(h2["layers"]))
    markets = "".join(f'<span class="mk">{icon("pin", 18)}{e(m)}</span>' for m in h2["markets_list"])
    network = "".join(f'<span class="chip">{e(x)}</span>' for x in h["network"])

    # --- the S99 system (stepper)
    tabs, panels = "", ""
    for i, (name, desc, items) in enumerate(h2["system"]):
        sel = "true" if i == 0 else "false"
        tabs += (f'<button class="sys-tab" type="button" role="tab" id="sys-t{i}" aria-controls="sys-p{i}" aria-selected="{sel}" tabindex="{0 if i == 0 else -1}">'
                 f'<span class="sys-n" dir="ltr">0{i + 1}</span><span>{e(name)}</span></button>')
        lis = "".join(f"<li>{CHECK}{e(x)}</li>" for x in items)
        panels += (f'<div class="sys-panel" role="tabpanel" id="sys-p{i}" aria-labelledby="sys-t{i}">'
                   f'<span class="sys-big" dir="ltr" aria-hidden="true">0{i + 1}</span><div><h3 class="h3">{e(name)}</h3><p>{e(desc)}</p><ul>{lis}</ul></div></div>')

    # --- services with a pain-point hook
    cards = ""
    for i, s in enumerate(SERVICES, 1):
        c = s[lang]
        hook = h2["hooks"].get(s["slug"], "")
        cards += (f'<a class="svc-card reveal" style="--d:{(i - 1) * 90}ms" href="{rel(f, page_file(lang, "svc", s["slug"]))}">'
                  f'<span class="top">{icon(s["icon"], 40, "#4A9BD4", 1.5)}<span class="outline-num" aria-hidden="true">0{i}</span></span>'
                  + (f'<span class="svc-hook">{e(hook)}</span>' if hook else "")
                  + f'<h3 class="h3">{e(c["name"])}</h3><p>{e(c["card"])}</p>'
                  f'<span class="more">{e(u["explore"])} <span class="flip" aria-hidden="true">→</span></span></a>')
    extras = "".join(f'<span class="chip">{e(x)}</span>' for x in h["extras"])

    # --- partners (how long clients stay)
    partners = "".join(
        f'<article class="partner reveal{" partner--top" if i == 0 else ""}" style="--d:{(i % 4) * 90}ms"><h3><bdi>{e(n)}</bdi></h3>'
        f'<p class="partner-since"><span class="label-up">{e(h2["since_label"])}</span>'
        f'<b dir="auto">{e(since)}</b></p><p class="partner-what">{e(what)}</p></article>'
        for i, (n, since, what) in enumerate(h2["partners"]))

    # --- myth vs fact
    myths = "".join(
        f'<button class="myth reveal" type="button" aria-pressed="false" style="--d:{i * 90}ms"><span class="myth-in">'
        f'<span class="myth-face myth-front"><small>{e(h2["myth_label"])}</small><b>{e(m)}</b><i aria-hidden="true">↻</i></span>'
        f'<span class="myth-face myth-back"><small>{e(h2["fact_label"])}</small><b>{e(fct)}</b></span></span></button>'
        for i, (m, fct) in enumerate(h2["myths"]))

    # --- before / after
    ba_left = "".join(f"<li>{CROSS}{e(x)}</li>" for x in h2["ba_left"])
    ba_right = "".join(f"<li>{CHECK}{e(x)}</li>" for x in h2["ba_right"])
    d = "rtl" if ar else "ltr"

    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in h2["faq"])
    options = "".join(f"<option>{e(x)}</option>" for x in fm["services"])

    body = site_open(lang, f) + f"""<div class="preloader" id="preloader" aria-hidden="true"><canvas class="pl-sphere" width="1200" height="1200"></canvas><img class="pl-mark" src="{root}assets/img/logo-nav.png" width="180" height="84" alt=""><span class="pl-caption">S99 / CREATIVE SYSTEM</span></div>
<script>(function(){{var p=document.getElementById('preloader');try{{if(sessionStorage.getItem('s99-pl-lunar-v5')){{p.remove();return}}sessionStorage.setItem('s99-pl-lunar-v5','1')}}catch(x){{}}document.documentElement.classList.add('pl-on')}})();</script>
""" + header(lang, f, other) + f"""<main id="main">
<section class="hook" aria-labelledby="hero-h" data-stage="1">
<div class="hook-pin">
<div class="wrap hook-inner">
<p class="hero-label">{e(h['hero_label'])}</p>
<div class="hook-lines">
<p class="hook-l hook-l1">{e(h2['hook'][0])}</p>
<h1 id="hero-h" class="hook-l hook-l2">{e(h2['hook'][1])}</h1>
</div>
<div class="hook-rest">
<p class="hero-p">{e(h['hero_p'])}</p>
<div class="hero-actions">
<a class="btn btn--primary" href="#contact">{e(h['hero_cta'])}</a>
<a class="play-btn" href="#work"><span class="ring">{PLAY_ICON}</span>{e(h['hero_reel'])}</a>
</div>
</div>
<span class="hook-hint" aria-hidden="true">{e(h2['hook_hint'])}<i></i></span>
</div>
</div>
</section>

<section class="marquee" id="clients" aria-label="{e(h['clients_h'])}"><p class="mq-label">{'علامات عملنا في مشاريعها' if ar else 'Brands we’ve worked on'}</p><div class="mq-row" dir="ltr"><ul class="mq-track">{row1}{row1}</ul></div><div class="mq-row" dir="ltr"><ul class="mq-track mq-rev">{row2}{row2}</ul></div></section>

<section class="section cf-sec" id="work" aria-labelledby="cf-h">
<div class="wrap sec-head"><div><p class="eyebrow">{e(h2['reel_eyebrow'])}</p><h2 class="h2" id="cf-h">{e(h2['reel_h'])}</h2></div><p>{e(h2['reel_p'])}</p></div>
<div class="cf" dir="ltr" tabindex="0" role="region" aria-roledescription="carousel" aria-label="{e(h2['reel_h'])}">
<div class="cf-stage">{cf_cards}</div>
</div>
<div class="wrap cf-under">
<p class="cf-cap" aria-live="polite"><span class="cf-num" dir="ltr">01</span><span><b><bdi>{e(first_name)}</bdi></b><small>{e(first_type)}</small></span></p>
<div class="cf-ctrl" dir="ltr"><button class="cf-prev" type="button" aria-label="{'السابق' if ar else 'Previous'}">←</button><span class="cf-i">01</span><span class="cf-line"><i></i></span><span class="cf-n">{len(cf_items):02d}</span><button class="cf-next" type="button" aria-label="{'التالي' if ar else 'Next'}">→</button></div>
<a class="btn btn--ghost cf-all" href="{rel(f, page_file(lang, 'svc', 'media-production'))}">{e(h2['cf_all'])} <span class="flip" aria-hidden="true">→</span></a>
</div>
</section>
<div class="ribbon" aria-hidden="true"><div class="ribbon-track" dir="ltr">{ribbon}{ribbon}</div></div>

<section id="influencers" class="section" aria-labelledby="inf-h">
<div class="wrap sec-head"><div><p class="eyebrow">{e(h['inf_eyebrow'])}</p><h2 class="h2" id="inf-h">{e(h['inf_h'])}</h2></div><p>{e(h['inf_p'])}</p></div>
<div class="rail" id="inf-rail" aria-label="{e(h['inf_h'])}"></div>
<div class="wrap"><a class="btn btn--ghost" href="{rel(f, page_file(lang, 'svc', 'influencer-marketing'))}">{e(h['inf_all'])} <span class="flip" aria-hidden="true">→</span></a></div>
</section>

<section class="section" style="padding-top:40px" aria-labelledby="films-h"><div class="wrap">
<div class="sec-head"><div><p class="eyebrow">{e(h['films_eyebrow'])}</p><h2 class="h2" id="films-h">{e(h['films_h'])}</h2></div><p>{e(h['films_p'])}</p></div>
<div id="featured" data-bts-h="{e(h['bts_h'])}" data-bts-p="{e(h['bts_p'])}"></div>
<div class="films" id="films"></div>
</div></section>

<section id="about" class="section"><div class="wrap about">
<div class="about-text">
<h2 class="h2">{e(h['about_h'])}</h2>
<p class="lead">{e(h['about_lead'])}</p>
<p class="muted">{e(h['about_p'])}</p>
<div class="founder"><span class="founder-mark" aria-hidden="true">{icon('team', 22)}</span><div><span class="label-up">{e(h['founder_label'])}</span><b>{e(h['founder_name'])}</b></div></div>
</div>
<div class="stats" aria-label="{e(h2['counters_h'])}">{counters}</div>
</div></section>

<section id="team" class="section section--alt" aria-labelledby="layers-h"><div class="wrap layers-wrap">
<div class="layers-head"><p class="eyebrow">{e(h2['layers_eyebrow'])}</p><h2 class="h2 big-h" id="layers-h">{e(h2['layers_h'])}</h2><p class="muted">{e(h2['layers_p'])}</p>
<div class="mk-row"><span class="label-up">{e(h2['markets_label'])}</span>{markets}</div>
<div class="network"><span class="label-up">{e(h['network_label'])}</span>{network}</div></div>
<ol class="layers">{layers}</ol>
</div></section>

<section id="system" class="section" aria-labelledby="sys-h"><div class="wrap">
<div class="sec-head"><div><p class="eyebrow">{e(h2['system_eyebrow'])}</p><h2 class="h2" id="sys-h">{e(h2['system_h'])}</h2></div><p>{e(h2['system_p'])}</p></div>
<div class="sys"><div class="sys-tabs" role="tablist" aria-label="{e(h2['system_h'])}">{tabs}</div><div class="sys-panels">{panels}</div></div>
</div></section>

<section id="services" class="section section--alt"><div class="wrap">
<div class="sec-head"><div><p class="eyebrow">{e(h['services_eyebrow'])}</p><h2 class="h2">{e(h['services_h'])}</h2></div><p>{e(h['services_p'])}</p></div>
<div class="cards-3">{cards}</div>
<div class="chips">{extras}</div>
</div></section>



<section id="partners" class="section section--alt" aria-labelledby="partners-h"><div class="wrap">
<div class="sec-head"><div><p class="eyebrow">{e(h2['partners_eyebrow'])}</p><h2 class="h2" id="partners-h">{e(h2['partners_h'])}</h2></div><p>{e(h2['partners_p'])}</p></div>
<div class="partners">{partners}</div>
</div></section>

<section class="section" aria-labelledby="myth-h"><div class="wrap">
<div class="sec-head"><div><p class="eyebrow">{e(h2['myth_eyebrow'])}</p><h2 class="h2" id="myth-h">{e(h2['myth_h'])}</h2></div><p>{e(h2['myth_hint'])}</p></div>
<div class="myths">{myths}</div>
</div></section>

<section class="section section--alt" aria-labelledby="ba-h"><div class="wrap">
<div class="sec-head sec-head--center"><div><p class="eyebrow">{e(h2['ba_eyebrow'])}</p><h2 class="h2" id="ba-h">{e(h2['ba_h'])}</h2></div></div>
<div class="ba" dir="ltr" style="--x:50%">
<div class="ba-side ba-old"><div class="ba-col" dir="{d}"><h3>{e(h2['ba_left_title'])}</h3><ul>{ba_left}</ul></div></div>
<div class="ba-side ba-new"><div class="ba-col" dir="{d}"><h3>{e(h2['ba_right_title'])}</h3><ul>{ba_right}</ul></div></div>
<span class="ba-handle" aria-hidden="true"><i>‹ ›</i></span>
<input class="ba-range" type="range" min="5" max="95" value="50" aria-label="{e(h2['ba_hint'])}">
</div>
<p class="ba-hint">{e(h2['ba_hint'])}</p>
</div></section>


<section id="faq" class="section"><div class="wrap">
<div class="sec-head sec-head--center"><div><p class="eyebrow">{e(h2['faq_eyebrow'])}</p><h2 class="h2">{e(h2['faq_h'])}</h2></div></div>
<div class="faq">{faq}</div>
</div></section>

<section class="section cta-band fork"><div class="wrap">
<div class="text"><h2 class="h2">{e(h2['fork_h'])}</h2></div>
<div class="actions"><a class="btn btn--light" href="#contact">{e(h2['fork_cta'])}</a></div>
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
{phone_fields('cf', ar)}
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
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in h2["faq"]]}
    hd = head(lang, f, h["title"], h["description"], page_url("en", "home"), page_url("ar", "home"), [business_ld(), site_ld, faq_ld])
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
                  "provider": {"@id": SITE_URL + "/#business"}, "areaServed": ["EG", "SA", "BH", "AE"], "url": page_url(lang, "svc", s["slug"])}
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
          f'<link rel="icon" href="{BASE_PATH}assets/img/favicon.ico"><link rel="stylesheet" href="{BASE_PATH}assets/css/site.css?v={CSS_VERSION}">')
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
