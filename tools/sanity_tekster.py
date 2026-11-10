#!/usr/bin/env python3
"""Lager ett siteText-dokument per tekst, så Kverneriet kan endre dem i Studio («Tekster på nettsiden»).

Kjør etter tools/build.py: python3 tools/sanity_tekster.py
Skriver sanity-tekster.ndjson. Ingenting sendes til Sanity herfra. Synkroniseringen gjøres med
  cd studio-kverneriet && npx sanity exec scripts/sync-tekster.ts --with-user-token
som oppdaterer standardtekst og plassering, men aldri det Kverneriet har skrevet.

Tekster som allerede kan endres et annet sted i Sanity, tas ikke med, ellers ville de hatt to hjem.
Det samme gjelder tekster som bygges rett fra åpningstidene, og nøkler som ikke vises noe sted."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv, site_texts
import build_blog  # registrerer /blogg/ og innleggene i kv.PAGES
os.chdir(kv.ROOT)

UT = 'sanity-tekster.ndjson'

# Første del av nøkkelen avgjør området. Navnene må stå likt i SITE_TEXT_AREAS i studio-kverneriet.
OMRADE = {
    'home': 'Forsiden', 'dag': 'Forsiden', 'maten': 'Maten', 'story': 'Forsiden', 'occ': 'Forsiden', 'craft': 'Forsiden', 'kar': 'Forsiden', 'media': 'Forsiden', 'press': 'Forsiden',
    'nav': 'Meny og bunnlinje', 'foot': 'Meny og bunnlinje', 'consent': 'Meny og bunnlinje', 'a11y': 'Meny og bunnlinje', 'video': 'Meny og bunnlinje', 'nf': 'Meny og bunnlinje',
    'act': 'Knapper',
    'book': 'Booking og skjema', 'f': 'Booking og skjema', 'modal': 'Booking og skjema',
    'v': 'Restaurantsidene', 'hours': 'Restaurantsidene', 'addr': 'Restaurantsidene', 'contact': 'Restaurantsidene', 'practical': 'Restaurantsidene',
    'majorstua': 'Restaurantsidene', 'solli': 'Restaurantsidene', 'tonsberg': 'Restaurantsidene', 'maj': 'Restaurantsidene', 'sol': 'Restaurantsidene', 'ton': 'Restaurantsidene',
    'menu': 'Menysiden', 'ta': 'Take-away', 'lp': 'Landingssider', 'om': 'Om og kontakt', 'kontakt': 'Om og kontakt', 'blog': 'Blogg', 'faq': 'Spørsmål og svar', 'pv': 'Personvern',
}
# Bygges fra åpningstidene eller er ukedager, eller redigeres allerede i Innstillinger, Restauranter og Landingssider.
UTELATES = re.compile(r'^(dr?\.|sh\.|maten\.[^.]+\.body$|home\.craft\.[^.]+$|.*\.barHours$|.*\.lunch$|.*\.since$|kontakt\.\w+\.kitchen$'
                      r'|home\.(heroSub|lede|aboutTitle|craftEyebrow|craftTitle)$|om\.(title|p\d+)$|craft\.\d+\.(title|sub)$|faq\.x\.'
                      r'|(majorstua|solli|tonsberg)\.(heroSub|slogan|about1|about2)$)')
TIDER = re.compile(r'\d{1,2}[.:]\d{2}|\d+\s*kr\b|\bkr\s*\d+', re.I)
SIDENAVN = {'index.html': 'Forsiden'}
# Den lille linjen over overskriften er feltet heroSub under Innstillinger, ikke en egen tekst her.
FASTE_STANDARD = {'home.h1': 'Overskriften øverst på forsiden',
                  'ta.badge': 'Merket øverst på take-away-siden', 'ta.h1': 'Overskriften på take-away-siden'}


def ordbok():
    """Hele ordboken slik siden bruker den: i18n.js med i18n-gen.js oppå."""
    base = site_texts.grunnordbok()
    s = open('content/i18n-gen.js', encoding='utf-8').read()
    gen = json.loads(s[s.index('=') + 1:s.rindex(';')])
    return {sprak: {**base[sprak], **gen[sprak]} for sprak in ('no', 'en')}


def fra_sanity():
    """Alle tekstbiter som allerede kommer fra andre dokumenter i Sanity. storyCards ligger bare i JSON-filen."""
    biter = set()
    def gaa(o):
        if isinstance(o, str):
            biter.add(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', o)).strip())
        elif isinstance(o, dict):
            for k, v in o.items():
                if k != 'storyCards': gaa(v)
        elif isinstance(o, list):
            for v in o: gaa(v)
    for navn in ('venues', 'landing', 'press', 'blog', 'site-copy'):
        gaa(kv.load_json(f'{navn}.json', {}))
    return biter


def sidenavn(fil):
    return SIDENAVN.get(fil) or '/' + fil.replace('index.html', '').strip('/') + '/'


def hvor(sider):
    if not sider: return 'I skjemaer og meldinger'
    if len(sider) >= 15: return 'Alle sider'
    navn = [sidenavn(f) for f in sider]
    return ', '.join(navn) if len(navn) <= 3 else f'{", ".join(navn[:3])} og {len(navn) - 3} til'


def main():
    filer = [f for f in kv.all_files() + ['404.html'] if os.path.exists(f)]
    html = {f: open(f, encoding='utf-8').read() for f in filer}
    d = ordbok()
    finnes = fra_sanity()
    js = open('site.js', encoding='utf-8').read() + open('meny.js', encoding='utf-8').read()
    plass, forst = {}, {}
    for f in filer:  # forsiden kommer først i kv.PAGES, så rekkefølgen følger siden ovenfra og ned
        for m in re.finditer(r'data-i18n(?:-html|-title|-ph|-label)?="([^"]+)"', html[f]):
            plass.setdefault(m.group(1), [])
            if f not in plass[m.group(1)]: plass[m.group(1)].append(f)
            forst.setdefault(m.group(1), len(forst))
    nokler = sorted(set(d['no']) | set(plass), key=lambda k: (forst.get(k, 10 ** 6), k))

    dok, utelatt, ids = [], 0, {}
    def i_sanity(tekst):  # korte ord som «Lunsj» kan stå begge steder uten at det er samme tekst
        ren = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', tekst)).strip()
        return len(ren) >= 40 and ren in finnes
    for i, k in enumerate(nokler):
        no = d['no'].get(k)
        if not no or UTELATES.match(k) or i_sanity(no) or (k not in plass and k not in js):
            utelatt += 1; continue
        _id = 'tekst-' + re.sub(r'[^A-Za-z0-9_-]', '-', k)
        if _id in ids: raise SystemExit(f'{k} og {ids[_id]} får samme dokument-ID')
        ids[_id] = k
        merknader = []
        if TIDER.search(no): merknader.append('Inneholder tider eller priser. Endrer du teksten, må de oppdateres for hånd etterpå.')
        if re.search(r'<[a-z]', no): merknader.append('Inneholder lenker. La <a href="...">-delen stå.')
        plassholdere = re.findall(r'\{\w+\}', no)
        if plassholdere: merknader.append(f'Behold {" og ".join(plassholdere)}. Det fylles inn av nettsiden.')
        rad = {'_id': _id, '_type': 'siteText', 'key': k, 'omrade': OMRADE.get(k.split('.')[0], 'Annet'), 'hvor': hvor(plass.get(k, [])),
               'rekkefolge': i, 'standardNo': no, 'standardEn': d['en'].get(k, '')}
        if merknader: rad['merknad'] = ' '.join(merknader)
        dok.append(rad)

    for j, (k, fil, monster) in enumerate(site_texts.FASTE):
        m = re.search(monster, html.get(fil, ''), flags=re.S)
        if not m: raise SystemExit(f'fant ikke {k} i {fil}')
        dok.append({'_id': 'tekst-' + k.replace('.', '-'), '_type': 'siteText', 'key': k, 'omrade': 'Forsiden' if fil == 'index.html' else 'Take-away',
                    'hvor': FASTE_STANDARD[k], 'rekkefolge': -len(site_texts.FASTE) + j, 'standardNo': m.group(2).strip(), 'fast': True})

    with open(UT, 'w', encoding='utf-8') as f:
        for rad in dok: f.write(json.dumps(rad, ensure_ascii=False) + '\n')
    print(f'{UT}: {len(dok)} tekster, {utelatt} utelatt (finnes andre steder i Sanity, kommer fra åpningstidene eller vises ikke)')


if __name__ == '__main__':
    main()
