#!/usr/bin/env python3
"""Skriver <head>-blokken på alle sider (mellom <!-- seo:start --> og <!-- seo:end -->): canonical, Open Graph,
fonter (preconnect + Google Fonts), ikoner og JSON-LD. Bygger også sitemap.xml, llms.txt og _redirects.

Strukturerte data kommer fra samme kilder som det synlige innholdet: content/venues.json (Restaurant, adresse,
geo, åpningstider, booking), content/menus.js (Menu) og tools/media.py (Review/NewsArticle – nøyaktig de
omtalene som vises på siden). FAQPage leses tilbake fra HTML-en, så den speiler alltid synlige spørsmål.
Kjør: python3 tools/build.py (eller python3 tools/seo_head.py etter at sidene er bygget)."""
import json, re, os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv, pages, faq
import media as MD
os.chdir(kv.ROOT)

DOMAIN = kv.DOMAIN
V = kv.venues(); ORG = V['org']
ORG_ID = DOMAIN + '#organization'; SITE_ID = DOMAIN + '#website'
TODAY = datetime.date.today().isoformat()
FONTS = 'https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,500;0,600;1,400&family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap'
ZENCHEF = 'https://bookings.zenchef.com/results?rid={rid}&lang=no'
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
OUTLET_NAMES = {'dagbladet': 'Dagbladet', 'finansavisen': 'Finansavisen', 'vg': 'VG / Godt.no', 'aftenposten': 'Aftenposten', 'dn': 'Dagens Næringsliv',
                'dagsavisen': 'Dagsavisen', 'nettavisen': 'Nettavisen', 'tb': 'Tønsbergs Blad', 'meravoslo': 'Mer av Oslo', 'op': 'Østlands-Posten', 'godt': 'Godt.no'}
try:
    _conf = json.load(open('tools/press-confirmed-2026-09-15.json', encoding='utf-8'))
    CONFIRMED = {i['url']: i for i in (_conf if isinstance(_conf, list) else _conf.get('items', []))}
except Exception:
    CONFIRMED = {}

BRAND = (kv.site_copy().get('brandStory') or {}).get('no') or ('Kverneriet er en norsk burgerrestaurant startet i Tønsberg i 2013, med restauranter på Majorstua (2015) og Solli plass (2017) i Oslo. '
         'Vi kverner alt kjøttet selv av storfe i toppklasse, steker burgerne medium pluss, lager trippelkokte fries som tar tre dager og serverer soft serve og milkshakes på Jersey-melk. '
         'Take-away-emballasjen er vår egen, i naturmaterialer.')

def img_size(path):
    try:
        import subprocess
        out = subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', path.lstrip('/')], capture_output=True, text=True).stdout
        w = int(re.search(r'pixelWidth: (\d+)', out).group(1)); h = int(re.search(r'pixelHeight: (\d+)', out).group(1))
        return w, h
    except Exception:
        return None

def org_node(full=True):
    n = {"@type": "Organization", "@id": ORG_ID, "name": ORG['name'], "legalName": ORG.get('legalName', ORG['name']), "url": DOMAIN,
         "logo": {"@type": "ImageObject", "url": DOMAIN + "assets/logo.svg", "width": 479, "height": 100},
         "image": DOMAIN + "assets/img/index-hero.jpg", "foundingDate": ORG['founded'], "telephone": ORG['telephone'], "email": ORG['email'],
         "description": BRAND, "sameAs": ORG['sameAs']}
    if full:
        n["subOrganization"] = [{"@type": "Restaurant", "@id": kv.abs_url(v['slug']) + '#restaurant', "name": v['fullName'], "url": kv.abs_url(v['slug'])} for v in V['venues']]
    return n

def opening_hours(v):
    """Åpent for gjester = kjøkkenet åpner → baren stenger (kjøkkentidene står i teksten og i description)."""
    opens = {}; closes = {}
    for h in v['hours']['kitchen']:
        for d in h['days']: opens[d] = h['opens']
    for h in v['hours']['bar']:
        for d in h['days']: closes[d] = h['closes']
    out = []
    for d in DAYS:
        if d in opens:
            same = next((o for o in out if o['opens'] == opens[d] and o['closes'] == closes.get(d, opens[d])), None)
            if same: same['dayOfWeek'].append(d)
            else: out.append({"@type": "OpeningHoursSpecification", "dayOfWeek": [d], "opens": opens[d], "closes": closes.get(d, opens[d])})
    return out

def reviews(slug):
    revs, articles = [], []
    for m in MD.MEDIA:
        if m['venue'] != slug: continue
        conf = CONFIRMED.get(m['url'], {})
        date = conf.get('date') or m['date']
        pub = {"@type": "Organization", "name": OUTLET_NAMES.get(m['outlet'], m['outlet'])}
        t = m['title']; t = t[1:-1] if t.startswith('«') and t.endswith('»') else t
        r = re.fullmatch(r'(\d+)/(\d+)', m['rating'] or '')
        if r:
            revs.append({"@type": "Review", "author": pub, "publisher": pub, "datePublished": date, "url": m['url'],
                         "reviewRating": {"@type": "Rating", "ratingValue": r.group(1), "bestRating": r.group(2), "worstRating": "1"},
                         "reviewBody": m['quote'], "name": t})
        else:
            articles.append({"@type": "NewsArticle", "headline": t, "url": m['url'], "datePublished": date, "publisher": pub, "description": m['quote']})
    return revs, articles

def restaurant_node(v, with_reviews=True):
    slug = v['slug']; a = v['address']
    kitchen = '; '.join(f'{kv.day_range(h["days"])} {kv.hhmm(h["opens"])}–{kv.hhmm(h["closes"])}' for h in v['hours']['kitchen'])
    same = [v['facebook']] + [u for u in (v['channels'].get('wolt'), v['channels'].get('foodora')) if u]
    n = {"@type": "Restaurant", "@id": kv.abs_url(slug) + '#restaurant', "name": v['fullName'], "alternateName": f"Kverneriet {v['area']}" if v['area'] != v['name'] else None,
         "url": kv.abs_url(slug), "image": [DOMAIN + pages.PAGES[slug]['img'].lstrip('/')],
         "description": f"Burgerrestaurant på {v['area']} i {v['city']} siden {v['since']}. Kjøtt vi kverner selv, trippelkokte fries, hot wings, soft serve og milkshakes. Kjøkkenet: {kitchen}. Lunsj {v['lunch']}.",
         "telephone": ORG['telephone'], "email": v['email'],
         "address": {"@type": "PostalAddress", "streetAddress": a['street'], "postalCode": a['postalCode'], "addressLocality": a['city'], "addressCountry": "NO"},
         "geo": {"@type": "GeoCoordinates", "latitude": v['geo']['lat'], "longitude": v['geo']['lng']},
         "hasMap": v['maps']['google'], "servesCuisine": ["Burger", "Amerikansk"], "priceRange": ORG['priceRange'], "currenciesAccepted": "NOK",
         "openingHoursSpecification": opening_hours(v),
         "acceptsReservations": ZENCHEF.format(rid=v['zenchef']),
         "potentialAction": {"@type": "ReserveAction", "target": {"@type": "EntryPoint", "urlTemplate": ZENCHEF.format(rid=v['zenchef']), "inLanguage": "nb", "actionPlatform": ["http://schema.org/DesktopWebPlatform", "http://schema.org/MobileWebPlatform"]},
                             "result": {"@type": "Reservation", "name": "Bordbestilling"}},
         "hasMenu": {"@type": "Menu", "@id": kv.abs_url(slug + '-menu') + '#menu', "url": kv.abs_url(slug + '-menu'), "name": f"Meny – {v['fullName']}"},
         "menu": kv.abs_url(slug + '-menu'), "foundingDate": v['since'], "parentOrganization": {"@id": ORG_ID}, "sameAs": same}
    n = {k: x for k, x in n.items() if x is not None}
    if with_reviews:
        revs, arts = reviews(slug)
        if revs: n["review"] = revs
        if arts: n["subjectOf"] = arts
    return n

def price_of(s):
    m = re.search(r'\d+', s or ''); return m.group(0) if m else None

def menu_node(slug):
    v = next(x for x in kv.menus()['venues'] if x['slug'] == slug)
    sections = []
    for s in v['menu']['sections']:
        items = []
        for it in s['items']:
            mi = {"@type": "MenuItem", "name": it['name']}
            if it.get('description'): mi["description"] = it['description'] + ((' ' + it['emphasis']) if it.get('emphasis') else '')
            if it.get('allergens'): mi["description"] = (mi.get("description", '') + f" Allergener: {', '.join(kv.menus()['allergenKey'].get(a, a) for a in it['allergens'])}.").strip()
            p = price_of(it['price'])
            if p: mi["offers"] = {"@type": "Offer", "price": p, "priceCurrency": "NOK"}
            items.append(mi)
        sec = {"@type": "MenuSection", "name": s['title'], "hasMenuItem": items}
        if s.get('intro'): sec["description"] = s['intro']
        addons = [{"@type": "MenuItem", "name": u['name'], **({"description": u['note']} if u.get('note') else {}),
                   **({"offers": {"@type": "Offer", "price": price_of(u['delta']), "priceCurrency": "NOK"}} if price_of(u.get('delta')) else {})}
                  for u in (s.get('upgrades', []) + s.get('dips', []))]
        if addons: sec["menuAddOn"] = addons
        sections.append(sec)
    return {"@context": "https://schema.org", "@type": "Menu", "@id": kv.abs_url(slug + '-menu') + '#menu', "name": f"Meny – Kverneriet {v['name']}",
            "url": kv.abs_url(slug + '-menu'), "inLanguage": "en", "description": f"Menyen på Kverneriet {v['name']} med priser i NOK og allergener.",
            "offers": {"@type": "Offer", "priceCurrency": "NOK"}, "hasMenuSection": sections}

def crumbs(*items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}

def webpage(slug, extra=None):
    p = pages.PAGES[slug]
    n = {"@context": "https://schema.org", "@type": "WebPage", "@id": kv.abs_url(slug) + '#webpage', "name": p['title'], "description": p['desc'], "url": kv.abs_url(slug),
         "inLanguage": "nb", "isPartOf": {"@id": SITE_ID}, "about": {"@id": ORG_ID}, "primaryImageOfPage": absimg(p['img'])}
    if extra: n.update(extra)
    return n

def ld_for(slug, html):
    ld = []
    if slug == 'index':
        ld.append({"@context": "https://schema.org", "@type": "WebSite", "@id": SITE_ID, "name": "Kverneriet", "url": DOMAIN, "inLanguage": "nb", "publisher": {"@id": ORG_ID}})
        ld.append({"@context": "https://schema.org", **org_node(True)})
    elif slug in kv.VENUE_SLUGS:
        v = kv.venue(slug)
        ld.append({"@context": "https://schema.org", **restaurant_node(v)})
        ld.append(crumbs(("Kverneriet", DOMAIN), (v['name'], kv.abs_url(slug))))
    elif slug.endswith('-menu'):
        vs = slug[:-5]; v = kv.venue(vs)
        ld.append(menu_node(vs))
        ld.append(crumbs(("Kverneriet", DOMAIN), (v['name'], kv.abs_url(vs)), ("Meny", kv.abs_url(slug))))
    elif slug == 'meny':
        ld.append(webpage(slug, {"@type": "CollectionPage", "hasPart": [{"@type": "Menu", "@id": kv.abs_url(v['slug'] + '-menu') + '#menu', "url": kv.abs_url(v['slug'] + '-menu'), "name": f"Meny – {v['fullName']}"} for v in V['venues']]}))
        ld.append(crumbs(("Kverneriet", DOMAIN), ("Meny", kv.abs_url('meny'))))
    elif slug == 'blogg':
        ld.append(webpage(slug, {"@type": "Blog", "name": "Kverneriet – blogg"}))
        ld.append(crumbs(("Kverneriet", DOMAIN), ("Blogg", kv.abs_url('blogg'))))
    elif slug.startswith('blog-'):
        p = pages.PAGES[slug]['post']
        n = {"@context": "https://schema.org", "@type": "BlogPosting", "@id": kv.abs_url(slug) + '#post', "headline": p['title'], "url": kv.abs_url(slug), "inLanguage": "nb",
             "datePublished": p['publishedAt'], "dateModified": p.get('updatedAt') or p['publishedAt'], "description": pages.PAGES[slug]['desc'],
             "author": {"@type": "Organization", "name": p.get('author') or "Kverneriet"}, "publisher": {"@id": ORG_ID}, "isPartOf": {"@id": SITE_ID},
             "mainEntityOfPage": kv.abs_url(slug)}
        if (p.get('mainImage') or {}).get('url'): n["image"] = p['mainImage']['url']
        ld.append(n)
        ld.append(crumbs(("Kverneriet", DOMAIN), ("Blogg", kv.abs_url('blogg')), (p['title'], kv.abs_url(slug))))
    else:
        ld.append(webpage(slug))
        name = {'takeaway': 'Take-away', 'lunsj': 'Lunsj', 'julebord': 'Julebord', 'selskap': 'Selskap og grupper', 'late-night': 'Late night'}[slug]
        ld.append(crumbs(("Kverneriet", DOMAIN), (name, kv.abs_url(slug))))
    pairs = faq.from_html(html)
    if pairs: ld.append(faq.ld(pairs))
    return ld

def absimg(path): return path if path.startswith('http') else DOMAIN + path.lstrip('/')

def head_block(slug, html):
    p = pages.PAGES[slug]; url = kv.abs_url(slug); img = absimg(p['img'])
    size = img_size(p['img']) if not p['img'].startswith('http') else None
    og_size = f'<meta property="og:image:width" content="{size[0]}">\n<meta property="og:image:height" content="{size[1]}">\n' if size else ''
    ld = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False, separators=(",", ":"))}</script>\n' for x in ld_for(slug, html))
    return (f'<link rel="canonical" href="{url}">\n'
            '<meta property="og:type" content="website">\n<meta property="og:site_name" content="Kverneriet">\n'
            f'<meta property="og:title" content="{kv.esc(p["title"])}">\n<meta property="og:description" content="{kv.esc(p["desc"])}">\n'
            f'<meta property="og:image" content="{img}">\n{og_size}<meta property="og:url" content="{url}">\n<meta property="og:locale" content="nb_NO">\n'
            '<meta name="twitter:card" content="summary_large_image">\n'
            '<meta name="theme-color" content="#085C51">\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link rel="stylesheet" href="{FONTS}">\n'
            '<link rel="preload" href="/assets/fonts/BourtonBase.ttf" as="font" type="font/ttf" crossorigin>\n'
            '<link rel="icon" href="/favicon.ico" sizes="32x32">\n<link rel="icon" href="/assets/icons/icon.svg" type="image/svg+xml">\n'
            '<link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png">\n<link rel="manifest" href="/site.webmanifest">\n'
            + ld)

HEAD_RE = re.compile(r'<title>.*?</title>\n<meta name="description" content="[^"]*">\n<!-- seo:start -->.*?<!-- seo:end -->\n', re.S)
ICON_RE = re.compile(r'<link rel="icon" type="image/svg\+xml" href="[^"]*">\n')

def apply_all():
    for slug, (file, _) in kv.PAGES.items():
        if not os.path.exists(file): print(file, 'mangler – hoppet over'); continue
        p = pages.PAGES[slug]
        html = open(file, encoding='utf-8').read()
        html = ICON_RE.sub('', html)
        block = f'<title>{kv.esc(p["title"])}</title>\n<meta name="description" content="{kv.esc(p["desc"])}">\n<!-- seo:start -->\n' + head_block(slug, html) + '<!-- seo:end -->\n'
        html2, n = HEAD_RE.subn(lambda m: block, html, count=1)
        if n != 1: raise SystemExit(f'{file}: fant ikke head-blokken')
        html2 = html2.replace('<html lang="no">', '<html lang="nb">')
        open(file, 'w', encoding='utf-8').write(html2); print(file, 'head ok')

def POSTS_EXIST(): return bool(kv.posts())

def sitemap():
    prio = {'index': '1.0', 'majorstua': '0.9', 'solli': '0.9', 'tonsberg': '0.9', 'majorstua-menu': '0.8', 'solli-menu': '0.8', 'tonsberg-menu': '0.8', 'meny': '0.6', 'takeaway': '0.8', 'blogg': '0.6'}
    def lastmod(s):
        p = pages.PAGES.get(s, {}); return (p.get('post') or {}).get('publishedAt', TODAY)[:10] if s.startswith('blog-') else TODAY
    rows = ''.join(f'  <url><loc>{kv.abs_url(s)}</loc><lastmod>{lastmod(s)}</lastmod><changefreq>{"weekly" if s in prio and prio[s] >= "0.8" else "monthly"}</changefreq><priority>{prio.get(s, "0.6" if s.startswith("blog-") else "0.7")}</priority></url>\n' for s in kv.PAGES if s != 'blogg' or POSTS_EXIST())
    open('sitemap.xml', 'w', encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + '</urlset>\n')
    print('sitemap.xml ok')

def llms():
    lines = ['# Kverneriet', '', f'> {BRAND}', '', '## Restauranter']
    for v in V['venues']:
        a = v['address']; kitchen = ', '.join(f'{kv.day_range(h["days"])} {kv.hhmm(h["opens"])}–{kv.hhmm(h["closes"])}' for h in v['hours']['kitchen'])
        bar = ', '.join(f'{kv.day_range(h["days"])} til {kv.hhmm(h["closes"])}' for h in v['hours']['bar'])
        lines += [f'- [{v["fullName"]}]({kv.abs_url(v["slug"])}): {a["street"]}, {a["postalCode"]} {a["city"]} ({v["area"]}). Åpnet {v["since"]}. Tlf {ORG["telephoneDisplay"]}. Kjøkken: {kitchen}. Bar: {bar}. Lunsj {v["lunch"]}. Meny: {kv.abs_url(v["slug"] + "-menu")}. Online booking (inntil {v["groupThreshold"]} personer): {ZENCHEF.format(rid=v["zenchef"])}. Take-away: {v["channels"]["pickup"]}' + (f', Wolt {v["channels"]["wolt"]}' if v['channels'].get('wolt') else '') + (f', Foodora {v["channels"]["foodora"]}' if v['channels'].get('foodora') else '')]
    lines += ['', '## Sider']
    for s in kv.PAGES: lines.append(f'- [{pages.PAGES[s]["title"]}]({kv.abs_url(s)}): {pages.PAGES[s]["desc"]}')
    pk = ORG['packages']
    lines += ['', '## Selskap og julebord', f'- {pk["note"]}'] + [f'- {p["name"]}: {p["price"]} kr per person. {p["desc"]}' for p in pk['items']] + [f'- Barnemeny: {pk["kids"]} kr (under 12 år).']
    lines += ['', '## Presse (utvalg)']
    for m in MD.MEDIA[:10]:
        lines.append(f'- {OUTLET_NAMES.get(m["outlet"], m["outlet"])} {m["date"]}{(" – " + m["rating"]) if m["rating"] else ""}: «{m["quote"]}» {m["url"]}')
    lines += ['', f'## Gavekort', f'- {ORG["giftcard"]}', '', f'Sist oppdatert {TODAY}.']
    open('llms.txt', 'w', encoding='utf-8').write('\n'.join(lines) + '\n'); print('llms.txt ok')

# Gamle adresser → nye. Brukes både i _redirects (Netlify/Cloudflare) og som HTML-stubber for GitHub Pages,
# som ikke har viderekoblinger på serveren.
REDIRECTS = [('/majorstua.html', '/majorstua/'), ('/solli.html', '/solli/'), ('/tonsberg.html', '/tonsberg/'), ('/meny.html', '/meny/'),
             ('/takeaway.html', '/takeaway/'), ('/lunsj.html', '/lunsj/'), ('/julebord.html', '/julebord/'), ('/selskap.html', '/selskap/'),
             ('/late-night.html', '/late-night/'), ('/packages/', '/selskap/'), ('/giftcard/', None), ('/gc/', None)]

def redirects():
    rows = ['# Viderekoblinger fra gamle kverneriet.com-adresser (Netlify/Cloudflare Pages-format; GitHub Pages bruker HTML-stubbene i stedet)', '/index.html  /  301']
    for old, new in REDIRECTS:
        new = new or ORG['giftcard']
        rows.append(f'{old}  {new}  301')
        if old.endswith('/'): rows.append(f'{old.rstrip("/")}  {new}  301')
    rows += ['/majorstua/menu  /majorstua/menu/  301', '/solli/menu  /solli/menu/  301', '/tonsberg/menu  /tonsberg/menu/  301']
    open('_redirects', 'w', encoding='utf-8').write('\n'.join(rows) + '\n'); print('_redirects ok')

def redirect_pages():
    """HTML-stubber på de gamle adressene (meta refresh + canonical + noindex) – det GitHub Pages kan tilby."""
    for old, new in REDIRECTS:
        target = new if new else ORG['giftcard']  # relativ sti, så stubbene virker også på <bruker>.github.io før domenet er flyttet
        path = old.lstrip('/') + ('index.html' if old.endswith('/') else '')
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        open(path, 'w', encoding='utf-8').write(
            f'<!DOCTYPE html>\n<html lang="nb">\n<head>\n<meta charset="utf-8">\n<title>Siden har flyttet – Kverneriet</title>\n'
            f'<link rel="canonical" href="{(DOMAIN.rstrip("/") + new) if new else target}">\n<meta http-equiv="refresh" content="0; url={target}">\n<meta name="robots" content="noindex">\n'
            f'<script>location.replace("{target}")</script>\n</head>\n<body>\n<p>Siden har flyttet til <a href="{target}">{target}</a>.</p>\n</body>\n</html>\n')
    print('redirect-stubber ok', len(REDIRECTS))

def robots():
    open('robots.txt', 'w', encoding='utf-8').write(
        'User-agent: *\nAllow: /\nDisallow: /tools/\n\n'
        '# AI-crawlere er velkomne (svarmotorer skal kunne sitere adresser, åpningstider og meny)\n'
        'User-agent: GPTBot\nAllow: /\n\nUser-agent: ClaudeBot\nAllow: /\n\nUser-agent: PerplexityBot\nAllow: /\n\nUser-agent: Google-Extended\nAllow: /\n\n'
        f'Sitemap: {DOMAIN}sitemap.xml\n')
    print('robots.txt ok')

def manifest():
    open('site.webmanifest', 'w', encoding='utf-8').write(json.dumps({
        "name": "Kverneriet", "short_name": "Kverneriet", "start_url": "/", "display": "browser", "background_color": "#FAF7F2", "theme_color": "#085C51",
        "icons": [{"src": "/assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, indent=1) + '\n')

if __name__ == '__main__':
    apply_all(); sitemap(); llms(); redirects(); redirect_pages(); robots(); manifest()
