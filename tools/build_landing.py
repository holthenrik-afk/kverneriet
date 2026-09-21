#!/usr/bin/env python3
"""Landingssidene (/lunsj/, /julebord/, /selskap/, /late-night/) fra én mal. Header/footer fra chrome.py,
modal fra modal.py, mediekort fra media.py, FAQ fra faq.py, titler fra pages.py. Fakta (åpningstider,
pakker, priser) hentes fra content/venues.json så sidene aldri lover noe restaurantene ikke har.
Kjør: python3 tools/build.py"""
import os, sys, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv, chrome, modal, media as MD, faq, pages, i18n_gen as G
os.chdir(kv.ROOT)

V = kv.venues(); ORG = V['org']; PK = ORG['packages']
e = kv.esc
def vv(slug): return kv.venue(slug)

def page(p):
    slug = p['slug']; meta = pages.PAGES[slug]
    gallery = ''
    if p.get('gallery'):
        cells = ''.join(f'<figure class="photo" style="aspect-ratio:{g[2] if len(g) > 2 else "1/1"}"><img src="{g[0]}" alt="{e(g[1])}" loading="lazy"></figure>' for g in p['gallery'])
        gallery = f'''
  <section class="section section--flush-top">
    <div class="wrap"><div class="gallery-grid" style="grid-template-columns:repeat({len(p['gallery'])},1fr)">{cells}</div></div>
  </section>'''
    press = ('\n' + MD.section(MD.by_key(*p['media']))) if p.get('media') else ''
    facts = ''.join(
        f'<div class="upgrade-row"><span class="upgrade-row__glyph" aria-hidden="true">➼</span><span class="upgrade-row__body">'
        f'<span class="upgrade-row__name">{("<a href=\"" + f[2] + "\">" + e(f[0]) + "</a>") if len(f) > 2 and f[2] else e(f[0])}</span><span class="upgrade-row__note">{e(f[1])}</span></span></div>'
        for f in p['facts'])
    others = ''.join(f'<a class="btn btn--outline btn--sm" href="{kv.url(o)}" data-i18n="lp.{k}">{t}</a>' for o, k, t in p['others'])
    venues = ''.join(f'<a class="btn btn--ghost btn--sm" href="{kv.url(v["slug"])}">{e(v["fullName"])}</a>' for v in V['venues'])
    if p['cta'] == 'book':
        cta_primary = f'<a class="btn btn--primary btn--lg" href="/majorstua/#booking" data-book-open data-track="lp:{slug}:book" data-i18n="lp.bookNow">Book bord nå</a>'
    else:
        cta_primary = f'<a class="btn btn--primary btn--lg" href="/majorstua/#booking" data-book-open data-book-mode="large" data-track="lp:{slug}:group" data-i18n="lp.groupCta">Send gruppeforespørsel</a>'
    crumbs = f'<nav class="crumbs" aria-label="Brødsmuler"><ol><li><a href="/">Kverneriet</a></li><li><span aria-current="page">{e(p["crumb"])}</span></li></ol></nav>'
    G.add('lp.venues', 'Restaurantene', 'The restaurants')
    return f'''<!DOCTYPE html>
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

  <section class="hero-dark hero-dark--short">
    <img class="hero-dark__img" src="{meta['img']}" alt="{e(p['imgAlt'])}" fetchpriority="high" decoding="async"{(' style="object-position:' + p['pos'] + '"') if p.get('pos') else ''}><div class="hero-dark__scrim" aria-hidden="true"></div>
    <div class="hero-dark__content">
      <span class="kv-eyebrow">{e(p['eyebrow'])}</span>
      <h1 class="hero-title" style="margin-top:var(--space-3);max-width:16ch">{e(p['h1'])}</h1>
      <p class="hero-sub">{e(p['sub'])}</p>
      <div style="display:flex;gap:12px;margin-top:var(--space-6);flex-wrap:wrap">
        {cta_primary}
        <a class="btn btn--paper btn--lg" href="/meny/" data-i18n="act.seeMenu">Se menyen</a>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      {crumbs}
      <div class="grid-2 grid-2--start">
      <div>
        <header class="sec-head">
          <div class="sec-head__rule"></div>
          <span class="kv-eyebrow">{e(p['sec_eyebrow'])}</span>
          <h2 class="display-2">{e(p['h2'])}</h2>
        </header>
        {''.join(f'<p class="lede" style="margin-top:var(--space-5)">{t}</p>' for t in p['body'])}
        <div style="margin-top:var(--space-6);display:flex;gap:12px;flex-wrap:wrap">
          {cta_primary.replace('btn--lg', 'btn--md')}
          <a class="btn btn--ghost btn--md" href="/takeaway/" data-order-open data-track="lp:{slug}:takeaway" data-i18n="act.order">Bestill take-away</a>
        </div>
      </div>
      <div>
        <div class="card">
          <div class="kv-eyebrow" style="margin-bottom:var(--space-3)">{e(p['facts_title'])}</div>
          {facts}
          <p class="caption" style="margin-top:var(--space-4)">{e(p['facts_note'])}</p>
        </div>
      </div>
      </div>
    </div>
  </section>
{gallery}{press}
{faq.section(faq.landing_faq(slug))}
  <section class="section section--flush-top">
    <div class="wrap">
      <div class="divider"><span data-i18n="lp.venues">Restaurantene</span></div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:var(--space-5)">{venues}</div>
      <div class="divider" style="margin-top:var(--space-7)"><span data-i18n="lp.moreEyebrow">Se også</span></div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:var(--space-5)">{others}</div>
    </div>
  </section>

</main>

{chrome.footer()}
{modal.MODAL}
</body>
</html>
'''

def lunch_sub():
    return ', '.join(f'{vv(s)["lunch"]} på {vv(s)["name"]}' for s in ('majorstua', 'solli')) + f' og {vv("tonsberg")["lunch"]} i Tønsberg'

def tonsberg_unique():
    """Retter som bare finnes på Tønsberg-menyen (fra content/menus.js)."""
    m = kv.menus(); names = {}
    for v in m['venues']: names[v['slug']] = {it['name'] for s in v['menu']['sections'] for it in s['items']}
    uniq = sorted(names['tonsberg'] - names['majorstua'] - names['solli'])
    return ' og '.join([', '.join(uniq[:-1]), uniq[-1]]) if len(uniq) > 1 else (uniq[0] if uniq else 'flere retter')

def hours_line(slug):
    v = vv(slug)
    return ', '.join(f'{kv.day_range(h["days"])} {kv.hhmm(h["opens"])}–{kv.hhmm(h["closes"])}' for h in v['hours']['kitchen'])

PAGES = [
 dict(slug='lunsj', crumb='Lunsj',
      imgAlt='Lunsjbord med salater, burger og cocktails på Kverneriet Tønsberg', pos='center 40%',
      eyebrow='Majorstua · Solli · Tønsberg', h1='Lunsj i Oslo og Tønsberg',
      sub=f'Burgerlunsj med kjøtt vi kverner selv og fries som tar tre dager – {lunch_sub()}.', cta='book',
      sec_eyebrow='Burgerlunsj i Oslo og Tønsberg', h2='En skikkelig lunsj, ikke en rask matbit',
      body=[f'På <a href="/majorstua/">Majorstua</a> åpner kjøkkenet kl. 11 tirsdag til fredag, på <a href="/solli/">Solli</a> kl. 11.30. Da får du de samme burgerne som om kvelden: 150 gram kjøtt vi kverner selv, ferske brød og fries som har tatt tre dager å lage. Har du en times pause, rekker du både en burger og en milkshake.',
            f'I <a href="/tonsberg/">Tønsberg</a> serverer vi lunsj torsdag til søndag fra kl. 12, med en bredere meny enn i Oslo – {tonsberg_unique()} i tillegg til burgerne. Sitter dere flere fra samme kontor, booker dere bord, så står det klart når dere kommer.'],
      facts_title='Lunsj og kjøkkentider', facts=[('Majorstua', f'Lunsj {vv("majorstua")["lunch"]} · kjøkken {hours_line("majorstua")}', '/majorstua/'), ('Solli', f'Lunsj {vv("solli")["lunch"]} · kjøkken {hours_line("solli")}', '/solli/'), ('Tønsberg', f'Lunsj {vv("tonsberg")["lunch"]} · kjøkken {hours_line("tonsberg")}', '/tonsberg/'),
                                       ('Grupper fra kontoret', 'Book bord, så slipper dere å vente'), ('Take-away', 'Forhåndsbestill og hent selv på alle tre')],
      facts_note='Hele menyen serveres fra kjøkkenet åpner. Baren holder åpent lenger – se restaurantsidene.',
      media=['fa_2024', 'dn_2016', 'dn_2017'],
      others=[('julebord', 'xmas', 'Julebord'), ('selskap', 'groups', 'Selskap og grupper'), ('late-night', 'late', 'Late night')]),
 dict(slug='julebord', crumb='Julebord',
      imgAlt='Spisesalen på Kverneriet Solli med korallrosa stoler og dekkede bord',
      eyebrow='November og desember', h1='Julebord i Oslo og Tønsberg',
      sub=f'Julebord med burger i stedet for ribbe – for grupper over 8 (7 i Tønsberg) på Majorstua, Solli og i Tønsberg. Matpakker fra {PK["items"][0]["price"]} kr per person, bar som holder åpent etter maten.', cta='group',
      sec_eyebrow=f'Grupper over 8 (7 i Tønsberg) · fra {PK["items"][0]["price"]} kr', h2='Et julebord folk faktisk gleder seg til',
      body=['Ikke alle vil ha pinnekjøtt fire ganger i desember. Hos oss får gjengen din burgere av kjøtt vi kverner selv, fries som tar tre dager og milkshakes – på <a href="/majorstua/">Majorstua</a>, <a href="/solli/">Solli</a> eller i <a href="/tonsberg/">Tønsberg</a>, i et lokale med bar som holder åpent til 23 tirsdag–lørdag.',
            f'Bordet velger én matpakke for hele gjengen: {", ".join(f"{p["name"]} ({p["price"]} kr)" for p in PK["items"])}. Send oss en forespørsel med antall, dato og ønsket tidspunkt, så kommer vi tilbake med et forslag til bord og meny. Julebordene fyller opp tidlig, så jo før du booker, jo bedre.'],
      facts_title='Slik fungerer det', facts=[('Antall', 'Grupper over 8 personer (7 i Tønsberg) booker som selskap')] + [(p['name'], f'{p["price"]} kr per person – {p["desc"]}') for p in PK['items']] + [('Barn', f'Barnemeny {PK["kids"]} kr for gjester under 12'), ('Baren', 'Åpen til 23 tirsdag–lørdag, 22 søndag og mandag')],
      facts_note='Pakkene gjelder hele bordet. Allergier og spesialbehov løser vi når vi får beskjed på forhånd.',
      media=['db_2023', 'fa_2026', 'vg_2017'],
      others=[('selskap', 'groups', 'Selskap og grupper'), ('lunsj', 'lunch', 'Lunsj'), ('late-night', 'late', 'Late night')]),
 dict(slug='selskap', crumb='Selskap og grupper',
      imgAlt='Uteserveringen til Kverneriet Tønsberg på Kaldnes brygge i kveldslys',
      eyebrow='Bursdag · Vennegjeng · Firma', h1='Selskap i Oslo og Tønsberg',
      sub=f'Gruppebooking for bursdag, firmafest og vennegjeng på Majorstua, Solli eller i Tønsberg. Grupper over 8 (7 i Tønsberg) velger matpakke fra {PK["items"][0]["price"]} kr per person.', cta='group',
      sec_eyebrow='Grupper over 8 personer (7 i Tønsberg)', h2='Samle gjengen rundt et langbord',
      body=['Vi tar imot selskap på alle tre restaurantene: <a href="/majorstua/">Kverneriet Majorstua</a> og <a href="/solli/">Kverneriet Solli</a> i Oslo, og <a href="/tonsberg/">Kverneriet Tønsberg</a>. Bursdag, avslutning, vennegjeng som ikke har sett hverandre på lenge, eller et team som fortjener noe bedre enn kantina – burgere av kjøtt vi kverner selv passer alle.',
            f'Grupper over 8 (7 i Tønsberg) velger én matpakke for hele bordet, så maten kommer samlet og raskt. Fyll ut forespørselen med antall, dato og tidsrom, så finner vi plass. Skal dere ha barn med, har vi egen barnemeny til {PK["kids"]} kr for gjester under 12.'],
      facts_title='Godt å vite', facts=[('Antall', 'Grupper over 8 (7 i Tønsberg) booker som selskap – vi finner plass til større selskap også')] + [(p['name'], f'{p["price"]} kr per person') for p in PK['items']] + [('Barn', f'Barnemeny {PK["kids"]} kr for gjester under 12'), ('Allergier', 'Alle retter er merket med allergener i menyen'), ('Drop-in', 'Mindre grupper booker online eller kommer innom')],
      facts_note='Forespørselen går til restauranten, og bordet er bekreftet når du har fått e-post fra oss.',
      media=['db_2023', 'vg_2017', 'ap_2020'],
      others=[('julebord', 'xmas', 'Julebord'), ('lunsj', 'lunch', 'Lunsj'), ('late-night', 'late', 'Late night')]),
 dict(slug='late-night', crumb='Late night',
      imgAlt='Gjester som skåler med cocktails og burgere på Kverneriet om kvelden', pos='center 40%',
      gallery=[('/assets/img/ln-beer.jpg', 'Øl tappes fra tappekrana i baren', '4/5'), ('/assets/img/ln-burger.jpg', 'Burger holdt i hendene ved bordet', '4/5'), ('/assets/img/ln-cocktail.jpg', 'Rød cocktail på marmorbaren', '4/5')],
      eyebrow='Åpent sent · tirsdag–lørdag', h1='Late night burger i Oslo',
      sub='Spise sent? Kjøkkenet på Majorstua og Solli serverer hele menyen til kl. 22, og baren holder åpent til 23 tirsdag til lørdag. Ingen booking nødvendig.', cta='book',
      sec_eyebrow='Majorstua · Solli · Tønsberg', h2='Åpent sent: kjøkkenet til 22, baren til 23',
      body=['Etter kino, etter kampen, etter en lang dag på jobb. Kjøkkenet på <a href="/majorstua/">Majorstua</a> og <a href="/solli/">Solli</a> serverer hele menyen til kl. 22 fra tirsdag til lørdag (21 søndag og mandag), og baren holder åpent en time til. Vi har mange drop-in-bord, så du trenger ikke booke for å spise sent i Oslo.',
            'Nattmat på Kverneriet betyr burger av kjøtt vi kverner selv, fries som tar tre dager, og en milkshake med 4 cl matchende sprit – eller en øl fra tappen og en cocktail fra baren. I <a href="/tonsberg/">Tønsberg</a> holder kjøkkenet åpent til 22 tirsdag–lørdag og baren til 23.'],
      facts_title='Sene åpningstider', facts=[('Majorstua – kjøkken', hours_line('majorstua'), '/majorstua/'), ('Solli – kjøkken', hours_line('solli'), '/solli/'), ('Tønsberg – kjøkken', hours_line('tonsberg'), '/tonsberg/'),
                                              ('Baren', 'Til 23 tirsdag–lørdag, til 22 søndag og mandag (alle tre)'), ('Make it grown-up', 'Milkshake med 4 cl sprit, +80 kr'), ('Drop-in', 'Mange bord uten booking')],
      facts_note='Kjøkkentider per restaurant. Baren holder åpent etter at kjøkkenet stenger.',
      media=['fa_2025', 'db_2020', 'mao_2018'],
      others=[('lunsj', 'lunch', 'Lunsj'), ('selskap', 'groups', 'Selskap og grupper'), ('julebord', 'xmas', 'Julebord')]),
]

def build():
    for p in PAGES:
        kv.write(p['slug'], page(p)); print(kv.path(p['slug']), 'ok')

if __name__ == '__main__':
    build(); G.write()
