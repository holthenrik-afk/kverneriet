"""Felles for generatorene: sideregister, URL-er og innholdslaget.

URL-strukturen følger kverneriet.com slik den var indeksert (kverneriet.com 301-es hit) (/majorstua/, /solli/, /tonsberg/,
/takeaway/, /<restaurant>/menu/), så ingen rangerte adresser går tapt ved lanseringen.
Hver side ligger som <mappe>/index.html; forsiden er index.html i roten."""
import datetime, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = 'https://kverneriet.no/'

# slug -> (fil, offentlig sti)
PAGES = {
    'index':      ('index.html',                '/'),
    'majorstua':  ('majorstua/index.html',      '/majorstua/'),
    'solli':      ('solli/index.html',          '/solli/'),
    'tonsberg':   ('tonsberg/index.html',       '/tonsberg/'),
    'meny':       ('meny/index.html',           '/meny/'),
    'majorstua-menu': ('majorstua/menu/index.html', '/majorstua/menu/'),
    'solli-menu':     ('solli/menu/index.html',     '/solli/menu/'),
    'tonsberg-menu':  ('tonsberg/menu/index.html',  '/tonsberg/menu/'),
    'takeaway':   ('takeaway/index.html',       '/takeaway/'),
    'om':         ('om/index.html',             '/om/'),
    'lunsj':      ('lunsj/index.html',          '/lunsj/'),
    'julebord':   ('julebord/index.html',       '/julebord/'),
    'selskap':    ('selskap/index.html',        '/selskap/'),
    'late-night': ('late-night/index.html',     '/late-night/'),
    'middag':     ('middag/index.html',         '/middag/'),
    'cocktails':  ('cocktails/index.html',      '/cocktails/'),
    'fries':      ('fries/index.html',          '/fries/'),
    'soft-serve': ('soft-serve/index.html',     '/soft-serve/'),
    'sporsmal':   ('sporsmal/index.html',       '/sporsmal/'),
    'kontakt':    ('kontakt/index.html',        '/kontakt/'),
    'maten':      ('maten/index.html',          '/maten/'),
    'personvern': ('personvern/index.html',     '/personvern/'),
}
VENUE_SLUGS = ['majorstua', 'solli', 'tonsberg']
LANDING_SLUGS = ['lunsj', 'middag', 'julebord', 'selskap', 'cocktails', 'late-night', 'fries', 'soft-serve']

def register(slug, file, url):
    PAGES[slug] = (file, url)

def path(slug): return PAGES[slug][0]
def url(slug): return PAGES[slug][1]
def abs_url(slug): return DOMAIN.rstrip('/') + url(slug)
def slug_of(file):
    for s, (f, _) in PAGES.items():
        if f == file: return s
    raise KeyError(file)
def all_files(): return [f for f, _ in PAGES.values()]

def read(slug): return open(os.path.join(ROOT, path(slug)), encoding='utf-8').read()
def write(slug, s):
    p = os.path.join(ROOT, path(slug)); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(s)

def venues():
    return json.load(open(os.path.join(ROOT, 'content/venues.json'), encoding='utf-8'))
def venue(slug):
    return next(v for v in venues()['venues'] if v['slug'] == slug)
def load_json(name, default=None):
    p = os.path.join(ROOT, 'content', name)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else default

def press(): return load_json('press.json', [])
def landing(): return load_json('landing.json', [])
def site_copy(): return load_json('site-copy.json', {})
def posts(): return load_json('blog.json', [])

def menus():
    src = open(os.path.join(ROOT, 'content/menus.js'), encoding='utf-8').read()
    return json.loads(src[src.index('{'): src.rindex('}') + 1])

DAYS_NO = {'Monday': 'mandag', 'Tuesday': 'tirsdag', 'Wednesday': 'onsdag', 'Thursday': 'torsdag',
           'Friday': 'fredag', 'Saturday': 'lørdag', 'Sunday': 'søndag'}
DAYS_EN = {'Monday': 'Monday', 'Tuesday': 'Tuesday', 'Wednesday': 'Wednesday', 'Thursday': 'Thursday',
           'Friday': 'Friday', 'Saturday': 'Saturday', 'Sunday': 'Sunday'}

WEEK = list(DAYS_EN)

def day_range(days, lang='no'):
    """['Tuesday','Wednesday','Thursday','Friday'] -> 'tirsdag–fredag'. Dager som ikke henger
    sammen, får «og» eller komma: ['Monday','Sunday'] -> 'mandag og søndag'."""
    names = DAYS_NO if lang == 'no' else DAYS_EN
    og = ' og ' if lang == 'no' else ' and '
    ds = sorted(days, key=WEEK.index)
    if len(ds) == 1: return names[ds[0]]
    idx = [WEEK.index(d) for d in ds]
    if idx == list(range(idx[0], idx[-1] + 1)): return f'{names[ds[0]]}–{names[ds[-1]]}'
    return ', '.join(names[d] for d in ds[:-1]) + og + names[ds[-1]]

def hours_rows(v):
    """Kjøkken og bar for samme dag på én rad. Dager som følger etter hverandre og har like tider,
    slås sammen: [(dager, åpner, kjøkkenet stenger, baren stenger), ...] i ukedagsrekkefølge."""
    k = {d: (h['opens'], h['closes']) for h in v['hours']['kitchen'] for d in h['days']}
    b = {d: h['closes'] for h in v['hours']['bar'] for d in h['days']}
    rows = []
    for d in WEEK:
        if d not in k: continue
        t = (k[d][0], k[d][1], b.get(d))
        if rows and rows[-1][1:] == t and WEEK.index(rows[-1][0][-1]) == WEEK.index(d) - 1:
            rows[-1][0].append(d)
        else:
            rows.append(([d], *t))
    return rows

def hhmm(t): return t.replace(':', '.')

# ---------------------------------------------------------------------------
# Endrede åpningstider (jul, påske, helligdager). Ligger i venues.json som hours.special,
# hentet fra feltet «Endrede åpningstider» på restauranten i Sanity:
#   {"from": "2026-12-27", "to": "2026-12-30", "opens": "14:00", "closes": "22:00"}
#   {"from": "2026-12-31", "to": "2026-12-31", "closed": true}
# opens/closes er kjøkkenet. barCloses er valgfri.
# ---------------------------------------------------------------------------
try:
    from zoneinfo import ZoneInfo
    _OSLO = ZoneInfo('Europe/Oslo')
except Exception:  # uten tidssonedata: bruk maskinens dato
    _OSLO = None

MONTHS_NO = ['januar', 'februar', 'mars', 'april', 'mai', 'juni', 'juli', 'august', 'september', 'oktober', 'november', 'desember']
MONTHS_EN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
SPECIAL_WINDOW_DAYS = 60   # vises på siden fra 60 dager før første dag


def today():
    """Dagens dato i Oslo. Bygget på GitHub kjører i UTC, og rett over midnatt er det fortsatt «i går» der."""
    return (datetime.datetime.now(_OSLO) if _OSLO else datetime.datetime.now()).date()


def special_hours(v, window=None):
    """De endrede åpningstidene som ikke er passert ennå, sortert etter dato. Med window
    tas bare de som begynner innen så mange dager med."""
    t = today()
    out = []
    for h in (v.get('hours') or {}).get('special') or []:
        try:
            a = datetime.date.fromisoformat(h['from'])
            b = datetime.date.fromisoformat(h.get('to') or h['from'])
        except (KeyError, ValueError):
            continue
        if b < a: a, b = b, a
        if b < t or (window is not None and (a - t).days > window):
            continue
        if not h.get('closed') and not (h.get('opens') and h.get('closes')):
            continue  # halvferdig rad i Sanity: hverken stengt eller tider
        out.append({**h, 'from': a.isoformat(), 'to': b.isoformat()})
    return sorted(out, key=lambda h: h['from'])


def date_range_text(a, b, lang='no'):
    """'2026-12-23', '2026-12-26' -> '23.–26. desember' / '23–26 December'.
    Over månedsskiftet: '30. desember–2. januar' / '30 December–2 January'."""
    a, b = datetime.date.fromisoformat(a), datetime.date.fromisoformat(b)
    m = MONTHS_NO if lang == 'no' else MONTHS_EN
    one = (lambda d: f'{d.day}. {m[d.month - 1]}') if lang == 'no' else (lambda d: f'{d.day} {m[d.month - 1]}')
    if a == b: return one(a)
    if (a.year, a.month) == (b.year, b.month):
        return f'{a.day}.–{one(b)}' if lang == 'no' else f'{a.day}–{one(b)}'
    return f'{one(a)}–{one(b)}'


def is_christmas(entries):
    """Alle radene ligger mellom 15. desember og 6. januar: da heter blokken «Jul og nyttår»."""
    def jul(s):
        d = datetime.date.fromisoformat(s)
        return (d.month == 12 and d.day >= 15) or (d.month == 1 and d.day <= 6)
    return bool(entries) and all(jul(h['from']) and jul(h['to']) for h in entries)

def esc(s): return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
