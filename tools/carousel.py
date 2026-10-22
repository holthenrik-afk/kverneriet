#!/usr/bin/env python3
"""Én karusellkomponent, brukt to steder på forsiden (ønske fra Kverneriet 21.10.2026).

Kortene ligger side om side i et scroll-snap-spor. Hele kortet er klikkbart, og under
teksten står en diskré lenke – ingen primærknapp, så den ikke konkurrerer med «Book bord»
øverst på siden. Piler og prikker legges på av site.js; uten JavaScript kan sporet dras.

Rekkefølgen kommer fra innholdet, så kunden kan dra kortene rundt i Sanity når sesongen
skifter. Det var hele poenget med bestillingen.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv, i18n_gen as G

e = kv.esc
ORG = kv.venues()['org']


def _href(h):
    """Kortets mål. #book og #order åpner modalen, resten er vanlige sider."""
    if h == '#book':  return None, 'data-book-open data-track="kort:book"'
    if h == '#order': return None, 'data-order-open data-track="kort:takeaway"'
    if h == 'giftcard': return ORG['giftcard'], 'target="_blank" rel="noopener"'
    return kv.url(h), ''


def card(c, nokkel):
    """Ett kort. Lenken nederst er en lenke, ikke en knapp.

    Stikkordet ligger som en pille nederst til venstre på bildet. Det skal være et
    operativt faktum – klokkeslett, antall personer eller pris fra – fordi det er
    det gjesten leter etter når hun bestemmer seg få timer før besøket.
    """
    tit, sub, alt = c['title'], c.get('sub') or {}, c.get('alt') or {}
    lt = c.get('lenketekst') or {'no': 'Les mer', 'en': 'Read more'}
    k = f'{nokkel}.{c["key"]}'
    G.add(f'{k}.title', tit['no'], tit.get('en') or tit['no'])
    if sub.get('no'): G.add(f'{k}.sub', sub['no'], sub.get('en') or sub['no'])
    G.add(f'{k}.cta', lt['no'], lt.get('en') or lt['no'])

    stikk = c.get('stikkord') or {}
    pille = ''
    if stikk.get('no'):
        G.add(f'{k}.pille', stikk['no'], stikk.get('en') or stikk['no'])
        pille = f'<span class="kort__pille" data-i18n="{k}.pille">{e(stikk["no"])}</span>'

    bilde = (f'<figure class="kort__bilde"><img src="{c["image"]}" alt="{e(alt.get("no",""))}" '
             f'loading="lazy" decoding="async">{pille}</figure>') if c.get('image') else ''
    sub_html = f'<p class="kort__sub" data-i18n="{k}.sub">{e(sub["no"])}</p>' if sub.get('no') else ''

    # href=None betyr et kort som bare skal leses – «Slik jobber vi» peker ingen steder
    # ennå. Da blir det en div uten lenketekst, ikke en knapp som ikke gjør noe.
    if c.get('href') is None:
        return (f'<div class="kort kort--flat">{bilde}<div class="kort__tekst">'
                f'<h3 class="kort__tit" data-i18n="{k}.title">{e(tit["no"])}</h3>'
                f'{sub_html}</div></div>')

    href, attrs = _href(c['href'])
    opn = f'<a class="kort" href="{href}" {attrs}>' if href else f'<button class="kort" type="button" {attrs}>'
    return (f'{opn}{bilde}<div class="kort__tekst">'
            f'<h3 class="kort__tit" data-i18n="{k}.title">{e(tit["no"])}</h3>'
            f'{sub_html}'
            f'<span class="kort__lenke" data-i18n="{k}.cta">{e(lt["no"])}</span>'
            f'</div></{"a" if href else "button"}>')


def track(items, nokkel, label):
    """Selve sporet med piler og prikker. Samme markup begge stedene den brukes."""
    if not items: raise SystemExit(f'karusell «{nokkel}»: ingen kort')
    G.add('kar.prev', 'Forrige', 'Previous')
    G.add('kar.next', 'Neste', 'Next')
    kort = ''.join(card(c, nokkel) for c in items)
    prikker = ''.join(
        f'<button type="button" class="kar__prikk" data-kar-goto="{i}" aria-label="{i+1} av {len(items)}"'
        f'{" aria-current=\"true\"" if i == 0 else ""}></button>' for i in range(len(items)))
    return (f'<div class="kar" data-kar aria-roledescription="carousel" aria-label="{e(label)}">\n'
            f'        <div class="kar__spor" tabindex="0">{kort}</div>\n'
            f'        <div class="kar__styring">\n'
            f'          <button type="button" class="kar__pil" data-kar-prev aria-label="Forrige" data-i18n-label="kar.prev">‹</button>\n'
            f'          <div class="kar__prikker">{prikker}</div>\n'
            f'          <button type="button" class="kar__pil" data-kar-next aria-label="Neste" data-i18n-label="kar.next">›</button>\n'
            f'        </div>\n      </div>')


def story_section():
    """Karusellen med Viktors seks budskap, rett under presselogoene."""
    items = kv.site_copy().get('storyCards') or []
    G.add('home.storyEyebrow', 'Hos Kverneriet', 'At Kverneriet')
    G.add('home.storyTitle', 'Hva vil du ha i dag?', 'What are you after today?')
    return ('  <section class="section section--flush-top" id="story">\n    <div class="wrap">\n'
            '      <header class="sec-head"><div class="sec-head__rule"></div>'
            '<span class="kv-eyebrow" data-i18n="home.storyEyebrow">Hos Kverneriet</span>'
            '<h2 class="display-2" data-i18n="home.storyTitle">Hva vil du ha i dag?</h2></header>\n'
            f'      {track(items, "story", "Hos Kverneriet")}\n'
            '    </div>\n  </section>\n')


# nøkkel, lenke, stikkord (pille), tittel, undertekst, bilde, alt-tekst.
# Bildene er valgt uten synlig alkohol: Tønsberg har fått advarsel før, og
# kortene ligger på forsiden der de treffer alle.
# (nøkkel, side, stikkord, tittel, undertekst, bilde, alt-tekst) – norsk og engelsk.
# Kortene sto lenge med norsk tekst også i den engelske utgaven, fordi de ble satt opp
# med 'en': samme norske streng. Begge språk står nå side om side her.
ANLEDNINGER = [
    ('lunsj',      'lunsj',
     ('Fra kl. 11', 'From 11.00'),
     ('Lunsj', 'Lunch'),
     ('Samme burgere som om kvelden, raskt nok til en times pause.',
      'The same burgers as in the evening, fast enough for an hour off.'),
     '/assets/img/hero-lunsj.jpg',
     ('Gjester på uteserveringen en lys ettermiddag', 'Guests on the terrace on a bright afternoon')),
    ('julebord',   'julebord',
     ('Nov og des', 'Nov and Dec'),
     ('Julebord', 'Christmas parties'),
     ('Burgere i stedet for ribbe. Grupper over 8, 7 i Tønsberg.',
      'Burgers instead of pork belly. Groups over 8, or 7 in Tønsberg.'),
     '/assets/img/hero-julebord.jpg',
     ('Spisesalen på Kverneriet Tønsberg', 'The dining room at Kverneriet Tønsberg')),
    ('selskap',    'selskap',
     ('Fra 8 personer', 'From 8 people'),
     ('Selskap og grupper', 'Parties and groups'),
     ('Langbord til gjengen, barnemeny til de små. Opptil 30–40 personer.',
      'A long table for the group, a kids menu for the little ones. Up to 30–40 people.'),
     '/assets/img/hero-selskap.jpg',
     ('Gjester ved bordene på uteserveringen', 'Guests at the tables on the terrace')),
    ('latenight',  'late-night',
     ('Kjøkken til 22', 'Kitchen until 22'),
     ('Late night', 'Late night'),
     ('Etter kino, etter kampen. Drop-in-bord.',
      'After the cinema, after the match. Walk-in tables.'),
     '/assets/img/ln-burger.jpg',
     ('Burger servert sent på kvelden', 'A burger served late in the evening')),
    ('middag',     'middag',
     ('Hver kveld', 'Every evening'),
     ('Middag', 'Dinner'),
     ('Tre dagers fries, kjøtt vi kverner selv, og god tid.',
      'Three-day fries, beef we grind ourselves, and time to linger.'),
     '/assets/img/index-hero.jpg',
     ('Burger fra Kverneriet på tallerken', 'A Kverneriet burger on the plate')),
    # Take-away og gavekort lå her før, men har fått egne seksjoner rett under
    # karusellen (22.10.2026). To like kort med samme bilde og samme lenke rett
    # over seksjonene de peker til, gir bare to steder å dele klikkene på.
]


def occasions_section():
    """Anledninger – samme karusellkomponent som over (ønske fra Kverneriet 21.10.2026)."""
    items = [{'key': k, 'href': h,
              'title': {'no': t[0], 'en': t[1]},
              'sub': {'no': b[0], 'en': b[1]},
              'stikkord': {'no': s[0], 'en': s[1]},
              'image': img, 'alt': {'no': alt[0], 'en': alt[1]},
              'lenketekst': {'no': 'Les mer', 'en': 'Read more'}}
             for k, h, s, t, b, img, alt in ANLEDNINGER]
    G.add('home.occEyebrow', 'Lunsj, kveld og fest', 'Lunch, evening and celebration')
    G.add('home.occTitle', 'Anledninger', 'Occasions')
    return ('  <section class="section section--flush-top" id="anledninger">\n    <div class="wrap">\n'
            '      <header class="sec-head"><div class="sec-head__rule"></div>'
            '<span class="kv-eyebrow" data-i18n="home.occEyebrow">Lunsj, kveld og fest</span>'
            '<h2 class="display-2" data-i18n="home.occTitle">Anledninger</h2></header>\n'
            f'      {track(items, "occ", "Anledninger")}\n'
            '    </div>\n  </section>\n')


if __name__ == '__main__':
    print(story_section()[:900])
