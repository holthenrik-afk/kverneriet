#!/usr/bin/env python3
"""Tekster Kverneriet endrer selv i Sanity («Tekster på nettsiden», dokumenttypen siteText).

Standardtekstene ligger der de alltid har ligget: i tools/, content/i18n.js og index.html. Sanity holder
bare det som er endret, så et tomt felt betyr standardteksten, og en endring i koden slår gjennom så lenge
ingen har overstyrt akkurat den teksten. fetch_sanity.py skriver overstyringene til content/site-texts.json.

apply() kjøres sist i tools/build.py, etter at alle sidene er bygget, men før G.write() og seo_head, så
ordboken, HTML-en og FAQPage-markupen sier det samme. En overstyring som ikke kan brukes, hoppes over med
en advarsel. Den skal aldri kunne stoppe bygget eller ødelegge en side.

index.html og takeaway/index.html er både kilde og resultat i bygget. CI bygger fra det som ligger i repoet og
skriver ikke tilbake, men committes en lokal bygging med overstyringer, blir linjene i FASTE stående til de
rettes for hånd. Resten retter seg selv, fordi tools/ eller ordboken skriver dem på nytt.

Selve utvalget i Studio lages av tools/sanity_tekster.py."""
import ast, os, re, sys
from html.parser import HTMLParser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv, i18n_gen as G

# Linjer uten språkbytte: merkevarelinjer og overskrifter som står likt på norsk og engelsk.
# (nøkkel, fil, mønster med tekst i gruppe 2). Teksten byttes uten å legge til data-i18n,
# fordi build.py leser disse linjene tilbake med mønstre som krever at taggen står urørt.
FASTE = [
    ('home.h1',        'index.html',          r'(<section class="hero-home.*?<h1\b[^>]*>)([^<]*)(</h1>)'),
    ('ta.badge',       'takeaway/index.html', r'(<span class="badge"[^>]*>)([^<]*)(</span>)'),
    ('ta.h1',          'takeaway/index.html', r'(<h1 class="hero-title"[^>]*>)([^<]*)(</h1>)'),
]

_LEDD = re.compile(r"""'([\w.-]+)':\s*('(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")""")
TILLATTE = {'a', 'b', 'strong', 'em', 'i', 'br'}


def grunnordbok():
    """content/i18n.js som {'no': {...}, 'en': {...}}."""
    s = open(os.path.join(kv.ROOT, 'content/i18n.js'), encoding='utf-8').read()
    no, en = re.split(r'\n\s*en:\s*\{', s, maxsplit=1)
    return {'no': {k: ast.literal_eval(v) for k, v in _LEDD.findall(no)},
            'en': {k: ast.literal_eval(v) for k, v in _LEDD.findall(en)}}


class _Sjekk(HTMLParser):
    """Godtar bare enkle tagger og lukkede lenker, så en skrivefeil ikke kan velte en side."""
    def __init__(self):
        super().__init__(); self.apne = []; self.feil = None
    def handle_starttag(self, tag, attrs):
        if tag not in TILLATTE: self.feil = f'taggen <{tag}> er ikke tillatt'
        if tag == 'a' and not re.match(r'(/|https?://|mailto:|tel:|#)', dict(attrs).get('href') or ''): self.feil = 'ugyldig lenke'
        if tag != 'br': self.apne.append(tag)
    def handle_endtag(self, tag):
        if tag == 'br': return
        if not self.apne or self.apne.pop() != tag: self.feil = f'</{tag}> står feil'


def html_feil(verdi):
    p = _Sjekk(); p.feed(verdi); p.close()
    if '<' in re.sub(r'<[^<>]*>', '', verdi): return 'en tagg er ikke lukket'
    return p.feil or (f'<{p.apne[-1]}> er ikke lukket' if p.apne else None)


def _html_nokler(sider):
    return {k for s in sider.values() for k in re.findall(r'data-i18n-html="([^"]+)"', s)}


def _vask(data, kjente, html_nokler, base):
    """Lar bare gjennom overstyringer som er trygge å bruke. Resten får en advarsel."""
    ren = {'no': {}, 'en': {}}
    for nokkel, felt in data.items():
        if not isinstance(felt, dict): continue
        if nokkel not in kjente:
            print(f'  tekster: hopper over {nokkel}, nøkkelen finnes ikke lenger'); continue
        for sprak in ('no', 'en'):
            verdi = str(felt.get(sprak) or '').strip()
            if not verdi: continue
            standard = G._D[sprak].get(nokkel) or base[sprak].get(nokkel) or ''
            mangler = set(re.findall(r'\{\w+\}', standard)) - set(re.findall(r'\{\w+\}', verdi))
            if mangler:
                print(f'  tekster: hopper over {nokkel} ({sprak}), mangler {", ".join(sorted(mangler))}'); continue
            if nokkel in html_nokler:
                feil = html_feil(verdi)
                if feil:
                    print(f'  tekster: hopper over {nokkel} ({sprak}), {feil}'); continue
            ren[sprak][nokkel] = verdi
    return ren


_ELEMENT = re.compile(r'<([a-zA-Z][\w-]*)((?:\s[^<>]*?)?\sdata-i18n="([^"]+)"[^<>]*)>([^<]*)</\1>')


def _sett_tekst(side, over):
    def bytt(m):
        tag, attrs, nokkel = m.group(1), m.group(2), m.group(3)
        if nokkel not in over: return m.group(0)
        verdi = over[nokkel]
        n = re.search(r'\sdata-i18n-n="([^"]*)"', attrs)
        if n: verdi = verdi.replace('{n}', n.group(1))
        attrs = re.sub(r'(\sdata-label=")[^"]*"', lambda a: a.group(1) + kv.esc(verdi) + '"', attrs)
        return f'<{tag}{attrs}>{kv.esc(verdi)}</{tag}>'
    return _ELEMENT.sub(bytt, side)


def _sett_html(side, over):
    """data-i18n-html kan inneholde lenker, så sluttaggen finnes ved å telle dybden."""
    ut, pos = [], 0
    for m in re.finditer(r'<([a-zA-Z][\w-]*)(?:\s[^<>]*?)?\sdata-i18n-html="([^"]+)"[^<>]*>', side):
        if m.group(2) not in over or m.start() < pos: continue
        dybde, slutt = 1, None
        for t in re.finditer(r'<(/?)%s\b[^<>]*>' % re.escape(m.group(1)), side[m.end():]):
            dybde += -1 if t.group(1) else 1
            if dybde == 0:
                slutt = m.end() + t.start(); break
        if slutt is None: continue
        ut += [side[pos:m.end()], over[m.group(2)]]; pos = slutt
    return ''.join(ut) + side[pos:]


def _sett_attr(side, data, attr, over):
    def bytt(m):
        nokkel = re.search(r'\s%s="([^"]+)"' % data, m.group(0)).group(1)
        if nokkel not in over: return m.group(0)
        return re.sub(r'(\s%s=")[^"]*"' % attr, lambda a: a.group(1) + kv.esc(over[nokkel]) + '"', m.group(0))
    return re.sub(r'<[a-zA-Z][^<>]*\s%s="[^"]+"[^<>]*>' % data, bytt, side)


def _sett_faste(sider, over):
    for nokkel, fil, monster in FASTE:
        if nokkel not in over or fil not in sider: continue
        ny, n = re.subn(monster, lambda m: m.group(1) + kv.esc(over[nokkel]) + m.group(3), sider[fil], count=1, flags=re.S)
        if n: sider[fil] = ny
        else: print(f'  tekster: fant ikke {nokkel} i {fil}')


def apply():
    """Legger overstyringene fra content/site-texts.json oppå sidene og ordboken. Feiler aldri bygget."""
    try:
        _apply()
    except Exception as ex:
        print(f'  tekster: bruker standardtekstene, fikk ikke lagt på endringene ({ex})')


def _apply():
    data = kv.load_json('site-texts.json', {}) or {}
    if not data:
        print('ingen endrede tekster'); return
    filer = [f for f in kv.all_files() + ['404.html'] if os.path.exists(os.path.join(kv.ROOT, f))]
    sider = {f: open(os.path.join(kv.ROOT, f), encoding='utf-8').read() for f in filer}
    base = grunnordbok()
    kjente = set(G._D['no']) | set(base['no']) | {n for n, _, _ in FASTE}
    ren = _vask(data, kjente, _html_nokler(sider), base)
    over = ren['no']
    for f, s in list(sider.items()):
        s = _sett_tekst(s, over)
        s = _sett_html(s, over)
        for attr_data, attr in (('data-i18n-ph', 'placeholder'), ('data-i18n-label', 'aria-label'), ('data-i18n-title', 'title')):
            s = _sett_attr(s, attr_data, attr, over)
        sider[f] = s
    _sett_faste(sider, over)
    for f, s in sider.items():
        open(os.path.join(kv.ROOT, f), 'w', encoding='utf-8').write(s)
    faste = {n for n, _, _ in FASTE}
    for sprak in ('no', 'en'):
        for nokkel, verdi in ren[sprak].items():
            if nokkel not in faste: G._D[sprak][nokkel] = verdi
    print(f'{len(over)} endrede tekster på norsk, {len(ren["en"])} på engelsk')
