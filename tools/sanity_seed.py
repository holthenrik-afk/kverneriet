#!/usr/bin/env python3
"""Lager et NDJSON-datasett av dagens innhold (venues.json, menus.js, media.py, landingssider) som lastes inn i
Sanity én gang:  python3 tools/sanity_seed.py && cd studio-kverneriet && npx sanity dataset import ../sanity-seed.ndjson production --replace
Bilder og PDF-er lastes opp av importen via _sanityAsset-referanser til lokale filer. Etter dette er Sanity kilden;
tools/fetch_sanity.py skriver innholdet tilbake til content/ før bygging."""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv
import media as MD
os.chdir(kv.ROOT)

V = kv.venues(); ORG = V['org']; M = kv.menus()
rows = []
def img(path, alt, key=None):
    if not path: return None
    d = {'_type': 'photo', '_sanityAsset': 'image@file://' + os.path.abspath(path.lstrip('/')), 'alt': alt}
    if key: d['_key'] = key
    return d
def file_asset(path):
    return {'_type': 'file', '_sanityAsset': 'file@file://' + os.path.abspath(path.lstrip('/'))} if path and os.path.exists(path.lstrip('/')) else None
def keyed(items):
    return [{**it, '_key': f'k{i}'} for i, it in enumerate(items)]
def loc(no, en=None): return {'no': no, 'en': en or no}

# --- Innstillinger
import seo_head as SH  # BRAND-teksten
rows.append({
    '_id': 'siteSettings', '_type': 'siteSettings', 'name': ORG['name'], 'legalName': ORG.get('legalName'), 'telephone': ORG['telephone'],
    'telephoneDisplay': ORG['telephoneDisplay'], 'email': ORG['email'], 'giftcard': ORG['giftcard'], 'founded': ORG['founded'], 'sameAs': ORG['sameAs'],
    'priceRange': ORG['priceRange'], 'deliveryMarkup': ORG.get('deliveryMarkup', '15–20 %'), 'packagesNote': ORG['packages']['note'],
    'packages': keyed([{'_type': 'packageItem', **p} for p in ORG['packages']['items']]), 'kidsPrice': ORG['packages']['kids'], 'kidsNote': ORG['packages'].get('kidsNote'),
    'brandStory': loc(SH.BRAND, 'Kverneriet is a Norwegian burger restaurant started in Tønsberg in 2013, with restaurants at Majorstua (2015) and Solli plass (2017) in Oslo. We grind all the beef ourselves from top-grade cattle, cook the burgers medium plus, make triple-cooked fries that take three days and serve Jersey-milk soft serve and milkshakes. Our take-away packaging is our own, in natural materials.'),
    'aboutTitle': loc('Burgersjappa fra Tønsberg som ble tre restauranter', 'The Tønsberg burger joint that became three restaurants'),
    'about1': loc('Kverneriet startet som en liten burgersjappe i Tønsberg i 2013. I 2015 åpnet vi på Majorstua i Oslo, og i 2017 ved Solli plass. Oppskriften er den samme alle tre steder: vi kverner alt kjøttet selv av storfe i toppklasse og steker burgerne medium pluss, brødene er ferske, og friesene er håndlagde, trippelkokte og tar tre dager – naturlig glutenfrie.',
                  'Kverneriet started as a small burger joint in Tønsberg in 2013. In 2015 we opened at Majorstua in Oslo, and in 2017 at Solli plass. The recipe is the same in all three: we grind all the beef ourselves from top-grade cattle and cook the burgers medium plus, the buns are fresh, and the fries are handmade, triple-cooked and take three days – naturally gluten-free.'),
    'allergenKey': keyed([{'_type': 'allergenCode', 'code': c, 'name': n} for c, n in M['allergenKey'].items()]),
})

# --- Restauranter + menyer (om-tekster og bilder fra build_venue.py)
import build_venue as BV
for v in V['venues']:
    s = v['slug']; c = BV.COPY[s]; mv = next(x for x in M['venues'] if x['slug'] == s)
    rows.append({
        '_id': f'venue-{s}', '_type': 'venue', 'slug': s, 'name': v['name'], 'fullName': v['fullName'], 'city': v['city'], 'area': v['area'], 'areaCues': v['areaCues'],
        'since': v['since'], 'tagline': v['tagline'], 'address': v['address'], 'geo': {'_type': 'geopoint', 'lat': v['geo']['lat'], 'lng': v['geo']['lng']},
        'maps': v['maps'], 'facebook': v['facebook'], 'email': v['email'],
        'kitchen': keyed([{'_type': 'kitchenHours', **h} for h in v['hours']['kitchen']]), 'bar': keyed([{'_type': 'barHours', **h} for h in v['hours']['bar']]),
        'lunch': v['lunch'], 'zenchef': v['zenchef'], 'groupThreshold': v['groupThreshold'],
        'channels': {k: u for k, u in v['channels'].items() if u},
        'drinksPdf': file_asset(v['menuPdf']['drinks']), 'kidsPdf': file_asset(v['menuPdf']['kids']),
        'heroImage': img(kv.abs_url(s) and __import__('pages').PAGES[s]['img'], c['heroAlt']),
        'heroSub': loc(*c['heroSub']), 'slogan': c['slogan'],
        'about1': loc(*c['about'][0]), 'about2': loc(*c['about'][1]),
        'aboutImage': img(c['aboutImg'][0], c['aboutImg'][1]),
        'gallery': [img(p, a, f'g{i}') for i, (p, a, _) in enumerate(c['gallery'])],
        'menuPhoto': img(mv['menu']['photo'], mv['menu']['photoLabel']),
    })
    sections = []
    for i, sec in enumerate(mv['menu']['sections']):
        d = {'_type': 'menuSection', '_key': f's{i}', 'id': {'_type': 'slug', 'current': sec['id']}, 'title': sec['title'], 'intro': sec.get('intro'),
             'items': keyed([{'_type': 'menuItem', **{k: it[k] for k in ('name', 'price', 'description', 'emphasis', 'quote', 'allergens', 'maybeAllergens') if k in it}} for it in sec['items']])}
        if sec.get('upgrades'): d['upgradesTitle'] = sec.get('upgradesTitle'); d['upgrades'] = keyed([{'_type': 'menuAddon', **u} for u in sec['upgrades']])
        if sec.get('dips'): d['dipsTitle'] = sec.get('dipsTitle'); d['dips'] = keyed([{'_type': 'menuAddon', **u} for u in sec['dips']])
        sections.append({k: x for k, x in d.items() if x is not None})
    rows.append({'_id': f'menu-{s}', '_type': 'menu', 'venue': {'_type': 'reference', '_ref': f'venue-{s}'}, 'updated': mv['menu']['updated'], 'sections': sections})

# --- Presse
CONF = {i['url']: i for i in json.load(open('tools/press-confirmed-2026-09-15.json', encoding='utf-8'))}
for i, m in enumerate(MD.MEDIA):
    date = CONF.get(m['url'], {}).get('date') or f"{m['date']}-01-01"
    rows.append({'_id': f'press-{m["key"]}', '_type': 'pressItem', 'key': {'_type': 'slug', 'current': m['key']}, 'outlet': m['outlet'], 'title': m['title'], 'date': date,
                 'url': m['url'], 'rating': m['rating'] or None, 'quote': m['quote'], 'venue': m['venue'], 'photo': img(m['photo'], m['alt']), 'featured': True, 'order': i})

# --- Landingssider (tekstene fra build_landing.py)
import build_landing as BL, pages
def rt(paragraphs):
    out = []
    for i, p in enumerate(paragraphs):
        # enkel konvertering: <a href="x">y</a> → lenke-mark, ellers ren tekst
        children, marks = [], []; pos = 0; k = 0
        for mm in re.finditer(r'<a href="([^"]+)">(.*?)</a>', p):
            if mm.start() > pos: children.append({'_type': 'span', '_key': f'c{k}', 'text': re.sub('<[^>]+>', '', p[pos:mm.start()]), 'marks': []}); k += 1
            mk = f'l{k}'; marks.append({'_type': 'link', '_key': mk, 'href': mm.group(1)})
            children.append({'_type': 'span', '_key': f'c{k}', 'text': mm.group(2), 'marks': [mk]}); k += 1; pos = mm.end()
        if pos < len(p): children.append({'_type': 'span', '_key': f'c{k}', 'text': re.sub('<[^>]+>', '', p[pos:]), 'marks': []})
        out.append({'_type': 'block', '_key': f'b{i}', 'style': 'normal', 'markDefs': marks, 'children': children})
    return out
for p in BL.PAGES:
    meta = pages.PAGES[p['slug']]
    rows.append({'_id': f'landing-{p["slug"]}', '_type': 'landingPage', 'slug': p['slug'], 'seoTitle': meta['title'], 'seoDescription': meta['desc'],
                 'eyebrow': p['eyebrow'], 'h1': p['h1'], 'sub': p['sub'], 'heroImage': img(meta['img'], p['imgAlt']), 'sectionEyebrow': p['sec_eyebrow'], 'h2': p['h2'],
                 'body': rt(p['body']), 'factsTitle': p['facts_title'], 'facts': keyed([{'_type': 'fact', 'label': f[0], 'text': f[1], **({'href': f[2]} if len(f) > 2 and f[2] else {})} for f in p['facts']]),
                 'factsNote': p['facts_note']})

with open('sanity-seed.ndjson', 'w', encoding='utf-8') as f:
    for r in rows: f.write(json.dumps({k: x for k, x in r.items() if x is not None}, ensure_ascii=False) + '\n')
print(f'sanity-seed.ndjson: {len(rows)} dokumenter')
