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
    """Ett kort. Lenken nederst er en lenke, ikke en knapp."""
    tit, sub, alt = c['title'], c.get('sub') or {}, c.get('alt') or {}
    lt = c.get('lenketekst') or {'no': 'Les mer', 'en': 'Read more'}
    k = f'{nokkel}.{c["key"]}'
    G.add(f'{k}.title', tit['no'], tit.get('en') or tit['no'])
    if sub.get('no'): G.add(f'{k}.sub', sub['no'], sub.get('en') or sub['no'])
    G.add(f'{k}.cta', lt['no'], lt.get('en') or lt['no'])

    href, attrs = _href(c.get('href', ''))
    tag = 'a' if href else 'button'
    opn = f'<a class="kort" href="{href}" {attrs}>' if href else f'<button class="kort" type="button" {attrs}>'
    bilde = (f'<figure class="kort__bilde"><img src="{c["image"]}" alt="{e(alt.get("no",""))}" '
             f'loading="lazy" decoding="async"></figure>') if c.get('image') else ''
    sub_html = f'<p class="kort__sub" data-i18n="{k}.sub">{e(sub["no"])}</p>' if sub.get('no') else ''
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


ANLEDNINGER = [
    ('lunsj',      'lunsj',    'Fra kl. 11 i Oslo, 12 i Tønsberg',  'Lunsj',
     'Samme burgere som om kvelden, raskt nok til en times pause.'),
    ('julebord',   'julebord', 'November og desember',              'Julebord',
     'Burgere i stedet for ribbe. Grupper over 8, 7 i Tønsberg.'),
    ('selskap',    'selskap',  'Bursdag · vennegjeng · firma',      'Selskap og grupper',
     'Langbord til gjengen, barnemeny til de små. Opptil 30–40 personer.'),
    ('latenight',  'late-night', 'Kjøkken til 22, bar til 23',      'Late night',
     'Etter kino, etter kampen. Drop-in-bord og milkshake med sprit.'),
    ('middag',     'middag',   'Hver kveld',                        'Middag',
     'Tre dagers fries, kjøtt vi kverner selv, og god tid.'),
    ('takeaway',   '#order',   'Hent selv eller få levert',         'Take-away',
     'Hent selv via OrderX, eller få levert med Wolt og Foodora i Oslo.'),
    ('gavekort',   'giftcard', 'Hele året',                         'Gavekort',
     'Et måltid noen faktisk gleder seg til.'),
]


def occasions_section():
    """Anledninger – samme karusellkomponent som over (ønske fra Kverneriet 21.10.2026)."""
    items = [{'key': k, 'href': h,
              'title': {'no': t, 'en': t},
              'sub': {'no': b, 'en': b},
              'lenketekst': {'no': 'Les mer', 'en': 'Read more'}} for k, h, e, t, b in ANLEDNINGER]
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
