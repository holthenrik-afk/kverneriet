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

# Om-tekster, bilder og slagord per restaurant ligger i content/venues.json under «copy» (redigeres i Sanity).
def copy_of(v):
    c = v['copy']
    sl = c['slogan'] if isinstance(c['slogan'], dict) else {'no': c['slogan'], 'en': c['slogan']}
    return dict(heroSub=(c['heroSub']['no'], c['heroSub'].get('en') or c['heroSub']['no']), slogan=(sl['no'], sl.get('en') or sl['no']), heroAlt=c['heroImg']['alt'], heroImg=c['heroImg']['url'],
                about=[(c['about1']['no'], c['about1'].get('en') or c['about1']['no']), (c['about2']['no'], c['about2'].get('en') or c['about2']['no'])],
                aboutImg=(c['aboutImg']['url'], c['aboutImg']['alt']), gallery=[(g['url'], g['alt'], '1/1') for g in c['gallery']])

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
    s = v['slug']; c = copy_of(v); a = v['address']; p = pages.PAGES[s]
    G.add(f'{s}.heroSub', *c['heroSub']); G.add(f'{s}.slogan', *c['slogan'])
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
    <img class="hero-dark__img" src="{c['heroImg']}" alt="{e(c['heroAlt'])}" fetchpriority="high" decoding="async"><div class="hero-dark__scrim" aria-hidden="true"></div>
    <div class="hero-dark__content">
      <span class="kv-eyebrow" data-i18n="{since_key}">{e(v['area'])}, {e(v['city'])} · siden {v['since']}</span>
      <h1 class="hero-title" style="margin-top:var(--space-3);max-width:14ch">{e(v['fullName'])}</h1>
      <p class="hero-sub" data-i18n="{s}.heroSub">{e(c['heroSub'][0])}</p>
      <p class="kv-eyebrow hero-slogan" data-i18n="{s}.slogan">{e(c['slogan'][0])}</p>
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
