#!/usr/bin/env python3
"""Skyver tekstendringer fra content/ opp til Sanity uten å røre bildene som allerede ligger der.
Brukes når vi har redigert content/site-copy.json eller content/venues.json lokalt og vil at Sanity
(som er kilden) skal si det samme. Henter dokumentet slik det er i Sanity, bytter bare tekstfeltene,
laster opp bilder som mangler, og skriver dokumentet tilbake.

Kjør: python3 tools/sanity_push.py            (krever `npx sanity login` i studio-kverneriet)"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv
os.chdir(kv.ROOT)
ST = 'studio-kverneriet'

def sanity(args, **kw):
    r = subprocess.run(['npx', 'sanity'] + args, cwd=ST, capture_output=True, text=True, **kw)
    if r.returncode: raise SystemExit((r.stdout + r.stderr)[-800:])
    return r.stdout

def query(groq):
    out = sanity(['documents', 'query', groq])
    return json.loads(out[out.index('['):out.rindex(']') + 1]) if '[' in out else []

_assets = None
def asset_ref(path, alt):
    """Finn (eller last opp) bildet i Sanity og returner en photo-verdi."""
    global _assets
    m = re.match(r'https://cdn\.sanity\.io/images/[^/]+/[^/]+/([0-9a-f]+)-(\d+x\d+)\.(\w+)', path or '')
    if m:  # bildet ligger allerede i Sanity
        return {'_type': 'photo', 'alt': alt, 'asset': {'_type': 'reference', '_ref': f'image-{m.group(1)}-{m.group(2)}-{m.group(3)}'}}
    name = os.path.basename(path)
    if _assets is None:
        _assets = {a['originalFilename']: a['_id'] for a in query('*[_type == "sanity.imageAsset"]{_id, originalFilename}') if a.get('originalFilename')}
    if name not in _assets:
        out = sanity(['assets', 'upload', '--type', 'image', '--file', os.path.abspath(path.lstrip('/'))])
        m = re.search(r'"_id":\s*"([^"]+)"', out)
        if not m: raise SystemExit(f'fikk ikke lastet opp {path}:\n{out[-400:]}')
        _assets[name] = m.group(1)
        print(f'  lastet opp {name}')
    return {'_type': 'photo', 'alt': alt, 'asset': {'_type': 'reference', '_ref': _assets[name]}}

def put(docs):
    nd = '/tmp/sanity-push.ndjson'
    with open(nd, 'w', encoding='utf-8') as f:
        for d in docs: f.write(json.dumps(d, ensure_ascii=False) + '\n')
    sanity(['dataset', 'import', nd, 'production', '--replace'])

def keyed(items, p='k'):
    return [{**it, '_key': f'{p}{i}'} for i, it in enumerate(items)]

def main():
    sc = kv.site_copy(); V = kv.venues()
    docs = []

    settings = query('*[_id == "siteSettings"]')[0]
    for k in ('heroSub', 'heroLede', 'aboutTitle', 'craftEyebrow', 'craftTitle'):
        if sc.get(k): settings[k] = sc[k]
    if sc.get('aboutParagraphs'): settings['aboutParagraphs'] = keyed([{'_type': 'localizedText', **p} for p in sc['aboutParagraphs']], 'p')
    if sc.get('craftItems'):
        settings['craftItems'] = keyed([{'_type': 'craftItem', 'title': c['title'], 'body': c['body'], 'photo': asset_ref(c['image'], c['alt'])} for c in sc['craftItems']], 'c')
    settings.pop('about1', None); settings.pop('about2', None)
    docs.append(settings)

    for v in query('*[_type == "venue"]'):
        src = next((x for x in V['venues'] if x['slug'] == v['slug']), None)
        if not src: continue
        c = src['copy']
        v['tagline'] = src['tagline']
        v['slogan'] = c['slogan'] if isinstance(c['slogan'], dict) else {'no': c['slogan'], 'en': c['slogan']}
        v['about1'] = c['about1']; v['about2'] = c['about2']
        docs.append(v)

    put(docs)
    print(f'sanity_push: {len(docs)} dokumenter oppdatert (tekst), bilder urørt')

if __name__ == '__main__':
    main()
