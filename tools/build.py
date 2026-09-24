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
import build_venue, build_menu, build_landing, build_blog, images, seo_head
import media as MD
os.chdir(kv.ROOT)

V = kv.venues(); ORG = V['org']
e = kv.esc

def about_section():
    """«Det startet i Tønsberg» – tittel og avsnitt fra content/site-copy.json (redigeres i Sanity)."""
    sc = kv.site_copy()
    t = sc.get('aboutTitle') or {'no': 'Det startet i Tønsberg', 'en': 'It started in Tønsberg'}
    paras = sc.get('aboutParagraphs') or []
    G.add('home.aboutEyebrow', 'Om Kverneriet', 'About Kverneriet'); G.add('home.aboutTitle', t['no'], t.get('en') or t['no'])
    body = ''
    for i, para in enumerate(paras):
        G.add(f'home.about{i + 1}', para['no'], para.get('en') or para['no'])
        cls = ' class="lede"' if i == 0 else ''
        style = '' if i == 0 else ' style="margin-top:var(--space-4);color:var(--text-muted)"'
        body += f'          <p{cls}{style} data-i18n="home.about{i + 1}">{e(para["no"])}</p>\n'
    return f'''      <!-- om:start -->
      <div class="grid-2 grid-2--start">
        <header class="sec-head">
          <div class="sec-head__rule"></div>
          <span class="kv-eyebrow" data-i18n="home.aboutEyebrow">Om Kverneriet</span>
          <h2 class="display-2" data-i18n="home.aboutTitle">{e(t['no'])}</h2>
        </header>
        <div>
{body}        </div>
      </div>
      <!-- om:end -->'''

def craft_section():
    """«Slik jobber vi» – kortene ligger i content/site-copy.json (craftItems) og redigeres i Sanity."""
    sc = kv.site_copy()
    eb = sc.get('craftEyebrow') or {'no': 'Håndverk, ingen snarveier', 'en': 'Craft, not shortcuts'}
    ti = sc.get('craftTitle') or {'no': 'Slik jobber vi', 'en': 'The way we work'}
    G.add('home.craftEyebrow', eb['no'], eb.get('en') or eb['no']); G.add('home.craftTitle', ti['no'], ti.get('en') or ti['no'])
    cards = ''
    for i, it in enumerate(sc.get('craftItems') or []):
        G.add(f'craft.{i}.t', it['title']['no'], it['title'].get('en') or it['title']['no'])
        G.add(f'craft.{i}.b', it['body']['no'], it['body'].get('en') or it['body']['no'])
        cards += (f'        <div class="venue-card">\n'
                  f'          <figure class="photo" style="aspect-ratio:1/1"><img src="{it["image"]}" alt="{e(it["alt"])}" loading="lazy"></figure>\n'
                  f'          <h3 class="display-4" data-i18n="craft.{i}.t">{e(it["title"]["no"])}</h3>\n'
                  f'          <p class="menu-item__desc" style="margin-top:0" data-i18n="craft.{i}.b">{e(it["body"]["no"])}</p>\n'
                  f'        </div>\n')
    return f'''  <!-- The craft -->
  <section class="section">
    <div class="wrap">
      <header class="sec-head">
        <div class="sec-head__rule"></div>
        <span class="kv-eyebrow" data-i18n="home.craftEyebrow">{e(eb['no'])}</span>
        <h2 class="display-2" data-i18n="home.craftTitle">{e(ti['no'])}</h2>
      </header>
      <div class="grid-3" style="margin-top:var(--space-7)">
{cards}      </div>
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
    sc = kv.site_copy()
    hs = sc.get('heroSub') or {'no': 'Burgerrestaurant i Oslo og Tønsberg siden 2013.', 'en': 'Burger restaurant in Oslo and Tønsberg since 2013.'}
    hl = sc.get('heroLede') or {}
    G.add('home.heroSub', hs['no'], hs.get('en') or hs['no'])
    if hl.get('no'): G.add('home.lede', hl['no'], hl.get('en') or hl['no'])
    G.add('home.hoursNote', 'Åpningstider, meny og booking på hver restaurantside.', 'Opening hours, menu and booking on each restaurant page.')
    s = re.sub(r'<h1( lang="en")?>[^<]*</h1>\n(    <p class="hero-home__sub"[^\n]*\n)?',
               f'<h1 lang="en">Handcrafted burgers</h1>\n    <p class="hero-home__sub" data-i18n="home.heroSub">{e(hs["no"])}</p>\n', s, count=1)
    s = re.sub(r'(<p class="lede" data-i18n="home.lede">)[^<]*(</p>)', lambda m: m.group(1) + e(G._D['no']['home.lede']) + m.group(2), s, count=1)
    # Take-away hører ikke hjemme blant det første gjesten ser (ønske fra Kverneriet 24.09.2026)
    s = re.sub(r'\s*<button class="btn btn--solid btn--lg" type="button" data-order-open data-track="cta:takeaway"[^>]*>[^<]*</button>', '', s, count=1)
    # Triptych: riktige alt-tekster og stedslinjer fra venues.json
    s = s.replace('alt="Kyllingburger fra Kverneriet Majorstua"', 'alt="Blå bar og grønne fløyelsbenker på Kverneriet Majorstua"')
    s = s.replace('alt="Uteserveringen på bryggekanten i Tønsberg"', 'alt="Bryggeterrassen til Kverneriet Tønsberg med kanalen bak"')
    for v in V['venues']:
        s = re.sub(r'(<a class="venue-panel" href="%s">.*?<span class="kv-eyebrow"><span class="glyph" aria-hidden="true">⋮</span> )[^<]*(</span>)' % re.escape(kv.url(v['slug'])),
                   lambda m: m.group(1) + e(f'{v["address"]["street"]}, {v["city"]} · {(v["copy"]["slogan"]["no"] if isinstance(v["copy"]["slogan"], dict) else v["copy"]["slogan"]).rstrip(".")}') + m.group(2), s, count=1, flags=re.S)
    # Om-teksten inn i restaurant-seksjonen (#om), FAQ før gavekort
    s = re.sub(r'      <!-- om:start -->.*?<!-- om:end -->', lambda m: about_section(), s, count=1, flags=re.S)
    s = re.sub(r'  <!-- The craft -->\n  <section class="section">.*?\n  </section>\n\n', lambda m: craft_section(), s, count=1, flags=re.S)
    s = re.sub(r'  <section class="section[^"]*" id="faq">.*?\n  </section>\n', '', s, count=1, flags=re.S)
    s = s.replace('\n</main>', '\n' + faq.section(faq.general_faq()) + '</main>', 1)
    s = s.replace('<html lang="no">', '<html lang="nb">')
    s = add_gen_script(s)
    s = re.sub(r'<span class="kv-eyebrow"( lang="en")?><span class="glyph" aria-hidden="true">⋮</span> Awesome food for awesome people[^<]*</span>',
               '<span class="kv-eyebrow" lang="en"><span class="glyph" aria-hidden="true">⋮</span> Awesome food for awesome people</span>', s, count=1)
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
    print('== sider'); build_venue.build(); build_menu.build(); build_landing.build(); build_blog.build(); patch_index(); patch_takeaway(); build_404()
    print('== presse'); subprocess.run([sys.executable, 'tools/media.py'], check=True); subprocess.run([sys.executable, 'tools/press.py'], check=True)
    print('== bilder'); images.apply_all(images.build_variants())
    print('== oversettelser'); print(G.write(), 'genererte nøkler')
    print('== head'); seo_head.apply_all(); seo_head.sitemap(); seo_head.llms(); seo_head.redirects(); seo_head.redirect_pages(); seo_head.robots(); seo_head.manifest()
    print('== css/js'); cache_bust()
    print('ferdig', datetime.datetime.now().strftime('%H:%M'))
