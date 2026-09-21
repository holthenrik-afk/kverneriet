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
 'tb': ('press-logo--tb', 'Tønsbergs Blad'), 'godt': ('press-logo--text', 'Godt.no'), 'meravoslo': ('press-logo--meravoslo', 'Mer av Oslo'), 'op': ('press-logo--text', 'Østlands-Posten'),
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
# Omtalene ligger i content/press.json (redigeres i Sanity → tools/fetch_sanity.py). Sortering = rekkefølgen i fila.
MEDIA = [m for m in kv.press() if m.get('featured', True)]

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
    """«Omtalt i»: etiketten som en divider (samme komponent som «Galleri»/«Se også»), logoene i én rolig, énfarget rad."""
    present = [k for k in SEEN_IN_ORDER if any(m['outlet'] == k for m in MEDIA) or k == 'dagbladet']
    return ('    <div class="seen-in"><div class="divider"><span data-i18n="media.seenIn">Omtalt i</span></div>'
            '<div class="seen-in__logos">' + ''.join(logo(k) for k in present) + '</div></div>')

def proof():
    """Tillitsraden under heroen: to like bevis (terning + påstand + kilde), begge lenket til omtalen."""
    items = []
    for key, claim, i18n in (('db_2020', 'Oslos overlegent beste burger', 'home.trustDb'), ('fa_2020', 'Oslos beste take-away-burger', 'home.trustTa')):
        m = BY_KEY[key]
        items.append(f'<a class="proof__item" href="{e(m["url"])}" target="_blank" rel="noopener" data-track="media:{m["outlet"]}:{m["date"]}">'
                     f'{die(m["rating"], m["outlet"])}<span class="proof__text"><strong class="proof__claim" data-i18n="{i18n}">{e(claim)}</strong>'
                     f'<span class="proof__src">{e(LOGOS[m["outlet"]][1])} · {e(m["date"])}</span></span></a>')
    return '    <div class="proof">' + ''.join(items) + '</div>'

if __name__ == '__main__':
    s = open('index.html', encoding='utf-8').read()
    # Logostripe rett etter tillitsraden
    # Tillitsraden (beviskortene) er tatt bort etter ønske fra Henrik 21.09.2026 – bare «Omtalt i»-stripen står igjen under CTA-ene
    s, n = re.subn(r'(?:    <div class="proof">.*?</div>\n|    <div class="trust">.*?\n    </div>\n)?    <div class="seen-in">.*?</div>\n', lambda m: seen_in() + '\n', s, count=1, flags=re.S)
    if n != 1: raise SystemExit('seen-in strip not found')
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
