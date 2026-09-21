#!/usr/bin/env python3
"""Henter innholdet fra Sanity (prosjekt u0hod2sg, datasett production) og skriver content/-filene som
tools/build.py bygger fra: venues.json, menus.js, press.json, landing.json, site-copy.json, blog.json.

Kjør: python3 tools/fetch_sanity.py            (før python3 tools/build.py)
Miljø: SANITY_READ_TOKEN kreves bare hvis datasettet er privat. Uten nett/tilgang beholdes filene som ligger der,
så bygget virker uansett – scriptet avslutter med kode 2 så CI kan velge å stoppe."""
import json, os, sys, urllib.request, urllib.parse, re, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv
os.chdir(kv.ROOT)

PROJECT, DATASET, API = 'u0hod2sg', 'production', 'v2025-02-19'
TOKEN = os.environ.get('SANITY_READ_TOKEN', '')

def q(groq, params=None):
    url = f'https://{PROJECT}.api.sanity.io/{API}/data/query/{DATASET}?' + urllib.parse.urlencode({'query': groq, 'perspective': 'published', **{f'${k}': json.dumps(v) for k, v in (params or {}).items()}})
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {TOKEN}'} if TOKEN else {})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)['result']

IMG = '{"url": @.asset->url, "alt": alt, "w": @.asset->metadata.dimensions.width, "h": @.asset->metadata.dimensions.height}'
def img(field): return f'"{field}": {field}{IMG}'
def imgs(field): return f'"{field}": {field}[]{IMG}'

def main():
    try:
        settings = q('*[_id == "siteSettings"][0]')
    except Exception as ex:
        print(f'fetch_sanity: fikk ikke kontakt med Sanity ({ex}). Beholder content/ som det er.'); sys.exit(2)
    if not settings:
        print('fetch_sanity: datasettet er tomt (kjør tools/sanity_seed.py + sanity dataset import først). Beholder content/.'); sys.exit(2)

    venues = q(f'*[_type == "venue"] | order(select(slug == "majorstua" => 0, slug == "solli" => 1, 2)) {{ ..., "drinksPdf": drinksPdf.asset->url, "kidsPdf": kidsPdf.asset->url, {img("heroImage")}, {img("aboutImage")}, {imgs("gallery")}, {img("menuPhoto")} }}')
    menus = q(f'*[_type == "menu"] {{ "slug": venue->slug, updated, sections }}')
    press = q(f'*[_type == "pressItem"] | order(order asc) {{ ..., "key": key.current, {img("photo")} }}')
    landing = q(f'*[_type == "landingPage"] {{ ..., {img("heroImage")}, body[] {{ ..., _type == "photo" => {IMG} }} }}')
    posts = q(f'*[_type == "post" && defined(slug.current) && publishedAt <= now()] | order(publishedAt desc) {{ ..., "slug": slug.current, "updatedAt": _updatedAt, {img("mainImage")}, body[] {{ ..., _type == "photo" => {IMG} }} }}')
    faqs = q('*[_type == "faqItem"] | order(order asc) { page, question, answer, order }')

    # --- venues.json (samme form som før, + copy/seo)
    old = kv.venues(); oldv = {v['slug']: v for v in old['venues']}
    pk = settings.get('packages') or []
    org = {**old['org'], 'name': settings.get('name') or old['org']['name'], 'legalName': settings.get('legalName') or old['org'].get('legalName'),
           'telephone': settings.get('telephone') or old['org']['telephone'], 'telephoneDisplay': settings.get('telephoneDisplay') or old['org']['telephoneDisplay'],
           'email': settings.get('email') or old['org']['email'], 'founded': settings.get('founded') or old['org']['founded'], 'giftcard': settings.get('giftcard') or old['org']['giftcard'],
           'sameAs': settings.get('sameAs') or old['org']['sameAs'], 'priceRange': settings.get('priceRange') or old['org']['priceRange'],
           'deliveryMarkup': settings.get('deliveryMarkup') or old['org'].get('deliveryMarkup', '15–20 %'),
           'packages': {'note': settings.get('packagesNote') or old['org']['packages']['note'], 'items': [{'name': p['name'], 'price': p['price'], 'desc': p.get('desc', '')} for p in pk] or old['org']['packages']['items'],
                        'kids': settings.get('kidsPrice') or old['org']['packages']['kids'], 'kidsNote': settings.get('kidsNote') or old['org']['packages'].get('kidsNote', '')}}
    out_v = []
    for v in venues:
        o = oldv.get(v['slug'], {})
        c = {
            'heroSub': v.get('heroSub') or o.get('copy', {}).get('heroSub'), 'slogan': v.get('slogan') or o.get('copy', {}).get('slogan', ''),
            'about1': v.get('about1') or o.get('copy', {}).get('about1'), 'about2': v.get('about2') or o.get('copy', {}).get('about2'),
            'heroImg': v.get('heroImage') if (v.get('heroImage') or {}).get('url') else o.get('copy', {}).get('heroImg'),
            'aboutImg': v.get('aboutImage') if (v.get('aboutImage') or {}).get('url') else o.get('copy', {}).get('aboutImg'),
            'gallery': [g for g in (v.get('gallery') or []) if g.get('url')] or o.get('copy', {}).get('gallery', []),
        }
        out_v.append({
            'slug': v['slug'], 'name': v['name'], 'fullName': v['fullName'], 'city': v['city'], 'area': v.get('area', ''), 'areaCues': v.get('areaCues') or [], 'since': v.get('since', ''),
            'tagline': v.get('tagline', ''), 'address': v['address'], 'geo': {'lat': v['geo']['lat'], 'lng': v['geo']['lng']} if v.get('geo') else o.get('geo'),
            'maps': v.get('maps') or o.get('maps'), 'facebook': v.get('facebook'), 'email': v.get('email'), 'zenchef': v.get('zenchef'), 'groupThreshold': v.get('groupThreshold') or 8,
            'hours': {'kitchen': [{'days': h['days'], 'opens': h['opens'], 'closes': h['closes']} for h in v.get('kitchen') or []], 'bar': [{'days': h['days'], 'closes': h['closes']} for h in v.get('bar') or []]},
            'lunch': v.get('lunch', ''), 'channels': {'pickup': (v.get('channels') or {}).get('pickup'), 'wolt': (v.get('channels') or {}).get('wolt'), 'foodora': (v.get('channels') or {}).get('foodora')},
            'menuPdf': {'drinks': v.get('drinksPdf') or o.get('menuPdf', {}).get('drinks'), 'kids': v.get('kidsPdf') or o.get('menuPdf', {}).get('kids')},
            'copy': c, 'seo': o.get('seo', {}),
        })
    json.dump({'_comment': f'Generert av tools/fetch_sanity.py {datetime.date.today().isoformat()} – rediger i Sanity, ikke her.', 'org': org, 'venues': out_v}, open('content/venues.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    # --- menus.js
    oldm = kv.menus(); oldmv = {m['slug']: m for m in oldm['venues']}
    key = {a['code']: a['name'] for a in (settings.get('allergenKey') or [])} or oldm['allergenKey']
    mv = []
    for v in out_v:
        m = next((x for x in menus if x['slug'] == v['slug']), None); om = oldmv.get(v['slug'], {})
        sections = []
        for s in (m or {}).get('sections') or []:
            d = {'id': (s.get('id') or {}).get('current') or re.sub(r'[^a-z0-9]+', '-', s['title'].lower()), 'label': s['title'], 'title': s['title']}
            if s.get('intro'): d['intro'] = s['intro']
            d['items'] = [{k: it[k] for k in ('name', 'price', 'description', 'emphasis', 'quote', 'allergens', 'maybeAllergens') if it.get(k)} for it in s.get('items') or []]
            if s.get('upgrades'): d['upgradesTitle'] = s.get('upgradesTitle') or 'Extras'; d['upgrades'] = [{k: u.get(k, '') for k in ('name', 'note', 'delta', 'allergens') if u.get(k) or k == 'delta'} for u in s['upgrades']]
            if s.get('dips'): d['dipsTitle'] = s.get('dipsTitle') or 'Dips'; d['dips'] = [{k: u.get(k, '') for k in ('name', 'note', 'delta', 'allergens') if u.get(k) or k == 'delta'} for u in s['dips']]
            sections.append(d)
        photo = next((x for x in venues if x['slug'] == v['slug']), {}).get('menuPhoto') or {}
        mv.append({'slug': v['slug'], 'name': v['name'], 'city': v['city'], 'tagline': v['tagline'], 'venuePage': f'/{v["slug"]}/', 'menuPage': f'/{v["slug"]}/menu/', 'pickup': v['channels']['pickup'], 'zenchef': v['zenchef'],
                   'menu': {'updated': (m or {}).get('updated') or om.get('menu', {}).get('updated'), 'source': 'Sanity', 'photo': photo.get('url') or om.get('menu', {}).get('photo'), 'photoLabel': photo.get('alt') or om.get('menu', {}).get('photoLabel', ''),
                            'drinksPdf': v['menuPdf']['drinks'], 'kidsPdf': v['menuPdf']['kids'], 'sections': sections or om.get('menu', {}).get('sections', [])}})
    open('content/menus.js', 'w', encoding='utf-8').write('// Generert av tools/fetch_sanity.py – rediger menyene i Sanity, ikke her.\nwindow.KV_CONTENT=' + json.dumps({'allergenKey': key, 'venues': mv}, ensure_ascii=False, indent=2) + ';\n')

    # --- press.json (samme felter som media.py bruker)
    json.dump([{'key': p['key'], 'outlet': p['outlet'], 'title': p['title'], 'date': (p.get('date') or '')[:4], 'url': p['url'], 'rating': p.get('rating') or '', 'quote': p['quote'], 'venue': p['venue'],
                'photo': (p.get('photo') or {}).get('url', ''), 'alt': (p.get('photo') or {}).get('alt', ''), 'featured': p.get('featured', True), 'isoDate': p.get('date')} for p in press],
              open('content/press.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # --- landing.json (tekst fra Sanity, fakta/others/media fra gammel fil når de ikke er satt)
    oldl = {l['slug']: l for l in kv.landing()}
    out_l = []
    for slug in ('lunsj', 'julebord', 'selskap', 'late-night'):
        o = oldl.get(slug, {}); l = next((x for x in landing if x['slug'] == slug), None) or {}
        d = dict(o)
        for k_s, k_o in (('seoTitle', 'seoTitle'), ('seoDescription', 'seoDescription'), ('eyebrow', 'eyebrow'), ('h1', 'h1'), ('sub', 'sub'), ('sectionEyebrow', 'sec_eyebrow'), ('h2', 'h2'), ('factsTitle', 'facts_title'), ('factsNote', 'facts_note')):
            if l.get(k_s): d[k_o] = l[k_s]
        if l.get('body'): d['body'] = l['body']
        if l.get('facts'): d['facts'] = [[f['label'], f['text']] + ([f['href']] if f.get('href') else []) for f in l['facts']]
        if (l.get('heroImage') or {}).get('url'): d['img'] = l['heroImage']['url']; d['imgAlt'] = l['heroImage'].get('alt', d.get('imgAlt', ''))
        d['slug'] = slug; out_l.append(d)
    json.dump(out_l, open('content/landing.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # --- site-copy.json + blog.json
    sc = kv.site_copy()
    for k in ('brandStory', 'aboutTitle', 'about1', 'about2'):
        if settings.get(k) and settings[k].get('no'): sc[k] = settings[k]
    sc['faqExtra'] = faqs
    json.dump(sc, open('content/site-copy.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(posts, open('content/blog.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'fetch_sanity: {len(venues)} restauranter, {len(menus)} menyer, {len(press)} omtaler, {len(landing)} landingssider, {len(posts)} innlegg, {len(faqs)} ekstra FAQ')

if __name__ == '__main__':
    main()
