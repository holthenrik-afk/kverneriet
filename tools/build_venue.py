#!/usr/bin/env python3
"""Restaurantsidene (/majorstua/, /solli/, /tonsberg/) fra én mal + content/venues.json + content/menus.js.
Hver side har: hero med navn og sted, om-tekst, galleri, presse (media.py), booking (Zenchef + gruppeforespørsel),
praktisk info (åpningstider, adresse, kontakt, PDF-menyer), take-away-kanaler og FAQ – alt fra samme datakilde
som JSON-LD-en, så tekst og strukturerte data aldri spriker. Kjør: python3 tools/build.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv, chrome, modal, media as MD, faq, i18n_gen as G, pages
os.chdir(kv.ROOT)

V = kv.venues(); ORG = V['org']
e = kv.esc

COPY = {
 'majorstua': dict(
    heroSub=('Burgerrestaurant i Kirkeveien 64B på Majorstuen, Oslo – siden 2015.', 'Burger restaurant at Kirkeveien 64B, Majorstuen, Oslo – since 2015.'),
    slogan='Flipping kick-ass burgers',
    heroAlt='Spisesalen på Kverneriet Majorstua med grønne fløyelsbenker, blå bar og Aperol-plakater',
    about=[('Kverneriet Majorstua åpnet i 2015 i Kirkeveien 64B, tre minutter fra Majorstuen T-bane. Her har vi flippet håndlagde burgere siden: 150 gram kjøtt vi kverner selv av storfe i toppklasse, ferske brød og fries som tar tre dager å lage. Menyen har vokst sammen med gjestene – hot wings, ribs, salater, soft serve på Jersey-melk og milkshakes – men burgeren er fortsatt hjertet.',
            'Kverneriet Majorstua opened in 2015 at Kirkeveien 64B, three minutes from Majorstuen metro. We have been flipping handmade burgers here ever since: 150 grams of beef we grind ourselves from top-grade cattle, fresh buns and fries that take three days to make. The menu has grown with our guests – hot wings, ribs, salads, Jersey-milk soft serve and milkshakes – but the burger is still the heart of it.'),
           ('Lokalet har grønne fløyelsbenker, blå bar og plass til både en rask lunsj tirsdag–fredag fra 11 og lange kvelder: kjøkkenet serverer til 22, og baren holder åpent til 23 tirsdag–lørdag. Finansavisen ga oss 5 av 6 i 2026 og mener Kverneriet «bør spille en av hovedrollene på Oslos burgerscene».',
            'The room has green velvet booths, a blue bar and space for both a quick lunch Tuesday–Friday from 11 and long evenings: the kitchen serves until 22.00 and the bar stays open until 23.00 Tuesday–Saturday. Finansavisen gave us 5 out of 6 in 2026 and thinks Kverneriet “should play one of the lead roles on Oslo’s burger scene”.')],
    aboutImg=('/assets/img/majorstua-about.jpg', 'Bord, benker og plakater i spisesalen på Kverneriet Majorstua'),
    gallery=[('/assets/img/trio-majorstua.jpg', 'Blå bar og fløyelsbenker på Kverneriet Majorstua', '1/1'), ('/assets/img/g-burger.jpg', 'Servitør bærer to burgere på tallerkener', '1/1'),
             ('/assets/img/g-fries-herb.jpg', 'Trippelkokte fries med urter', '1/1'), ('/assets/img/g-patties.jpg', 'Grillede patties med smeltet blåmuggost', '1/1'),
             ('/assets/img/g-softserve-oreo.jpg', 'Soft serve med Oreo-smuler', '1/1'), ('/assets/img/g-toast.jpg', 'Toast fra menyen', '1/1'),
             ('/assets/img/g-tomatoes.jpg', 'Skivede tomater til burgerne', '1/1'), ('/assets/img/g-fries-truffle.jpg', 'Trøffelfries med parmesan', '1/1')],
 ),
 'solli': dict(
    heroSub=('Burgerrestaurant og cocktailbar ved Solli plass, Henrik Ibsens gate 100, Oslo – siden 2017.', 'Burger restaurant and cocktail bar at Solli plass, Henrik Ibsens gate 100, Oslo – since 2017.'),
    slogan='Your urban oasis',
    heroAlt='Spisesalen på Kverneriet Solli med korallrosa sofabenker og grønne fløyelsstoler',
    about=[('Kverneriet Solli åpnet i 2017 i Henrik Ibsens gate 100, rett ved Solli plass mellom Frogner, Vika og Aker Brygge – en urban oase med uteservering, cocktailbar og de samme håndlagde burgerne som på Majorstua: kjøtt vi kverner selv, ferske brød og trippelkokte fries.',
            'Kverneriet Solli opened in 2017 at Henrik Ibsens gate 100, right by Solli plass between Frogner, Vika and Aker Brygge – an urban oasis with outdoor seating, a cocktail bar and the same handmade burgers as at Majorstua: beef we grind ourselves, fresh buns and triple-cooked fries.'),
           ('Dagbladet kåret take-awayen vår til «Oslos overlegent beste burger» med terningkast 6, og Finansavisen kaller Solli sentrums beste sted for å kombinere business og burger. Lunsj tirsdag–fredag fra 11.30, kjøkken til 22 og bar til 23 tirsdag–lørdag. Hent selv, eller få levert med Wolt og Foodora.',
            'Dagbladet named our take-away “Oslo’s best burger by far” with a 6/6 rating, and Finansavisen calls Solli the best place downtown to combine business and burgers. Lunch Tuesday–Friday from 11.30, kitchen until 22.00 and bar until 23.00 Tuesday–Saturday. Pick up, or get delivery with Wolt and Foodora.')],
    aboutImg=('/assets/img/solli-about.jpg', 'Uteserveringen til Kverneriet Solli ved Solli plass med parasoller og rottingstoler'),
    gallery=[('/assets/img/trio-solli.jpg', 'Korallrosa sofabenk og dekkede bord på Kverneriet Solli', '1/1'), ('/assets/img/meny-solli.jpg', 'Burger på marmorbord på Kverneriet Solli', '1/1'),
             ('/assets/img/ln-cocktail.jpg', 'Rød cocktail på marmorbaren', '1/1'), ('/assets/img/g-fries-truffle.jpg', 'Trøffelfries med parmesan', '1/1'),
             ('/assets/img/g-burger.jpg', 'Servitør bærer to burgere på tallerkener', '1/1'), ('/assets/img/g-softserve.jpg', 'Soft serve med karamell', '1/1')],
 ),
 'tonsberg': dict(
    heroSub=('Burgerrestaurant på Kaldnes brygge, Rambergveien 15, Tønsberg – der det startet i 2013.', 'Burger restaurant on Kaldnes brygge, Rambergveien 15, Tønsberg – where it all started in 2013.'),
    slogan='Kick-ass food since 2013',
    heroAlt='Uteserveringen til Kverneriet Tønsberg på Kaldnes brygge med utsikt over kanalen mot Tønsberg brygge',
    about=[('Kverneriet Tønsberg er der det hele startet i 2013: en liten burgersjappe som har vokst til en fullverdig restaurant på Kaldnes brygge, Rambergveien 15, med uteservering ved kanalen og utsikt mot Tønsberg brygge. Kjøttet kverner vi selv, friesene tar tre dager, og menyen er den bredeste av de tre – salater, ribs, wings og kyllingretter i tillegg til burgerne.',
            'Kverneriet Tønsberg is where it all started in 2013: a small burger joint that has grown into a full restaurant on Kaldnes brygge, Rambergveien 15, with outdoor seating by the canal looking across to Tønsberg brygge. We grind the beef ourselves, the fries take three days, and the menu is the broadest of the three – salads, ribs, wings and chicken dishes alongside the burgers.'),
           ('Tønsbergs Blad kalte det «ren nytelse» i 2020 og ga oss 5 av 6 i 2024, og i 2021 lå vi øverst på Tripadvisors liste over Tønsbergs beste restauranter. Kjøkkenet holder åpent til 22 tirsdag–lørdag, baren til 23. Lunsj torsdag–søndag fra 12. Take-away henter du selv – forhåndsbestill på OrderX.',
            'Tønsbergs Blad called it “pure pleasure” in 2020 and gave us 5 out of 6 in 2024, and in 2021 we topped Tripadvisor’s list of Tønsberg’s best restaurants. The kitchen is open until 22.00 Tuesday–Saturday, the bar until 23.00. Lunch Thursday–Sunday from 12.00. Take-away is pick-up – pre-order on OrderX.')],
    aboutImg=('/assets/img/tonsberg-about.jpg', 'Lunsjbord med salater, toast, eggs benedict og cocktails på Kverneriet Tønsberg'),
    gallery=[('/assets/img/trio-tonsberg.jpg', 'Bord på bryggeterrassen til Kverneriet Tønsberg med kanalen bak', '1/1'), ('/assets/img/meny-tonsberg.jpg', 'Burger med smeltet ost, jalapeño og paprika på Kverneriet Tønsberg', '1/1'),
             ('/assets/img/craft-pack.jpg', 'Kverneriets take-away-eske i naturmaterialer', '1/1'), ('/assets/img/g-burger.jpg', 'Servitør bærer to burgere på tallerkener', '1/1'),
             ('/assets/img/ln-beer.jpg', 'Øl tappes fra tappekrana i baren', '1/1'), ('/assets/img/craft-fries.jpg', 'Trippelkokte fries med trøffel og parmesan', '1/1')],
 ),
}

def day_label(days):
    key = 'd.' + '-'.join(d[:3].lower() for d in days)
    no = kv.day_range(days, 'no'); en = kv.day_range(days, 'en')
    return G.add(key, no[0].upper() + no[1:] + ':', en + ':'), no[0].upper() + no[1:] + ':'

def hours_block(v):
    rows = ''
    for h in v['hours']['kitchen']:
        key, lab = day_label(h['days'])
        rows += f'              <dt data-i18n="{key}">{lab}</dt><dd>{kv.hhmm(h["opens"])}–{kv.hhmm(h["closes"])}</dd>\n'
    bar = ''
    for h in v['hours']['bar']:
        key, lab = day_label(h['days'])
        bar += f'              <dt data-i18n="{key}">{lab}</dt><dd><span data-i18n="hours.until">til</span> {kv.hhmm(h["closes"])}</dd>\n'
    G.add('hours.until', 'til', 'until')
    lunch_en = faq.LUNCH_EN[v['slug']]
    G.add(f'{v["slug"]}.lunch', f'Lunsj serveres {v["lunch"]}. Hele menyen fra åpning.', f'Lunch is served {lunch_en}. Full menu from opening.')
    return f'''        <div class="stack-6" style="margin-top:var(--space-5)">
          <div class="hours">
            <div class="kv-eyebrow" style="margin-bottom:var(--space-3)" data-i18n="hours.kitchen">Kjøkkenet</div>
            <dl>
{rows}            </dl>
          </div>
          <div class="hours">
            <div class="kv-eyebrow" style="margin-bottom:var(--space-3)" data-i18n="hours.bar">Baren</div>
            <dl>
{bar}            </dl>
          </div>
          <p class="caption" data-i18n="{v['slug']}.lunch">Lunsj serveres {e(v['lunch'])}. Hele menyen fra åpning.</p>
        </div>'''

def page(v):
    s = v['slug']; c = COPY[s]; a = v['address']; p = pages.PAGES[s]
    G.add(f'{s}.heroSub', *c['heroSub'])
    for i, (no, en) in enumerate(c['about']): G.add(f'{s}.about{i+1}', no, en)
    G.add('v.welcome', 'Velkommen til', 'Welcome to'); G.add('v.faq', 'Spørsmål', 'FAQ'); G.add('v.takeaway', 'Take-away', 'Take-away')
    G.add('book.venueIntro', 'Book online for inntil {n} personer og få bekreftelse med en gang. Større grupper sender forespørsel her – vi svarer på e-post. Vi har også mange drop-in-bord.',
          'Book online for up to {n} guests with instant confirmation. Larger groups send a request here – we reply by e-mail. We also keep plenty of walk-in tables.')
    G.add('practical.pdfs', 'Menyer i PDF', 'PDF menus'); G.add('practical.drinks', 'Drikkemeny (PDF)', 'Drinks menu (PDF)'); G.add('practical.kids', 'Barnemeny (PDF)', 'Kids menu (PDF)')
    G.add('contact.emailNote', 'Spørsmål og henvendelser (booking gjøres online)', 'Questions and enquiries (bookings are made online)')
    media_items = [m for m in MD.MEDIA if m['venue'] in (s, 'generelt')]
    gallery = ''.join(f'        <figure class="photo" style="aspect-ratio:{r}"><img src="{src}" alt="{e(alt)}" loading="lazy"></figure>\n' for src, alt, r in c['gallery'])
    book_intro = G._D['no']['book.venueIntro'].replace('{n}', str(v['groupThreshold']))
    facebook = f'          <a class="btn btn--ghost btn--sm btn--block" href="{v["facebook"]}" target="_blank" rel="noopener">Facebook{(" – " + e(v["fullName"])) if v["facebook"] not in ORG["sameAs"][:1] else ""}</a>\n' if v.get('facebook') else ''
    since_key = G.add(f'{s}.since', f'{e(v["area"])}, {e(v["city"])} · siden {v["since"]}', f'{faq.AREA_EN[s]}, {e(v["city"])} · since {v["since"]}')
    html = f'''<!DOCTYPE html>
<html lang="nb">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(p['title'])}</title>
<meta name="description" content="{e(p['desc'])}">
<!-- seo:start -->
<!-- seo:end -->
<link rel="stylesheet" href="/styles.css">
<link rel="stylesheet" href="/site.css">
<script src="/content/i18n.js" defer></script>
<script src="/content/i18n-gen.js" defer></script>
<script src="/site.js" defer></script>
</head>
<body data-venue="{s}">

{chrome.header(active=s, menu_href=kv.url(s + '-menu'))}
<!-- Undermeny for restauranten -->
<nav class="section-nav" aria-label="{e(v['name'])}" data-scrollspy>
  <ul>
    <li><a href="#about" data-i18n="v.about">Om</a></li>
    <li><a href="#gallery" data-i18n="v.gallery">Galleri</a></li>
    <li><a href="#booking" data-i18n="v.booking">Booking</a></li>
    <li><a href="#practical" data-i18n="v.practical">Praktisk info</a></li>
    <li><a href="#faq" data-i18n="v.faq">Spørsmål</a></li>
    <li><a href="{kv.url(s + '-menu')}" data-i18n="act.menu">Meny</a></li>
  </ul>
</nav>

<main id="main">

  <!-- Hero — den ene mørke seksjonen på siden -->
  <section class="hero-dark hero-dark--venue">
    <img class="hero-dark__img" src="{p['img']}" alt="{e(c['heroAlt'])}" fetchpriority="high" decoding="async"><div class="hero-dark__scrim" aria-hidden="true"></div>
    <div class="hero-dark__content">
      <span class="kv-eyebrow" data-i18n="{since_key}">{e(v['area'])}, {e(v['city'])} · siden {v['since']}</span>
      <h1 class="hero-title" style="margin-top:var(--space-3);max-width:14ch">{e(v['fullName'])}</h1>
      <p class="hero-sub" data-i18n="{s}.heroSub">{e(c['heroSub'][0])}</p>
      <p class="kv-eyebrow hero-slogan" lang="en">{e(c['slogan'])}</p>
      <div style="display:flex;gap:12px;margin-top:var(--space-6);flex-wrap:wrap">
        <a class="btn btn--primary btn--lg" href="#booking" data-book-open data-book-venue="{s}" data-track="cta:book:{s}" data-i18n="act.book">Book bord</a>
        <a class="btn btn--paper btn--lg" href="{kv.url(s + '-menu')}" data-i18n="act.seeMenu">Se menyen</a>
        <button class="btn btn--ghost btn--lg" type="button" data-order-open data-track="cta:takeaway:{s}" data-i18n="act.order">Bestill take-away</button>
      </div>
    </div>
  </section>

  <!-- Om -->
  <section class="section" id="about">
    <div class="wrap grid-2">
      <div>
        <header class="sec-head">
          <div class="sec-head__rule"></div>
          <span class="kv-eyebrow" data-i18n="v.welcome">Velkommen til</span>
          <h2 class="display-2">{e(v['fullName'])}{(', ' + e(v['city'])) if v['city'] != v['name'] else ''}</h2>
        </header>
        <p class="lede" style="margin-top:var(--space-5)" data-i18n="{s}.about1">{e(c['about'][0][0])}</p>
        <p style="margin-top:var(--space-4)" data-i18n="{s}.about2">{e(c['about'][1][0])}</p>
        <div style="margin-top:var(--space-6);display:flex;gap:10px;flex-wrap:wrap">
          <a class="btn btn--outline btn--md" href="{kv.url(s + '-menu')}" data-i18n="v.menuCta">Se hele menyen</a>
          <a class="btn btn--ghost btn--md" href="/lunsj/" data-i18n="lp.lunch">Lunsj</a>
          <a class="btn btn--ghost btn--md" href="/selskap/" data-i18n="lp.groups">Selskap og grupper</a>
        </div>
      </div>
      <figure class="photo" style="aspect-ratio:4/3"><img src="{c['aboutImg'][0]}" alt="{e(c['aboutImg'][1])}" loading="lazy"></figure>
    </div>
  </section>

  <!-- Galleri -->
  <section class="section section--flush-top" id="gallery">
    <div class="wrap">
      <div class="divider"><span data-i18n="v.gallery">Galleri</span></div>
      <div class="gallery-grid" style="margin-top:var(--space-5)">
{gallery}      </div>
    </div>
  </section>

{MD.section(media_items)}
  <!-- Booking -->
  <section class="section section--tint" id="booking">
    <div class="wrap booking-grid">
      <div>
        <header class="sec-head">
          <div class="sec-head__rule"></div>
          <span class="kv-eyebrow" data-i18n="book.eyebrow">Bord til to?</span>
          <h2 class="display-3" data-i18n="book.title">Book bord</h2>
        </header>
        <p class="lede" style="margin-top:var(--space-5)" data-i18n="book.venueIntro" data-i18n-n="{v['groupThreshold']}">{e(book_intro)}</p>
        <p class="caption" style="margin-top:var(--space-4)"><a href="{modal.zenchef_url(s)}" target="_blank" rel="noopener" data-i18n="book.openWindow">Åpne online booking i eget vindu</a></p>
      </div>
      <div class="card card--pad-lg">
        {modal.booking_form('p', False, venue=s)}
      </div>
    </div>
  </section>

  <!-- Praktisk -->
  <section class="section" id="practical">
    <div class="wrap practical-grid">
      <div>
        <header class="sec-head">
          <div class="sec-head__rule"></div>
          <h2 class="display-3" data-i18n="hours.title">Åpningstider</h2>
        </header>
{hours_block(v)}
      </div>

      <div class="card">
        <h3 class="display-4" data-i18n="addr.title">Adresse</h3>
        <div class="kv-eyebrow" style="margin-top:var(--space-4)">{e(v['fullName'])}</div>
        <p style="margin-top:var(--space-2)">{e(a['street'])}<br>{a['postalCode']} {e(a['city'])}</p>
        <div class="stack-2" style="margin-top:var(--space-5)">
          <a class="btn btn--outline btn--sm btn--block" href="{v['maps']['google']}" target="_blank" rel="noopener"><span class="btn__glyph" aria-hidden="true">➼</span> Google Maps</a>
          <a class="btn btn--outline btn--sm btn--block" href="{v['maps']['apple']}" target="_blank" rel="noopener"><span class="btn__glyph" aria-hidden="true">➼</span> Apple Maps</a>
        </div>
      </div>

      <div class="card">
        <h3 class="display-4" data-i18n="contact.title">Kontakt</h3>
        <div class="stack-2" style="margin-top:var(--space-4)">
          <a class="btn btn--ghost btn--sm btn--block" href="tel:{ORG['telephone']}">{ORG['telephoneDisplay']}</a>
          <a class="btn btn--ghost btn--sm btn--block" href="mailto:{v['email']}">{v['email']}</a>
          <p class="caption" data-i18n="contact.emailNote">Spørsmål og henvendelser (booking gjøres online)</p>
{facebook}        </div>
        <h3 class="display-4" style="margin-top:var(--space-5)" data-i18n="practical.pdfs">Menyer i PDF</h3>
        <div class="stack-2" style="margin-top:var(--space-3)">
          <a class="btn btn--ghost btn--sm btn--block" href="{v['menuPdf']['drinks']}" target="_blank" rel="noopener" data-i18n="practical.drinks">Drikkemeny (PDF)</a>
          <a class="btn btn--ghost btn--sm btn--block" href="{v['menuPdf']['kids']}" target="_blank" rel="noopener" data-i18n="practical.kids">Barnemeny (PDF)</a>
        </div>
      </div>
    </div>
  </section>

  <!-- Take-away -->
  <section class="section section--tint" id="order">
    <div class="wrap grid-2 grid-2--start">
      <div>
        <header class="sec-head">
          <div class="sec-head__rule"></div>
          <span class="kv-eyebrow" lang="en">Stay safe - eat home</span>
          <h2 class="display-3" data-i18n="v.orderTitle">Bestill take-away</h2>
        </header>
        <p class="lede" style="margin-top:var(--space-5)" data-i18n="home.taBody">Vi tar take-away like seriøst som maten vi serverer i restauranten. Er det Norges beste take-away-burger? Noen mener det - vi lar deg avgjøre.</p>
        <p style="margin-top:var(--space-4)"><a href="/takeaway/" data-i18n="ta.more">Les mer om take-away og emballasjen vår</a></p>
      </div>
      <div class="card">
        {modal.order_group(s)}
        <div style="margin-top:var(--space-4)">{modal.delivery_note(s)}</div>
      </div>
    </div>
  </section>

{faq.section(faq.venue_faq(v))}
</main>

{chrome.footer(menu_href=kv.url(s + '-menu'))}
{modal.MODAL}
</body>
</html>
'''
    G.add('ta.more', 'Les mer om take-away og emballasjen vår', 'More about take-away and our packaging')
    return html

def build():
    for v in V['venues']:
        kv.write(v['slug'], page(v)); print(kv.path(v['slug']), 'ok')

if __name__ == '__main__':
    build(); G.write()
