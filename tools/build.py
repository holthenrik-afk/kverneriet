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
import kv, chrome, modal, faq, carousel, i18n_gen as G, pages
import build_venue, build_menu, build_landing, build_blog, images, seo_head
import media as MD
os.chdir(kv.ROOT)

V = kv.venues(); ORG = V['org']
e = kv.esc

def cta_section():
    """Heldekkende bånd: «Om Kverneriet – Det startet i Tønsberg».

    Båndet hadde ingen overskrift, bare en ingress og en knapp, så det sa ikke
    hva det handlet om (ønske fra Kverneriet 22.10.2026). Tittelen kommer fra
    aboutTitle i Sanity, og «Les mer» går til /om/.
    """
    sc = kv.site_copy()
    hl = sc.get('heroLede') or {}
    if hl.get('no'): G.add('home.lede', hl['no'], hl.get('en') or hl['no'])
    t = sc.get('aboutTitle') or {'no': 'Det startet i Tønsberg', 'en': 'It started in Tønsberg'}
    G.add('home.aboutEyebrow', 'Om Kverneriet', 'About Kverneriet')
    G.add('home.aboutTitle', t['no'], t.get('en') or t['no'])
    G.add('act.aboutMore', 'Les mer om Kverneriet', 'More about Kverneriet')
    # majorstua-about.jpg kan ikke brukes: den har lesbare Aperol- og Fernet-Branca-plakater
    # på veggen og en hylle med spritflasker. Tønsberg-interiøret er rent, og passer dessuten
    # til «Det startet i Tønsberg».
    G.add('home.ctaAlt', 'Spisesalen på Kverneriet Tønsberg', 'The dining room at Kverneriet Tønsberg')
    return f"""  <section class="cta-band">
    <img class="cta-band__img" src="/assets/img/hero-julebord.jpg" alt="{e(G._D['no']['home.ctaAlt'])}" loading="lazy" decoding="async">
    <div class="cta-band__scrim" aria-hidden="true"></div>
    <div class="cta-band__inner wrap">
      <header class="sec-head sec-head--invert sec-head--center">
        <div class="sec-head__rule"></div>
        <span class="kv-eyebrow" data-i18n="home.aboutEyebrow">Om Kverneriet</span>
        <h2 class="display-2" data-i18n="home.aboutTitle">{e(t['no'])}</h2>
      </header>
      <p class="lede" data-i18n="home.lede">{e(G._D['no']['home.lede'])}</p>
      <div class="band-cta">
        <button class="btn btn--primary btn--lg" type="button" data-book-open data-track="cta:band:book" data-i18n="act.book">Book bord</button>
        <a class="btn btn--paper btn--lg" href="{kv.url('om')}" data-track="cta:band:om" data-i18n="act.aboutMore">Les mer om Kverneriet</a>
      </div>
    </div>
  </section>
"""


def takeaway_section():
    """«Ta Kverneriet med hjem» – take-away hadde ingen plass på forsiden i det hele tatt.

    Egen seksjon, ikke bare et kort i karusellen, fordi det er en egen inntektskanal
    (ønske fra Kverneriet 22.10.2026).
    """
    G.add('home.taEyebrow', 'Take-away på ordentlig', 'Take-away done properly')
    G.add('home.taTitle', 'Ta Kverneriet med hjem', 'Take Kverneriet home')
    G.add('home.taBody',
          'Samme burgere og samme tre dagers fries som i restauranten. Hent selv på '
          'Majorstua, Solli eller i Tønsberg, eller få levert med Wolt og Foodora i Oslo. '
          'Emballasjen har vi designet fra bunnen av, så maten kommer fram slik den '
          'forlot kjøkkenet.',
          'The same burgers and the same three-day fries as in the restaurant. Pick up at '
          'Majorstua, Solli or Tønsberg, or get it delivered with Wolt and Foodora in Oslo. '
          'We designed the packaging from scratch, so the food arrives the way it left the kitchen.')
    # ta-band.jpg er stående 2:3 og blir hardt beskåret i et bredt bånd; hero-takeaway er 16:9.
    G.add('home.taAlt', 'Person med take-away-pose fra Kverneriet på gaten',
          'Someone carrying a Kverneriet take-away bag down the street')
    G.add('act.seeTakeaway', 'Se take-away-menyen', 'See the take-away menu')
    # Tre bilder som krysstoner bak tonelaget. Bare det første har alt-tekst – de to
    # andre er dekorasjon av samme budskap, og tre like alt-tekster ville bare blitt
    # støy i en skjermleser. Krysstoningen står stille for den som har bedt om mindre
    # bevegelse i systemet (prefers-reduced-motion), og da vises det første bildet.
    bilder = [('ta-gate.jpg', G._D['no']['home.taAlt']),
              ('ta-pakking.jpg', ''),
              ('ta-emballasje.jpg', '')]
    lag = '\n    '.join(
        f'<img class="cta-band__img{" cta-band__img--fade" if i else ""}" style="--kv-fade:{i}"'
        f' src="/assets/img/{f}" alt="{e(a)}"{"" if a else " aria-hidden=\"true\""}'
        f' loading="lazy" decoding="async">'
        for i, (f, a) in enumerate(bilder))
    return f"""  <section class="cta-band cta-band--skifte">
    {lag}
    <div class="cta-band__scrim" aria-hidden="true"></div>
    <div class="cta-band__inner wrap">
      <header class="sec-head sec-head--invert sec-head--center">
        <div class="sec-head__rule"></div>
        <span class="kv-eyebrow" data-i18n="home.taEyebrow">Take-away på ordentlig</span>
        <h2 class="display-2" data-i18n="home.taTitle">Ta Kverneriet med hjem</h2>
      </header>
      <p class="lede" data-i18n="home.taBody">{e(G._D['no']['home.taBody'])}</p>
      <div class="band-cta">
        <button class="btn btn--primary btn--lg" type="button" data-order-open data-track="cta:ta:order" data-i18n="act.order">Bestill take-away</button>
        <a class="btn btn--paper btn--lg" href="{kv.url('takeaway')}" data-track="cta:ta:side" data-i18n="act.seeTakeaway">Se take-away-menyen</a>
      </div>
    </div>
  </section>
"""


def giftcard_section():
    """Gavekort – den kampanjen som har solgt best, men som ikke sto på forsiden."""
    ORG = kv.venues()['org']
    G.add('home.gcEyebrow', 'Hele året', 'All year round')
    G.add('home.gcTitle', 'Gavekort', 'Gift cards')
    G.add('home.gcBody',
          'Et måltid noen faktisk gleder seg til. Gavekortet gjelder på alle tre '
          'restaurantene, og kommer på e-post med en gang det er kjøpt.',
          'A meal someone actually looks forward to. The gift card works at all three '
          'restaurants and arrives by email as soon as it is bought.')
    # Emballasjebildet lå her før, men det viser take-away – og sto rett under
    # take-away-båndet. Et gavekort selges på måltidet, ikke på esken.
    G.add('home.gcAlt', 'To burgere på tallerken, båret ut i restauranten',
          'Two burgers on plates, carried out into the restaurant')
    G.add('act.buyGiftcard', 'Kjøp gavekort', 'Buy a gift card')
    return f"""  <section class="section section--accent" id="gavekort">
    <div class="wrap">
      <div class="grid-2 grid-2--start sidestilt">
        <figure class="photo sidestilt__bilde" style="aspect-ratio:4/3"><img src="/assets/img/g-burger.jpg" alt="{e(G._D['no']['home.gcAlt'])}" loading="lazy" decoding="async"></figure>
        <div>
          <header class="sec-head">
            <div class="sec-head__rule"></div>
            <span class="kv-eyebrow" data-i18n="home.gcEyebrow">Hele året</span>
            <h2 class="display-2" data-i18n="home.gcTitle">Gavekort</h2>
          </header>
          <p class="lede" style="margin-top:var(--space-5)" data-i18n="home.gcBody">{e(G._D['no']['home.gcBody'])}</p>
          <div class="band-cta">
            <a class="btn btn--solid btn--lg" href="{ORG['giftcard']}?utm_source=kverneriet.no&amp;utm_medium=forside&amp;utm_campaign=gavekort" target="_blank" rel="noopener" data-track="cta:gavekort" data-i18n="act.buyGiftcard">Kjøp gavekort</a>
          </div>
        </div>
      </div>
    </div>
  </section>
"""


def locations_section():
    """Restaurantene som egen seksjon igjen (Viktors punkt 6)."""
    G.add('home.locEyebrow', 'Tre steder', 'Three places')
    G.add('home.locTitle', 'Restaurantene', 'The restaurants')
    trio = TRIO_HTML
    for v in kv.venues()['venues']:
        sl = v['copy']['slogan']
        sl = sl if isinstance(sl, dict) else {'no': sl, 'en': sl}
        place = f'{v["address"]["street"]}, {v["city"]} · '
        # Egen i18n-nøkkel per kort, så slagordet bytter språk (adressen gjør den ikke)
        G.add(f'home.card.{v["slug"]}', place + sl['no'].rstrip('.'), place + sl['en'].rstrip('.'))
        line = f'<span data-i18n="home.card.{v["slug"]}">{e(place + sl["no"].rstrip("."))}</span>'
        pat = r'(<a class="venue-panel" href="%s">.*?<span class="kv-eyebrow"><span class="glyph" aria-hidden="true">⋮</span> )(?:<span data-i18n="home\.card\.[a-z]+">[^<]*</span>|[^<]*)(</span>)' % re.escape(kv.url(v['slug']))
        trio, n = re.subn(pat, lambda m: m.group(1) + line + m.group(2), trio, count=1, flags=re.S)
        if n != 1: raise SystemExit(f'venue-panel {v["slug"]}: {n} treff')
    return ('  <section class="section section--flush-top" id="locations">\n    <div class="wrap">\n'
            '      <header class="sec-head"><div class="sec-head__rule"></div>'
            '<span class="kv-eyebrow" data-i18n="home.locEyebrow">Tre steder</span>'
            '<h2 class="display-2" data-i18n="home.locTitle">Restaurantene</h2></header>\n'
            + trio +
            '    </div>\n  </section>\n')


TRIO_HTML = """      <div class="venue-trio" style="margin-top:var(--space-7)">
        <a class="venue-panel" href="/majorstua/">
          <figure class="photo" style="aspect-ratio:3/4"><picture><source type="image/webp" srcset="/assets/img/r/trio-majorstua-480.webp 480w, /assets/img/r/trio-majorstua-800.webp 800w, /assets/img/r/trio-majorstua-1200.webp 1200w, /assets/img/r/trio-majorstua-1400.webp 1400w" sizes="(max-width:760px) 100vw, 50vw"><img alt="Blå bar og grønne fløyelsbenker på Kverneriet Majorstua" loading="lazy" src="/assets/img/r/trio-majorstua-1200.jpg" srcset="/assets/img/r/trio-majorstua-480.jpg 480w, /assets/img/r/trio-majorstua-800.jpg 800w, /assets/img/r/trio-majorstua-1200.jpg 1200w, /assets/img/r/trio-majorstua-1400.jpg 1400w" sizes="(max-width:760px) 100vw, 50vw" width="1400" height="2086"></picture></figure>
          <h3 class="display-3">Majorstua</h3>
          <span class="kv-eyebrow"><span class="glyph" aria-hidden="true">⋮</span> <span data-i18n="home.card.majorstua">Kirkeveien 64B, Oslo · Burger, bar og nabolagsstemning</span></span>
          <span class="venue-panel__cta" data-i18n="act.explore">Utforsk</span>
        </a>
        <a class="venue-panel" href="/solli/">
          <figure class="photo" style="aspect-ratio:3/4"><picture><source type="image/webp" srcset="/assets/img/r/trio-solli-480.webp 480w, /assets/img/r/trio-solli-800.webp 800w, /assets/img/r/trio-solli-1200.webp 1200w, /assets/img/r/trio-solli-1400.webp 1400w" sizes="(max-width:760px) 100vw, 50vw"><img alt="Spisesalen på Kverneriet Solli" loading="lazy" src="/assets/img/r/trio-solli-1200.jpg" srcset="/assets/img/r/trio-solli-480.jpg 480w, /assets/img/r/trio-solli-800.jpg 800w, /assets/img/r/trio-solli-1200.jpg 1200w, /assets/img/r/trio-solli-1400.jpg 1400w" sizes="(max-width:760px) 100vw, 50vw" width="1400" height="935"></picture></figure>
          <h3 class="display-3">Solli</h3>
          <span class="kv-eyebrow"><span class="glyph" aria-hidden="true">⋮</span> <span data-i18n="home.card.solli">Henrik Ibsens gate 100, Oslo · Fra lunsj til cocktails</span></span>
          <span class="venue-panel__cta" data-i18n="act.explore">Utforsk</span>
        </a>
        <a class="venue-panel" href="/tonsberg/">
          <figure class="photo" style="aspect-ratio:3/4"><picture><source type="image/webp" srcset="/assets/img/r/trio-tonsberg-480.webp 480w, /assets/img/r/trio-tonsberg-800.webp 800w, /assets/img/r/trio-tonsberg-1200.webp 1200w, /assets/img/r/trio-tonsberg-1400.webp 1400w" sizes="(max-width:760px) 100vw, 50vw"><img alt="Bryggeterrassen til Kverneriet Tønsberg med kanalen bak" loading="lazy" src="/assets/img/r/trio-tonsberg-1200.jpg" srcset="/assets/img/r/trio-tonsberg-480.jpg 480w, /assets/img/r/trio-tonsberg-800.jpg 800w, /assets/img/r/trio-tonsberg-1200.jpg 1200w, /assets/img/r/trio-tonsberg-1400.jpg 1400w" sizes="(max-width:760px) 100vw, 50vw" width="1400" height="2096"></picture></figure>
          <h3 class="display-3">T&oslash;nsberg</h3>
          <span class="kv-eyebrow"><span class="glyph" aria-hidden="true">⋮</span> <span data-i18n="home.card.tonsberg">Rambergveien 15, Tønsberg · Der det hele startet</span></span>
          <span class="venue-panel__cta" data-i18n="act.explore">Utforsk</span>
        </a>
      </div>
"""



# Stikkordene til «Slik jobber vi» ligger her og ikke i site-copy.json, fordi
# fetch_sanity.py bygger craftItems på nytt ved hver henting og bare kjenner
# image, alt, title og body. Et felt lagt i JSON-en ville vært slettet innen
# ti minutter. Nøkkelen er tittelen i små bokstaver: endrer Kverneriet tittelen
# i Sanity, forsvinner pillen i stedet for å vise feil faktum.
CRAFT_STIKKORD = {
    'kjøttet':           ('Kvernes her',     'Ground here'),
    'tre dagers fries':  ('Tre dager',       'Three days'),
    'soft serve deluxe': ('100 % Jersey',    '100% Jersey'),
    'baren':             ('Egen bar',        'Our own bar'),
    'folkene':           ('Siden 2013',      'Since 2013'),
    'emballasjen':       ('Naturmaterialer', 'Natural materials'),
}


def craft_section():
    """«Slik jobber vi» – samme karusell som de to andre på forsiden.

    Kortene peker ingen steder ennå (href=None), så de rendres som vanlige kort
    uten «Les mer». Innholdet redigeres fortsatt i Sanity.
    """
    sc = kv.site_copy()
    eb = sc.get('craftEyebrow') or {'no': 'Håndverk, ingen snarveier', 'en': 'Craft, not shortcuts'}
    ti = sc.get('craftTitle') or {'no': 'Slik jobber vi', 'en': 'The way we work'}
    G.add('home.craftEyebrow', eb['no'], eb.get('en') or eb['no']); G.add('home.craftTitle', ti['no'], ti.get('en') or ti['no'])

    items = []
    for i, it in enumerate(sc.get('craftItems') or []):
        kort = {'key': str(i), 'href': None, 'image': it['image'],
                'alt': {'no': it.get('alt', ''), 'en': it.get('alt', '')},
                'title': it['title'], 'sub': it['body']}
        s = CRAFT_STIKKORD.get(it['title']['no'].strip().lower())
        if s: kort['stikkord'] = {'no': s[0], 'en': s[1]}
        items.append(kort)

    return f'''  <!-- The craft -->
  <section class="section">
    <div class="wrap">
      <header class="sec-head">
        <div class="sec-head__rule"></div>
        <span class="kv-eyebrow" data-i18n="home.craftEyebrow">{e(eb['no'])}</span>
        <h2 class="display-2" data-i18n="home.craftTitle">{e(ti['no'])}</h2>
      </header>
      {carousel.track(items, 'craft', 'Slik jobber vi')}
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
    # Innrykket varierer med hvordan heroen er bygget, så regexen tar vare på det den fant.
    s, n = re.subn(r'( *)<h1( lang="en")?>[^<]*</h1>\n(?:[ \t]*<p class="hero-home__sub"[^\n]*\n)?',
               lambda m: f'{m.group(1)}<h1 lang="en">Handcrafted burgers</h1>\n'
                         f'{m.group(1)}<p class="hero-home__sub" data-i18n="home.heroSub">{e(hs["no"])}</p>\n',
               s, count=1)
    if n != 1: raise SystemExit('build: fant ikke h1 i heroen')
    s = re.sub(r'<p class="lede" data-i18n(?:-html)?="home\.lede(?:\.html)?">.*?</p>',
               f'<p class="lede" data-i18n="home.lede">{e(G._D["no"]["home.lede"])}</p>', s, count=1, flags=re.S)
    G.add('home.hoursNote', 'Åpningstider, meny og booking på hver restaurantside.', 'Opening hours, menu and booking on each restaurant page.')

    # Take-away hører ikke hjemme blant det første gjesten ser (ønske fra Kverneriet 24.09.2026)
    s = re.sub(r'\s*<button class="btn btn--solid btn--lg" type="button" data-order-open data-track="cta:takeaway"[^>]*>[^<]*</button>', '', s, count=1)
    # Triptych: riktige alt-tekster og stedslinjer fra venues.json
    s = s.replace('alt="Kyllingburger fra Kverneriet Majorstua"', 'alt="Blå bar og grønne fløyelsbenker på Kverneriet Majorstua"')
    s = s.replace('alt="Uteserveringen på bryggekanten i Tønsberg"', 'alt="Bryggeterrassen til Kverneriet Tønsberg med kanalen bak"')
    # Om-teksten inn i restaurant-seksjonen (#om), FAQ før gavekort
    s, n = re.subn(r'  <!-- story:start -->.*?  <!-- story:end -->', lambda m: '  <!-- story:start -->\n' + carousel.story_section().rstrip('\n') + '\n  <!-- story:end -->', s, count=1, flags=re.S)
    if n != 1: raise SystemExit('build: fant ikke story-markørene')
    s, n = re.subn(r'  <!-- cta:start -->.*?  <!-- cta:end -->', lambda m: '  <!-- cta:start -->\n' + cta_section().rstrip('\n') + '\n  <!-- cta:end -->', s, count=1, flags=re.S)
    if n != 1: raise SystemExit('build: fant ikke cta-markørene')
    s, n = re.subn(r'  <!-- locations:start -->.*?  <!-- locations:end -->', lambda m: '  <!-- locations:start -->\n' + locations_section().rstrip('\n') + '\n  <!-- locations:end -->', s, count=1, flags=re.S)
    if n != 1: raise SystemExit('build: fant ikke locations-markørene')
    s, n = re.subn(r'  <!-- anledninger:start -->.*?  <!-- anledninger:end -->', lambda m: '  <!-- anledninger:start -->\n' + carousel.occasions_section().rstrip('\n') + '\n  <!-- anledninger:end -->', s, count=1, flags=re.S)
    if n != 1: raise SystemExit('build: fant ikke anledninger-markørene')
    s, n = re.subn(r'  <!-- takeaway:start -->.*?  <!-- takeaway:end -->', lambda m: '  <!-- takeaway:start -->\n' + takeaway_section().rstrip('\n') + '\n  <!-- takeaway:end -->', s, count=1, flags=re.S)
    if n != 1: raise SystemExit('build: fant ikke takeaway-markørene')
    s, n = re.subn(r'  <!-- gavekort:start -->.*?  <!-- gavekort:end -->', lambda m: '  <!-- gavekort:start -->\n' + giftcard_section().rstrip('\n') + '\n  <!-- gavekort:end -->', s, count=1, flags=re.S)
    if n != 1: raise SystemExit('build: fant ikke gavekort-markørene')
    s = re.sub(r'  <!-- The craft -->\n  <section class="section">.*?\n  </section>\n\n', lambda m: craft_section(), s, count=1, flags=re.S)
    s = re.sub(r'  <section class="section[^"]*" id="faq">.*?\n  </section>\n', '', s, count=1, flags=re.S)
    s = s.replace('\n</main>', '\n' + faq.section(faq.general_faq()) + '</main>', 1)
    s = s.replace('<html lang="no">', '<html lang="nb">')
    s = add_gen_script(s)
    s = re.sub(r'<span class="kv-eyebrow"( lang="en")?><span class="glyph" aria-hidden="true">⋮</span> Awesome food for awesome people[^<]*</span>',
               '<span class="kv-eyebrow" lang="en"><span class="glyph" aria-hidden="true">⋮</span> Awesome food for awesome people</span>', s, count=1)
    # «Stay safe - eat home» er en korona-linje som ikke hører hjemme i tonefallet lenger (ønske fra Kverneriet 06.10.2026)
    s = re.sub(r'<span class="kv-eyebrow"(?: lang="en")?>Stay safe - eat home</span>',
               '<span class="kv-eyebrow" data-i18n="ta.eyebrow">Ta Kverneriet med hjem</span>', s)
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

def build_about():
    """/om/ – historien bak «Les mer om Kverneriet» i CTA-båndet.

    Teksten er de samme avsnittene som ligger i Sanity (aboutParagraphs), så
    Kverneriet redigerer den selv. Siden fantes ikke før knappen ble lagt til.
    """
    sc = kv.site_copy()
    meta = pages.PAGES['om']
    t = sc.get('aboutTitle') or {'no': 'Det startet i Tønsberg', 'en': 'It started in Tønsberg'}
    paras = sc.get('aboutParagraphs') or []
    G.add('om.eyebrow', 'Om Kverneriet', 'About Kverneriet')
    G.add('om.title', t['no'], t.get('en') or t['no'])

    # Alkoholreklame er forbudt i Norge, og Tønsberg har fått advarsler. Avsnittet som
    # markedsfører «cocktails vi er stolte av, et stort vinkart og et bredt utvalg øl»
    # slippes derfor ikke ut på denne siden. Teksten ligger i Sanity og må rettes der –
    # til da sier bygget fra om hva som ble holdt tilbake.
    SPERRE = ('cocktails vi er stolte av', 'stort vinkart', 'bredt utvalg øl')
    holdt = [p['no'] for p in paras if any(s in p['no'].lower() for s in SPERRE)]
    paras = [p for p in paras if not any(s in p['no'].lower() for s in SPERRE)]
    for h in holdt:
        print(f'  /om/: holdt tilbake avsnitt med alkoholreklame – «{h[:60]}…» (rett i Sanity)')
    if not paras:
        raise SystemExit('build: /om/ har ingen avsnitt å vise – sjekk aboutParagraphs')

    body = ''
    for i, para in enumerate(paras):
        G.add(f'om.p{i + 1}', para['no'], para.get('en') or para['no'])
        cls = ' class="lede"' if i == 0 else ''
        style = '' if i == 0 else ' style="margin-top:var(--space-5);color:var(--text-muted)"'
        body += f'          <p{cls}{style} data-i18n="om.p{i + 1}">{e(para["no"])}</p>\n'

    venues = ''.join(
        f'<a class="btn btn--outline btn--md" href="{kv.url(v["slug"])}">{e(v["fullName"])}</a>'
        for v in V['venues'])

    html = f'''<!DOCTYPE html>
<html lang="nb">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(meta['title'])}</title>
<meta name="description" content="{e(meta['desc'])}">
<!-- seo:start -->
<!-- seo:end -->
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
      <nav class="crumbs" aria-label="Brødsmuler"><ol><li><a href="/">Kverneriet</a></li><li><span aria-current="page">Om Kverneriet</span></li></ol></nav>
      <header class="sec-head">
        <div class="sec-head__rule"></div>
        <span class="kv-eyebrow" data-i18n="om.eyebrow">Om Kverneriet</span>
        <h1 class="display-1" data-i18n="om.title">{e(t['no'])}</h1>
      </header>
      <div style="margin-top:var(--space-6)">
{body}      </div>
    </div>
  </section>

  <section class="section section--flush-top">
    <div class="wrap">
      <figure class="photo" style="aspect-ratio:16/9"><img src="/assets/img/hero-julebord.jpg" alt="Spisesalen på Kverneriet Tønsberg" loading="lazy" decoding="async"></figure>
    </div>
  </section>

  <section class="section section--flush-top">
    <div class="wrap wrap--narrow">
      <header class="sec-head">
        <div class="sec-head__rule"></div>
        <span class="kv-eyebrow">Tre steder</span>
        <h2 class="display-2">Besøk oss</h2>
      </header>
      <div class="band-cta" style="margin-top:var(--space-5)">{venues}</div>
      <div class="band-cta" style="margin-top:var(--space-6)">
        <button class="btn btn--primary btn--lg" type="button" data-book-open data-track="lp:om:book" data-i18n="act.book">Book bord</button>
      </div>
    </div>
  </section>
</main>

{chrome.footer()}
{modal.MODAL}
</body>
</html>
'''
    kv.write('om', html)
    print(kv.path('om'), 'ok')


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
        s = chrome.add_pixel(s)
        s = chrome.add_tracking(s)
        open(f, 'w', encoding='utf-8').write(s)
    print(f'css v={h} js v={js}')

if __name__ == '__main__':
    print('== sider'); build_venue.build(); build_menu.build(); build_landing.build(); build_blog.build(); build_about(); patch_index(); patch_takeaway(); build_404()
    print('== presse'); subprocess.run([sys.executable, 'tools/media.py'], check=True); subprocess.run([sys.executable, 'tools/press.py'], check=True)
    print('== bilder'); images.apply_all(images.build_variants())
    print('== oversettelser'); print(G.write(), 'genererte nøkler')
    print('== head'); seo_head.apply_all(); seo_head.sitemap(); seo_head.llms(); seo_head.redirects(); seo_head.redirect_pages(); seo_head.robots(); seo_head.manifest()
    print('== css/js'); cache_bust()
    print('ferdig', datetime.datetime.now().strftime('%H:%M'))
