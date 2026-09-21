#!/usr/bin/env python3
"""Bygger hele nettstedet. Rekkefølgen betyr noe:
  1. build_venue / build_menu / build_landing  – genererte sider fra content/*.json|js
  2. index.html og takeaway/index.html         – håndskrevne, får header/footer/modal/FAQ/om-tekst satt inn her
  3. media.py, press.py                         – pressekort og tillitsrad
  4. images.py                                  – responsive bilder (srcset/webp/width/height)
  5. seo_head.py                                – <head>, JSON-LD, sitemap, llms.txt, robots, _redirects, manifest
  6. build_css + cache-busting                  – én CSS-fil, ?v= på CSS/JS
Kjør: python3 tools/build.py"""
import os, re, sys, hashlib, subprocess, datetime, functools
print = functools.partial(print, flush=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv, chrome, modal, faq, i18n_gen as G, pages
import build_venue, build_menu, build_landing, images, seo_head
import media as MD
os.chdir(kv.ROOT)

V = kv.venues(); ORG = V['org']
e = kv.esc

def about_section():
    G.add('home.aboutEyebrow', 'Om Kverneriet', 'About Kverneriet'); G.add('home.aboutTitle', 'Burgersjappa fra Tønsberg som ble tre restauranter', 'The Tønsberg burger joint that became three restaurants')
    G.add('home.about1', 'Kverneriet startet som en liten burgersjappe i Tønsberg i 2013. I 2015 åpnet vi på Majorstua i Oslo, og i 2017 ved Solli plass. Oppskriften er den samme alle tre steder: vi kverner alt kjøttet selv av storfe i toppklasse og steker burgerne medium pluss, brødene er ferske, og friesene er håndlagde, trippelkokte og tar tre dager – naturlig glutenfrie.',
          'Kverneriet started as a small burger joint in Tønsberg in 2013. In 2015 we opened at Majorstua in Oslo, and in 2017 at Solli plass. The recipe is the same in all three: we grind all the beef ourselves from top-grade cattle and cook the burgers medium plus, the buns are fresh, and the fries are handmade, triple-cooked and take three days – naturally gluten-free.')
    rng = faq.burger_range('majorstua') or (239, 289); fries = faq.fries_from() or 84; pk0 = ORG['packages']['items'][0]['price']
    G.add('home.about2', f'Burgerne koster fra {rng[0]} til {rng[1]} kr og fries fra {fries} kr. Bord for inntil 8 personer (7 i Tønsberg) booker du online med bekreftelse med en gang; større grupper sender forespørsel og velger matpakke fra {pk0} kr per person. Alle restaurantene har drop-in-bord og take-away du henter selv, og Majorstua og Solli leverer hjem med Wolt og Foodora.',
          f'Burgers cost NOK {rng[0]}–{rng[1]} and fries from NOK {fries}. Tables for up to 8 (7 in Tønsberg) are booked online with instant confirmation; larger groups send a request and choose a food package from NOK {pk0} per person. All three restaurants keep walk-in tables and do pick-up take-away, and Majorstua and Solli deliver with Wolt and Foodora.')
    return f'''  <!-- Om Kverneriet -->
  <section class="section" id="om">
    <div class="wrap grid-2 grid-2--start">
      <div>
        <header class="sec-head">
          <div class="sec-head__rule"></div>
          <span class="kv-eyebrow" data-i18n="home.aboutEyebrow">Om Kverneriet</span>
          <h2 class="display-2" data-i18n="home.aboutTitle">Burgersjappa fra Tønsberg som ble tre restauranter</h2>
        </header>
        <p class="lede" style="margin-top:var(--space-5)" data-i18n="home.about1">{e(G._D['no']['home.about1'])}</p>
        <p style="margin-top:var(--space-4)" data-i18n="home.about2">{e(G._D['no']['home.about2'])}</p>
      </div>
      <div class="card">
        <div class="kv-eyebrow" style="margin-bottom:var(--space-3)" data-i18n="home.restTitle">Restaurantene</div>
        {''.join(f'<div class="upgrade-row"><span class="upgrade-row__glyph" aria-hidden="true">➼</span><span class="upgrade-row__body"><span class="upgrade-row__name"><a href="{kv.url(v["slug"])}">{e(v["fullName"])}</a></span><span class="upgrade-row__note">{e(v["address"]["street"])}, {v["address"]["postalCode"]} {e(v["address"]["city"])} · <a href="tel:{ORG["telephone"]}">{ORG["telephoneDisplay"]}</a></span></span></div>' for v in V['venues'])}
        <p class="caption" style="margin-top:var(--space-4)"><span data-i18n="home.hoursNote">Åpningstider, meny og booking på hver restaurantside.</span></p>
      </div>
    </div>
  </section>

'''

def add_gen_script(s):
    return re.sub(r'(<script src="/content/i18n\.js[^"]*" defer></script>\n)(?!<script src="/content/i18n-gen\.js)', r'\1<script src="/content/i18n-gen.js" defer></script>\n', s, count=1)

def patch_index():
    s = open('index.html', encoding='utf-8').read()
    s = chrome.apply(s)
    s = modal.apply(s)
    s = s.replace('<main>', '<main id="main">', 1)
    # H1 beholder merkevarelinjen, men får en synlig undertekst med sted og produkt
    G.add('home.heroSub', 'Burgerrestaurant på Majorstua og Solli plass i Oslo, og i Tønsberg – siden 2013.', 'Burger restaurant at Majorstua and Solli plass in Oslo, and in Tønsberg – since 2013.')
    G.add('home.hoursNote', 'Åpningstider, meny og booking på hver restaurantside.', 'Opening hours, menu and booking on each restaurant page.')
    if 'home.heroSub' not in s:
        s = re.sub(r'<h1( lang="en")?>Flipping kick-ass burgers</h1>\n', '<h1 lang="en">Flipping kick-ass burgers</h1>\n    <p class="hero-home__sub" data-i18n="home.heroSub">Burgerrestaurant på Majorstua og Solli plass i Oslo, og i Tønsberg – siden 2013.</p>\n', 1)
    # Photo band: LCP-kandidat → fetchpriority
    s = s.replace('alt="Trippelkokte fries fra Kverneriet" loading="eager">', 'alt="Trippelkokte fries fra Kverneriet" loading="eager" fetchpriority="high" decoding="async">')
    # Triptych: riktige alt-tekster og stedslinjer fra venues.json
    s = s.replace('alt="Kyllingburger fra Kverneriet Majorstua"', 'alt="Blå bar og grønne fløyelsbenker på Kverneriet Majorstua"')
    s = s.replace('alt="Uteserveringen på bryggekanten i Tønsberg"', 'alt="Bryggeterrassen til Kverneriet Tønsberg med kanalen bak"')
    for v in V['venues']:
        s = re.sub(r'(<a class="venue-panel" href="%s">.*?<span class="kv-eyebrow"><span class="glyph" aria-hidden="true">⋮</span> )[^<]*(</span>)' % re.escape(kv.url(v['slug'])),
                   lambda m: m.group(1) + e(f'{v["address"]["street"]}, {v["city"]} · {v["tagline"].split(" - ")[-1]}') + m.group(2), s, count=1, flags=re.S)
    # Om-seksjon før «Slik jobber vi», FAQ før gavekort
    s = re.sub(r'  <!-- Om Kverneriet -->\n  <section class="section" id="om">.*?\n  </section>\n\n', '', s, count=1, flags=re.S)
    s = s.replace('  <section class="section">\n    <div class="wrap">\n      <header class="sec-head">\n        <div class="sec-head__rule"></div>\n        <span class="kv-eyebrow" data-i18n="home.craftEyebrow">',
                  about_section() + '  <section class="section">\n    <div class="wrap">\n      <header class="sec-head">\n        <div class="sec-head__rule"></div>\n        <span class="kv-eyebrow" data-i18n="home.craftEyebrow">', 1)
    s = re.sub(r'  <section class="section[^"]*" id="faq">.*?\n  </section>\n', '', s, count=1, flags=re.S)
    s = s.replace('\n</main>', '\n' + faq.section(faq.general_faq()) + '</main>', 1)
    s = s.replace('<html lang="no">', '<html lang="nb">')
    s = add_gen_script(s)
    s = s.replace('<span class="kv-eyebrow"><span class="glyph" aria-hidden="true">⋮</span> Awesome food for awesome people since 2013</span>', '<span class="kv-eyebrow" lang="en"><span class="glyph" aria-hidden="true">⋮</span> Awesome food for awesome people since 2013</span>')
    s = s.replace('<h1>Flipping kick-ass burgers</h1>', '<h1 lang="en">Flipping kick-ass burgers</h1>')
    s = s.replace('<span class="kv-eyebrow">Stay safe - eat home</span>', '<span class="kv-eyebrow" lang="en">Stay safe - eat home</span>')
    open('index.html', 'w', encoding='utf-8').write(s); print('index.html ok')

def patch_takeaway():
    s = open('takeaway/index.html', encoding='utf-8').read()
    s = chrome.apply(s); s = modal.apply(s)
    s = s.replace('<main>', '<main id="main">', 1)
    s = s.replace('<span class="badge">Best take-away burger</span>', '<span class="badge" lang="en">Best take-away burger</span>')
    s = re.sub(r'<h1 class="hero-title"([^>]*)>Take-?away</h1>', r'<h1 class="hero-title"\1>Take-away burger i Oslo og Tønsberg</h1>', s)
    s = s.replace('style="object-position:center 68%"><div class="hero-dark__scrim"', 'style="object-position:center 68%" fetchpriority="high" decoding="async"><div class="hero-dark__scrim"', 1)
    # Bestillingskanalene fra venues.json (nb-Wolt, rel=noopener)
    s = re.sub(r'        <div class="stack-5">\n          <div class="order-group" id="majorstua">.*?\n          <p class="caption" data-i18n="modal.note">',
               lambda m: '        <div class="stack-5">\n          ' + '\n          '.join(modal.order_group(v['slug']).replace('<div class="order-group" data-venue=', '<div class="order-group" id="%s" data-venue=' % v['slug']) for v in V['venues']) + '\n          <p class="caption" data-i18n="modal.note">', s, count=1, flags=re.S)
    s = s.replace('<div class="kv-eyebrow" style="margin-bottom:var(--space-4)" data-i18n="v.orderTitle">Bestill take-away</div>', '<h2 class="display-4" style="margin-bottom:var(--space-4)" data-i18n="v.orderTitle">Bestill take-away</h2>', 1)
    s = re.sub(r'  <section class="section[^"]*" id="faq">.*?\n  </section>\n', '', s, count=1, flags=re.S)
    s = s.replace('\n</main>', '\n' + faq.section(faq.takeaway_faq()) + '</main>', 1)
    s = s.replace('<html lang="no">', '<html lang="nb">')
    s = add_gen_script(s)
    # Restaurantnavnene i bestillingskortet lenker til restaurantsidene
    for v in V['venues']:
        label = f'{v["name"]}, {v["city"]}' if v['city'] != v['name'] else v['name']
        s = s.replace(f'<div class="order-group" id="{v["slug"]}" data-venue="{v["slug"]}"><div class="kv-eyebrow">{label}</div>', f'<div class="order-group" id="{v["slug"]}" data-venue="{v["slug"]}"><div class="kv-eyebrow"><a href="{kv.url(v["slug"])}">{label}</a></div>')
    s = s.replace('<button class="btn btn--primary btn--lg" type="button" data-order-open data-track="cta:takeaway" data-i18n="act.order">Bestill take-away</button>', '<a class="btn btn--primary btn--lg" href="#majorstua" data-order-open data-track="cta:takeaway" data-i18n="act.order">Bestill take-away</a>')
    open('takeaway/index.html', 'w', encoding='utf-8').write(s); print('takeaway/index.html ok')

def build_404():
    """404.html (GitHub Pages og de fleste verter plukker den opp automatisk)."""
    G.add('nf.title', 'Fant ikke siden', 'Page not found'); G.add('nf.body', 'Adressen finnes ikke lenger, eller den er skrevet feil. Restaurantene, menyene og booking finner du her:', 'That address no longer exists, or it was mistyped. The restaurants, menus and booking are here:')
    links = ''.join(f'<a class="btn btn--outline btn--md" href="{kv.url(v["slug"])}">{e(v["fullName"])}</a>' for v in V['venues'])
    html = f'''<!DOCTYPE html>
<html lang="nb">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fant ikke siden – Kverneriet</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/assets/icons/icon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/styles.css">
<link rel="stylesheet" href="/site.css">
<script src="/content/i18n.js" defer></script>
<script src="/content/i18n-gen.js" defer></script>
<script src="/site.js" defer></script>
</head>
<body>

{chrome.header()}
<main id="main">
  <section class="section">
    <div class="wrap wrap--narrow">
      <header class="sec-head"><div class="sec-head__rule"></div><span class="kv-eyebrow">404</span><h1 class="display-2" data-i18n="nf.title">Fant ikke siden</h1></header>
      <p class="lede" style="margin-top:var(--space-5)" data-i18n="nf.body">Adressen finnes ikke lenger, eller den er skrevet feil. Restaurantene, menyene og booking finner du her:</p>
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:var(--space-6)">{links}<a class="btn btn--outline btn--md" href="/meny/" data-i18n="act.menu">Meny</a><a class="btn btn--primary btn--md" href="/majorstua/#booking" data-book-open data-i18n="act.book">Book bord</a></div>
    </div>
  </section>
</main>

{chrome.footer()}
{modal.MODAL}
</body>
</html>
'''
    open('404.html', 'w', encoding='utf-8').write(html); print('404.html ok')

def build_css():
    """Én CSS-fil (tokens + site.css) i stedet for en @import-kjede; Google Fonts lastes fra <head>."""
    css = ''
    for m in re.findall(r'@import url\("([^"?]+)', open('styles.css', encoding='utf-8').read()):
        c = open(m, encoding='utf-8').read()
        c = re.sub(r'@import url\("https://fonts\.googleapis\.com[^"]*"\);\n?', '', c)
        css += f'/* --- {m} --- */\n' + c + '\n'
    css += '/* --- site.css --- */\n' + open('site.css', encoding='utf-8').read()
    open('kverneriet.css', 'w', encoding='utf-8').write(css)
    return hashlib.md5(css.encode()).hexdigest()[:8]

def cache_bust():
    h = build_css()
    js = hashlib.md5(b''.join(open(f, 'rb').read() for f in ['site.js', 'meny.js', 'content/i18n.js', 'content/i18n-gen.js', 'content/menus.js'])).hexdigest()[:8]
    for f in kv.all_files() + ['404.html']:
        if not os.path.exists(f): continue
        s = open(f, encoding='utf-8').read()
        s = re.sub(r'<link rel="stylesheet" href="/styles\.css[^"]*">\n<link rel="stylesheet" href="/site\.css[^"]*">', f'<link rel="stylesheet" href="/kverneriet.css?v={h}">', s)
        s = re.sub(r'href="/kverneriet\.css\?v=[0-9a-f]+"', f'href="/kverneriet.css?v={h}"', s)
        s = re.sub(r'src="(/site\.js|/meny\.js|/content/i18n\.js|/content/i18n-gen\.js|/content/menus\.js)(\?v=[0-9a-z]+)?"', lambda m: f'src="{m.group(1)}?v={js}"', s)
        open(f, 'w', encoding='utf-8').write(s)
    print(f'css v={h} js v={js}')

if __name__ == '__main__':
    print('== sider'); build_venue.build(); build_menu.build(); build_landing.build(); patch_index(); patch_takeaway(); build_404()
    print('== presse'); subprocess.run([sys.executable, 'tools/media.py'], check=True); subprocess.run([sys.executable, 'tools/press.py'], check=True)
    print('== bilder'); images.apply_all(images.build_variants())
    print('== oversettelser'); print(G.write(), 'genererte nøkler')
    print('== head'); seo_head.apply_all(); seo_head.sitemap(); seo_head.llms(); seo_head.redirects(); seo_head.redirect_pages(); seo_head.robots(); seo_head.manifest()
    print('== css/js'); cache_bust()
    print('ferdig', datetime.datetime.now().strftime('%H:%M'))
