#!/usr/bin/env python3
"""«Kverneriet i media»: logostripe under heroen + kortgalleri med lenke til hver omtale.
Kilden er MEDIA-listen under (verifisert 15.09.2026 ved å åpne hver URL). Rediger her og kjør:
python3 tools/media.py && python3 tools/build-landing.py"""
import re, os, sys, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import press as P
import kv
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def e(s): return H.escape(s, quote=True)

# Avislogoer: nøkkel → (css-klasse, visningsnavn). Aviser uten SVG får tekst-ordmerke.
LOGOS = {
 'dagbladet': ('press-logo--dagbladet', 'Dagbladet'), 'finansavisen': ('press-logo--finansavisen', 'Finansavisen'),
 'dn': ('press-logo--dn', 'Dagens Næringsliv'), 'vg': ('press-logo--vg', 'VG'), 'aftenposten': ('press-logo--aftenposten', 'Aftenposten'),
 'dagsavisen': ('press-logo--dagsavisen', 'Dagsavisen'), 'nettavisen': ('press-logo--nettavisen', 'Nettavisen'),
 'tb': ('press-logo--tb', 'Tønsbergs Blad'), 'godt': ('press-logo--text', 'Godt.no'), 'meravoslo': ('press-logo--img', 'Mer av Oslo'), 'op': ('press-logo--text', 'Østlands-Posten'),
}
# Logoer som ikke egner seg som énfarget maske (Mer av Oslo har et beige/blått merke) vises som bilde
IMG_LOGOS = {'meravoslo': ('/assets/press/meravoslo.png', 200, 199)}

def logo(key, size=''):
    cls, name = LOGOS[key]
    if cls == 'press-logo--text': return f'<span class="press-logo press-logo--text">{e(name)}</span>'
    if cls == 'press-logo--img':
        src, w, h = IMG_LOGOS[key]
        return f'<img class="press-logo press-logo--img press-logo--{key}" src="{src}" alt="{e(name)}" width="{w}" height="{h}" loading="lazy">'
    return f'<span class="press-logo {cls}{(" "+size) if size else ""}" role="img" aria-label="{e(name)}"></span>'

def die(rating, outlet_key):
    """Terningkast: Dagbladets egen for Dagbladet, generisk ink-terning for andre. Andre skalaer vises som tekst."""
    m = re.fullmatch(r'(\d)/6', rating or '')
    if not m: return f'<span class="terning__label" aria-label="Vurdering {e(rating)}">{e(rating)}</span>' if rating else ''
    n = int(m.group(1))
    src = '/assets/press/dagbladet-terning.png' if outlet_key == 'dagbladet' else f'/assets/press/terning-{n}.svg'
    return (f'<span class="terning{"" if outlet_key=="dagbladet" else " terning--generic"}"><img class="terning__die" src="{src}" alt="Terningkast {n}"{' width="256" height="192"' if outlet_key=="dagbladet" else ' width="120" height="124"'}>'
            f'<span class="terning__label" aria-hidden="true">{n}<span class="terning__of">/6</span></span></span>').replace('<img class="terning__die"', '<img class="terning__die" loading="lazy"')

# ---- Sitatbank: 90 omtaler ble funnet og verifisert 15.09.2026 (scratch: press-confirmed.json).
# Her ligger de redaksjonelle og positive, sterkeste først. 'vg' brukes også for Godt.no (VGs matseksjon). ----
MEDIA = [
 dict(key='db_2020', outlet='dagbladet', title='«Oslos overlegent beste burger»', date='2020', url='https://www.dagbladet.no/mat/oslos-overlegent-beste-burger/72391109',
      rating='6/6', quote='Burgerne fra Kverneriet er så nære man kommer en perfekt.', venue='solli', photo='/assets/img/ta-press-burger.jpg', alt='Burger fra Kverneriet holdt opp mot lyset'),
 dict(key='fa_2026', outlet='finansavisen', title='«Oslo, våkne opp!»', date='2026', url='https://www.finansavisen.no/mat-og-drikke/2026/02/21/8326967/anmeldelse-av-restaurant-kverneriet-pa-majorstuen',
      rating='5/6', quote='Kverneriet bør spille en av hovedrollene på Oslos burgerscene. Nesten toppklasse.', venue='majorstua', photo='/assets/img/majorstua-about.jpg', alt='Spisesalen på Kverneriet Majorstua'),
 dict(key='db_2023', outlet='dagbladet', title='Oslos beste burger: «Himmelsk!»', date='2023', url='https://www.dagbladet.no/mat/oslos-beste-burger-himmelsk/78327900',
      rating='', quote='Kverneriet har toppet de fleste av våre tidligere burgertester, og det skjønner vi godt.', venue='solli', photo='/assets/img/solli-hero.jpg', alt='Spisesalen på Kverneriet Solli'),
 dict(key='vg_2016', outlet='vg', title='«Sjefsburger»', date='2016', url='https://www.godt.no/anmeldelser/restaurant/i/mRdjng/restaurantanmeldelse-av-kverneriet-sjefsburger',
      rating='5/6', quote='Kverneriet på Majorstuen har Oslos beste burger.', venue='majorstua', photo='/assets/img/trio-majorstua.jpg', alt='Kverneriet Majorstua'),
 dict(key='dn_2017', outlet='dn', title='«Dette er faktisk vilt godt»', date='2017', url='https://www.dn.no/smak/lunsjguiden/kverneriet/solli-plass/burgere/-dette-er-faktisk-vilt-godt/2-1-193022',
      rating='21/25', quote='Dette er en av de beste burgerne jeg har smakt her i byen.', venue='solli', photo='/assets/img/meny-solli.jpg', alt='Burger på marmorbord, Kverneriet Solli'),
 dict(key='fa_2020', outlet='finansavisen', title='Test av take-away-burger i Oslo', date='2020', url='https://www.finansavisen.no/premium/lunsjguiden/2020/04/19/7518435/test-av-takeaway-burger-i-oslo',
      rating='6/6', quote='Her har de gjort alt riktig. Brødet er luftig og kjøttet er virkelig godt.', venue='solli', photo='/assets/img/ta-press-boxes.jpg', alt='Take-away-esker fra Kverneriet'),
 dict(key='vg_2017', outlet='vg', title='«Bra burger»', date='2017', url='https://www.godt.no/anmeldelser/restaurant/i/OpBAwb/restaurantanmeldelse-av-kverneriet-bra-burger',
      rating='5/6', quote='Kverneriet på Solli plass byr på vellaget tohåndsmat i fine omgivelser.', venue='solli', photo='/assets/img/solli-about.jpg', alt='Uteserveringen ved Solli plass'),
 dict(key='ap_2015', outlet='aftenposten', title='«Oslo har fått en ny burgerhimmel»', date='2015', url='https://www.aftenposten.no/oslo/sulten/i/4dROV/kverneriet-oslo-har-faatt-en-ny-burgerhimmel',
      rating='', quote='Majorstuen har fått et nytt, godt vannhull med nydelig håndmat.', venue='majorstua', photo='/assets/img/g-burger.jpg', alt='Burger på tallerken'),
 dict(key='mao_2018', outlet='meravoslo', title='Hamburgere laget med kjærlighet', date='2018', url='https://meravoslo.no/nyheter/22/7/2018/kverneriet',
      rating='6/6', quote='Vi kan på det varmeste anbefale å prøve Umami-burgeren, for det er ikke mange bedre hamburgere i Oslo mener vi!', venue='solli', photo='/assets/img/craft-grind.jpg', alt='Nykvernede patties på fjøl'),
 dict(key='tb_2024', outlet='tb', title='«Smakene sitter som de skal»', date='2024', url='https://www.tb.no/kverneriet-i-tonsberg-smakene-sitter-som-de-skal-men-gar-det-egentlig-an-med-ananas-pa-burger/r/5-76-2376585',
      rating='5/6', quote='Kverneriet har noe for alle.', venue='tonsberg', photo='/assets/img/tonsberg-about.jpg', alt='Lunsjbord på Kverneriet Tønsberg'),
 dict(key='ap_2020', outlet='aftenposten', title='«Majorstua-burger med mersmak»', date='2020', url='https://vink.aftenposten.no/artikkel/APLkgA/anmeldelse-av-burgerrestauranten-kverneriet-pa-majorstua',
      rating='4/6', quote='Servicen er på alerten fra det øyeblikket vi kommer inn døren til vi har fått bestilt, samt gjennom hele måltidet.', venue='majorstua', photo='/assets/img/majorstua-hero.jpg', alt='Kverneriet Majorstua'),
 dict(key='fa_2026b', outlet='finansavisen', title='Fire burgere i Oslo du bør teste', date='2026', url='https://www.finansavisen.no/mat-og-drikke/2026/01/31/8324464/her-er-fire-restauranter-i-oslo-vi-anbefaler-at-du-tester-burgeren',
      rating='', quote='Fortsetter å levere ordentlig gode burgere år etter år.', venue='generelt', photo='/assets/img/g-fries-truffle.jpg', alt='Trøffelfries'),
 dict(key='na_2020', outlet='nettavisen', title='172 ting du bør ha sett i Norge', date='2020', url='https://www.nettavisen.no/livsstil/reisetips/172-ting-du-bor-ha-sett-i-norge/s/12-95-3423952768',
      rating='', quote='Rett ved finner du Oslos beste burger på Kverneriet.', venue='majorstua', photo='/assets/img/g-softserve-oreo.jpg', alt='Soft serve med Oreo'),
 dict(key='ap_2023', outlet='aftenposten', title='Oslos beste 2023: burger', date='2023', url='https://vink.aftenposten.no/artikkel/eJQ8Gl/render-er-vinner-av-oslos-beste-2023-i-kategorien-burger',
      rating='', quote='Steder som […] Kverneriet […] fortsetter å levere varene, år etter år.', venue='generelt', photo='/assets/img/craft-fries.jpg', alt='Fries med trøffel og parmesan'),
 dict(key='db_2017', outlet='dagbladet', title='«Wow! Her blir det vanskelig å finne ord»', date='2017', url='https://www.dagbladet.no/mat/robinson-begynte-a-mape-pa-burgerrestauranten--wow-her-blir-det-vanskelig-a-finne-ord/68690888',
      rating='', quote='Mørt og saftig kjøtt og delikat tilbehør.', venue='solli', photo='/assets/img/ln-burger.jpg', alt='Burger i hendene ved bordet'),
 dict(key='db_2016', outlet='dagbladet', title='«Nam-nam på Kverneriet»', date='2016', url='https://www.dagbladet.no/tema/nam-nam-pa-kverneriet/60427896',
      rating='', quote='Kjøttet i Umami-burgeren var grovkvernet, veldig saftig og full av spennende smaker.', venue='majorstua', photo='/assets/img/g-patties.jpg', alt='Patties med blåmuggost'),
 dict(key='tb_2020', outlet='tb', title='«Ren nytelse»', date='2020', url='https://www.tb.no/tbs-restaurantanmeldere-mener-kverneriet-er-mer-enn-burgere-ren-nytelse/r/5-76-1253308',
      rating='', quote='TBs restaurantanmeldere mener Kverneriet er mer enn burgere: ren nytelse.', venue='tonsberg', photo='/assets/img/tonsberg-hero.jpg', alt='Kverneriet Tønsberg på Kaldnes, ved kanalen'),
 dict(key='op_2021', outlet='op', title='Folket har talt: Tønsbergs beste restaurant', date='2021', url='https://www.op.no/folket-har-talt-dette-er-tonsbergs-beste-restaurant-en-bekreftelse-pa-at-vi-er-pa-rett-vei/s/5-36-1112460',
      rating='', quote='Folket har talt – dette er Tønsbergs beste restaurant: – En bekreftelse på at vi er på rett vei.', venue='tonsberg', photo='/assets/img/trio-tonsberg.jpg', alt='Uteserveringen i Tønsberg'),
 dict(key='fa_2024', outlet='finansavisen', title='Forretningslunsjen på Solli plass', date='2024', url='https://www.finansavisen.no/mat-og-drikke/2024/03/22/8112125/finansavisen-sin-anmeldelse-av-restaurant-kverneriet-pa-solli-plass',
      rating='', quote='Er det sentrums beste sted for å kombinere business og burger? Ja.', venue='solli', photo='/assets/img/solli-hero.jpg', alt='Spisesalen på Kverneriet Solli'),
 dict(key='fa_2025', outlet='finansavisen', title='Overtidsmaten vi anbefaler', date='2025', url='https://www.finansavisen.no/mat-og-drikke/2025/09/21/8292533/til-lange-dager-pa-kontoret-her-er-overtidsmaten-vi-anbefaler',
      rating='', quote='Kverneriet har servert bankers burgere i luksussegmentet i en årrekke. Dette er noe helt annet enn den jevne gatekjøkkenburgeren.', venue='generelt', photo='/assets/img/ta-band.jpg', alt='Innpakket take-away-burger'),
 dict(key='dn_2016', outlet='dn', title='Lunsjguiden: Kverneriet Majorstua', date='2016', url='https://www.dn.no/smak/lunsjguiden/mat/smak/-gar-ikke-folk-snart-lei/1-1-5753348',
      rating='21/25', quote='Har man lyst på burger til lunsj, er Kverneriet absolutt et godt valg.', venue='majorstua', photo='/assets/img/g-burger.jpg', alt='Burger på tallerken'),
]

BY_KEY = {m['key']: m for m in MEDIA}
def by_key(*keys): return [BY_KEY[k] for k in keys]

def card(m):
    lg = logo(m['outlet'])
    d = die(m['rating'], m['outlet'])
    return (f'<article class="media-card">'
            f'<figure class="photo"><img src="{m["photo"]}" alt="{e(m["alt"])}" loading="lazy"></figure>'
            f'<div class="media-card__body"><div class="media-card__head">{lg}{d}</div>'
            f'<h3 class="media-card__title">{e(m["title"])}</h3><p>&laquo;{e(m["quote"])}&raquo;</p>'
            f'<div class="media-card__meta"><span class="caption">{e("VG / Godt.no" if m["outlet"]=="vg" else LOGOS[m["outlet"]][1])} · {e(m["date"])}</span>'
            f'<a class="btn btn--outline btn--sm" href="{e(m["url"])}" target="_blank" rel="noopener" data-track="media:{m["outlet"]}:{m["date"]}" data-i18n="media.read">Les omtalen</a></div></div></article>')

def section(items, eyebrow_key='media.eyebrow', title_key='media.title'):
    return (f'  <section class="section section--flush-top" id="media">\n    <div class="wrap">\n'
            f'      <header class="sec-head"><div class="sec-head__rule"></div><span class="kv-eyebrow" data-i18n="{eyebrow_key}">Omtalt i pressen</span>'
            f'<h2 class="display-2" data-i18n="{title_key}">Kverneriet i media</h2></header>\n'
            f'      <div class="media-scroller">{"".join(card(m) for m in items)}</div>\n'
            f'    </div>\n  </section>\n')

SEEN_IN_ORDER = ['dagbladet', 'finansavisen', 'vg', 'aftenposten', 'dn', 'nettavisen', 'meravoslo', 'tb']
def seen_in():
    present = [k for k in SEEN_IN_ORDER if any(m['outlet'] == k for m in MEDIA) or k == 'dagbladet']
    return ('    <div class="seen-in"><span class="seen-in__label" data-i18n="media.seenIn">Omtalt i</span>' + ''.join(logo(k) for k in present) + '</div>')

if __name__ == '__main__':
    s = open('index.html', encoding='utf-8').read()
    # Logostripe rett etter tillitsraden
    s, n = re.subn(r'(    <div class="trust">.*?\n    </div>\n)(?:    <div class="seen-in">.*?</div>\n)?', lambda m: m.group(1) + seen_in() + '\n', s, count=1, flags=re.S)
    if n != 1: raise SystemExit('trust row not found')
    # Media-seksjonen erstatter presse-seksjonen på forsiden (kortene dekker det samme og mer)
    s, n = re.subn(r'  <section class="section[^"]*" id="(?:presse|media)">.*?\n  </section>\n', lambda m: section(MEDIA), s, count=1, flags=re.S)
    if n != 1: raise SystemExit('press/media section not found')
    open('index.html', 'w', encoding='utf-8').write(s); print('index media ok:', len(MEDIA), 'cards')
    # Restaurantsidene: kort for den restauranten + generelle
    for slug in ['majorstua', 'solli', 'tonsberg']:
        f = kv.path(slug); s = open(f, encoding='utf-8').read()
        items = [m for m in MEDIA if m['venue'] in (slug, 'generelt')]
        if len(items) < 2: continue
        s, n = re.subn(r'  <section class="section[^"]*" id="(?:presse|media)">.*?\n  </section>\n', lambda m: section(items), s, count=1, flags=re.S)
        if n == 0:
            anchor = '  <!-- Take-away -->\n  <section class="section section--tint" id="order">'
            if anchor in s: s = s.replace(anchor, section(items) + '\n' + anchor, 1); n = 1
        if n == 1: open(f, 'w', encoding='utf-8').write(s); print(f, 'media ok:', len(items))
