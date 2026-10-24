#!/usr/bin/env python3
"""Sjekker at forhåndsvisningen i Sanity Studio viser det samme som nettsiden bygger.

Studioet tegner blogginnlegg selv (studio-kverneriet/preview/postHtml.ts), fordi nettsiden er
statisk og ikke kan vise utkast. Den koden er en kopi av tools/portable.py og må holdes lik.
Dette skriptet henter alle publiserte innlegg fra Sanity, kjører begge gjengivelsene og
sammenligner resultatet tegn for tegn.

Kjør: python3 tools/check_preview_parity.py      (krever Node 23.6 eller nyere)"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv, portable as PT
from build_blog import nice_date
from fetch_sanity import q

CLI = os.path.join(kv.ROOT, 'studio-kverneriet', 'preview', 'render-cli.ts')
IMG = '"url": asset->url, "w": asset->metadata.dimensions.width, "h": asset->metadata.dimensions.height'

# Et innlegg som bruker alt redaktøren kan lage i Studio. De ekte innleggene dekker ikke
# nødvendigvis alle grenene, så dette sørger for at testen gjør det uansett.
def _b(style, *spans, key='k', marks=None, defs=None, li=None):
    blk = {'_type': 'block', '_key': key, 'style': style, 'markDefs': defs or [],
           'children': [{'_type': 'span', 'text': t, 'marks': m} for t, m in spans]}
    if li: blk['listItem'] = li
    return blk

_REF = 'image-Tb9Ew8CXIwaY6R1kjMvI0uRR-2000x3000-jpg'
_URL = 'https://cdn.sanity.io/images/u0hod2sg/production/Tb9Ew8CXIwaY6R1kjMvI0uRR-2000x3000.jpg'
FIXTURE = {
    '_id': 'fixture-alle-grener', 'title': 'Alle grener', 'publishedAt': '2026-02-01T23:30:00Z',
    'mainImage': {'_type': 'photo', 'alt': 'Hoved', 'asset': {'_ref': _REF}, 'url': _URL, 'w': 2000, 'h': 3000},
    'body': [
        _b('normal', ('Vanlig & <tekst> med «sitat» og \'apostrof\'', []), ('\nny linje', [])),
        _b('normal', ('fet', ['strong']), (' kursiv', ['em']), (' begge', ['strong', 'em'])),
        _b('normal', ('intern', ['l1']), (' ekstern', ['l2']), (' egen .com', ['l3']), (' uten href', ['l4']),
           defs=[{'_key': 'l1', '_type': 'link', 'href': '/meny/'},
                 {'_key': 'l2', '_type': 'link', 'href': 'https://vg.no/?a=1&b="2"'},
                 {'_key': 'l3', '_type': 'link', 'href': 'https://kverneriet.com/x'},
                 {'_key': 'l4', '_type': 'link'}]),
        _b('h2', ('Mellomtittel', [])),
        _b('h3', ('Liten tittel', [])),
        _b('blockquote', ('Et sitat', [])),
        _b('normal', ('punkt 1', []), li='bullet'), _b('normal', ('punkt 2', []), li='bullet'),
        _b('normal', ('nummer 1', []), li='number'),
        {'_type': 'photo', '_key': 'p1', 'alt': 'Bilde "med" anførsel', 'asset': {'_ref': _REF}, 'url': _URL, 'w': 2000, 'h': 3000},
        {'_type': 'photo', '_key': 'p2', 'alt': 'uten bilde'},
        _b('normal', ('etter bildet', [])),
        _b('h2', ('Ofte stilte spørsmål', [])),
        _b('h3', ('Spørsmål én?', [])), _b('normal', ('Svar én.', [])), _b('normal', ('Mer svar.', [])),
        _b('h3', ('Spørsmål uten svar?', [])),
        _b('h3', ('Spørsmål to?', [])), _b('normal', ('Svar to.', [])),
        _b('h2', ('Etter FAQ', [])), _b('normal', ('siste avsnitt', [])),
    ],
}

def main():
    posts = q(f'*[_type == "post"] {{ ..., mainImage {{ ..., {IMG} }}, body[] {{ ..., _type == "photo" => {{ ..., {IMG} }} }} }}')
    if not posts:
        sys.exit('fant ingen innlegg i Sanity')
    posts.append(FIXTURE)
    ts = json.loads(subprocess.run(['node', CLI], input=json.dumps(posts), capture_output=True, text=True, check=True).stdout)

    feil = 0
    for p in posts:
        t = ts[p['_id']]
        navn = p.get('title', p['_id'])
        sjekker = [
            ('brødtekst', PT.to_html(p.get('body')), t['body']),
            ('dato', nice_date(p['publishedAt']) if p.get('publishedAt') else None, t['dato']),
            ('bildeadresser', [b.get('url') for b in [p.get('mainImage')] + [x for x in p.get('body') or [] if x.get('_type') == 'photo'] if b],
             t['bilder']),
        ]
        for hva, py, js in sjekker:
            if py == js:
                continue
            feil += 1
            print(f'AVVIK  {navn}: {hva}')
            if isinstance(py, str) and isinstance(js, str):
                i = next((k for k, (a, b) in enumerate(zip(py, js)) if a != b), min(len(py), len(js)))
                print(f'   nettsiden:        …{py[max(0, i - 60):i + 80]!r}')
                print(f'   forhåndsvisning:  …{js[max(0, i - 60):i + 80]!r}')
            else:
                print(f'   nettsiden:        {py!r}\n   forhåndsvisning:  {js!r}')
    if feil:
        sys.exit(f'{feil} avvik i {len(posts)} innlegg')
    print(f'likt: {len(posts) - 1} innlegg fra Sanity + ett testinnlegg med alle grener, på brødtekst, dato og bildeadresser')

if __name__ == '__main__':
    main()
