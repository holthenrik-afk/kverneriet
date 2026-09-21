#!/usr/bin/env python3
"""Importerer menyene fra kverneriet.com/<restaurant>/menu/ til content/menus.js (innholdslaget).

Kjør: python3 tools/import-menus.py            # henter live
      python3 tools/import-menus.py <dir>      # leser <dir>/<slug>_menu.html (lagrede kopier)

Menyene på kverneriet.com er kilden (samme markup for alle tre): <h1 class="section"> = seksjon,
<h2 class="dish"> med <span class="price"> = rett, <p> = beskrivelse (<strong> = uthevet),
<ul class="allergens"> = allergener (kode i parentes = «kan inneholde»), <h2 class="dish"> uten pris
eller <p><strong>…</strong></p> = undergruppe (oppgraderinger/dipper/topping) med <p class="subItm">-rader.
Allergen-nøkkelen leses fra data-content-attributtene på siden, så den er alltid den kjøkkenet bruker.
Rettene beholdes ordrett på engelsk, som på den ekte menyen (skrivefeil bevart)."""
import re, sys, os, json, html, urllib.request, datetime
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

V = json.load(open('content/venues.json', encoding='utf-8'))
PHOTOS = {'majorstua': ('/assets/img/g-burger.jpg', 'Crispy chicken-burger på tallerken, Kverneriet Majorstua'),
          'solli': ('/assets/img/meny-solli.jpg', 'Burger på marmorbord, Kverneriet Solli'),
          'tonsberg': ('/assets/img/meny-tonsberg.jpg', 'Burger med crispy kylling, Kverneriet Tønsberg')}
# Norske allergennavn til nøkkelen (koden er kjøkkenets, navnet vises i nøkkelen på menysiden)
NAMES = {'Egg': 'Egg', 'Wheat': 'Gluten (hvete)', 'Milk': 'Melk', 'Nuts': 'Nøtter', 'Peanuts': 'Peanøtter',
         'Mustard': 'Sennep', 'Soy': 'Soya', 'Celery': 'Selleri', 'Fish': 'Fisk', 'Sesame': 'Sesam',
         'Sulfite': 'Sulfitt', 'Shellfish': 'Skalldyr', 'Sulfur': 'Svoveldioksid', 'Lupin': 'Lupin', 'Molluscs': 'Bløtdyr',
         'Pistachios': 'Pistasjnøtter', 'Almond': 'Mandler'}

def fetch(slug, src_dir):
    if src_dir:
        return open(os.path.join(src_dir, f'{slug}_menu.html'), encoding='utf-8', errors='ignore').read()
    req = urllib.request.Request(f'https://kverneriet.com/{slug}/menu/', headers={'User-Agent': 'Mozilla/5.0 (kverneriet-site importer)'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'ignore')

def clean(s):
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()

def parse_allergens(block, key):
    """Returnerer (allergener, kanskje-allergener, pris-delta) fra en <ul class="allergens">."""
    al, maybe, delta = [], [], ''
    for m in re.finditer(r'<li(?: class="([^"]*)")?>(.*?)</li>', block, re.S):
        cls, inner = m.group(1) or '', m.group(2)
        if 'price' in cls:
            delta = clean(inner); continue
        a = re.search(r'data-content="([^"]+)">\s*(\(?)([A-Z]+)\)?\s*</a>', inner)
        if not a: continue
        desc, paren, code = a.groups()
        key.setdefault(code, desc)
        (maybe if paren else al).append(code)
    return al, maybe, delta

def parse_menu(src, key):
    i = src.find('menu-wrp'); j = src.find('</main>', i)
    body = src[i:j]
    # Tokeniser: seksjonsoverskrifter, retter, undergruppe-titler, subItm-rader, avsnitt, allergenlister
    tok = re.compile(r'<div id="([a-z-]+)" class="anchor"></div>\s*<h1 class="section">(.*?)</h1>'
                     r'|<h1 id="([a-z-]+)" class="section following">(.*?)</h1>'
                     r'|<h2 class="dish">(.*?)</h2>'
                     r'|<p class="subItm">(.*?)</p>'
                     r'|<p(?: style="[^"]*")?>(.*?)</p>'
                     r'|<ul class="allergens( subLi)?">(.*?)</ul>', re.S)
    sections, sec, item, group = [], None, None, None
    for m in tok.finditer(body):
        if m.group(1) or m.group(3):
            sid = m.group(1) or m.group(3); title = clean(m.group(2) or m.group(4))
            sec = {'id': sid, 'label': title, 'title': title, 'items': []}; sections.append(sec); item = group = None
        elif m.group(5) is not None:
            raw = m.group(5)
            pm = re.search(r'<span class="price">(.*?)</span>', raw)
            if pm:
                item = {'name': clean(raw[:pm.start()]), 'price': clean(pm.group(1))}
                sec['items'].append(item); group = None
            else:  # undergruppe (Upgrades & Extras / Give me an upgrade / Dips / Select your topping!)
                group = {'title': clean(raw), 'rows': []}; sec.setdefault('groups', []).append(group); item = None
        elif m.group(6) is not None:
            raw = m.group(6)
            nm = re.search(r'<span class="newRow">(.*?)</span>', raw, re.S)
            row = {'name': clean(re.sub(r'&#10172;|➼', '', raw[:nm.start()] if nm else raw))}
            if nm:
                note = nm.group(1)
                em = re.search(r'<strong>(.*?)</strong>', note)
                row['note'] = clean(note if not em else note[:em.start()] + ' ' + em.group(1))
            if group is None:
                group = {'title': 'Extras', 'rows': []}; sec.setdefault('groups', []).append(group)
            group['rows'].append(row); item = None
        elif m.group(7) is not None:
            raw = m.group(7)
            if re.fullmatch(r'\s*<strong>(.*?)</strong>\s*', raw, re.S):  # «Build your own»
                group = {'title': clean(raw), 'rows': []}; sec.setdefault('groups', []).append(group); item = None
            elif item is not None and 'description' not in item:
                em = re.search(r'<strong>(.*?)</strong>\s*$', raw, re.S)
                if em:
                    item['description'] = clean(raw[:em.start()]); item['emphasis'] = clean(em.group(1))
                else:
                    item['description'] = clean(raw)
                if not item['description']: item.pop('description')
            elif sec is not None and not sec['items'] and 'intro' not in sec:
                link = re.search(r'<a href="([^"]+)">', raw)
                if link and 'pdf' in link.group(1).lower():
                    sec['pdf'] = link.group(1)
                else:
                    sec['intro'] = clean(raw)
        else:
            sub, block = m.group(8), m.group(9)
            al, maybe, delta = parse_allergens(block, key)
            target = group['rows'][-1] if (sub and group and group['rows']) else item
            if target is None: continue
            if al: target['allergens'] = al
            if maybe: target['maybeAllergens'] = maybe
            if delta: target['delta'] = delta
    # Sett undergrupper i skjemaet meny.js forstår: første = upgrades, «Dips» = dips
    for s in sections:
        for g in s.pop('groups', []):
            for r in g['rows']: r.setdefault('delta', '')
            if g['title'].lower().startswith('dips'): s['dipsTitle'], s['dips'] = g['title'], g['rows']
            elif 'upgrades' not in s: s['upgradesTitle'], s['upgrades'] = g['title'], g['rows']
            else: s['upgrades'] += g['rows']
    return sections

def main():
    src_dir = sys.argv[1] if len(sys.argv) > 1 else None
    key = {}
    venues = []
    for v in V['venues']:
        src = fetch(v['slug'], src_dir)
        sections = parse_menu(src, key)
        photo, label = PHOTOS[v['slug']]
        venues.append({
            'slug': v['slug'], 'name': v['name'], 'city': v['city'], 'tagline': v['tagline'],
            'venuePage': f'/{v["slug"]}/', 'menuPage': f'/{v["slug"]}/menu/',
            'pickup': v['channels']['pickup'], 'zenchef': v['zenchef'],
            'menu': {'updated': datetime.date.today().isoformat(), 'source': f'kverneriet.com/{v["slug"]}/menu/ (importert ordrett)',
                     'photo': photo, 'photoLabel': label,
                     'drinksPdf': v['menuPdf']['drinks'], 'kidsPdf': v['menuPdf']['kids'], 'sections': sections}})
        n = sum(len(s['items']) for s in sections)
        print(f'{v["slug"]}: {len(sections)} seksjoner, {n} retter, allergenkoder {sorted(key)}')
    order = ['E', 'H', 'M', 'N', 'P', 'PN', 'MA', 'SN', 'SY', 'SL', 'F', 'SD', 'SS', 'S', 'SV']
    allergen_key = {k: NAMES.get(key[k], key[k]) for k in sorted(key, key=lambda k: order.index(k) if k in order else 99)}
    out = {'allergenKey': allergen_key, 'venues': venues}
    head = ('// Kverneriet — innholdslaget. Dette er filen et CMS ville publisert.\n'
            '// Generert av tools/import-menus.py fra kverneriet.com/<restaurant>/menu/ — rediger der (eller her) og kjør\n'
            '// python3 tools/import-menus.py && python3 tools/build.py\n')
    open('content/menus.js', 'w', encoding='utf-8').write(head + 'window.KV_CONTENT=' + json.dumps(out, ensure_ascii=False, indent=2) + ';\n')
    print('content/menus.js skrevet; allergennøkkel:', allergen_key)

if __name__ == '__main__':
    main()
