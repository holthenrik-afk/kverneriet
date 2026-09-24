"""Felles for generatorene: sideregister, URL-er og innholdslaget.

URL-strukturen følger kverneriet.com slik den er indeksert i dag (/majorstua/, /solli/, /tonsberg/,
/takeaway/, /<restaurant>/menu/), så ingen rangerte adresser går tapt ved lanseringen.
Hver side ligger som <mappe>/index.html; forsiden er index.html i roten."""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = 'https://kverneriet.com/'

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
    'lunsj':      ('lunsj/index.html',          '/lunsj/'),
    'julebord':   ('julebord/index.html',       '/julebord/'),
    'selskap':    ('selskap/index.html',        '/selskap/'),
    'late-night': ('late-night/index.html',     '/late-night/'),
    'middag':     ('middag/index.html',         '/middag/'),
    'cocktails':  ('cocktails/index.html',      '/cocktails/'),
}
VENUE_SLUGS = ['majorstua', 'solli', 'tonsberg']
LANDING_SLUGS = ['lunsj', 'middag', 'julebord', 'selskap', 'cocktails', 'late-night']

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

def day_range(days, lang='no'):
    """['Tuesday','Wednesday','Thursday','Friday'] -> 'tirsdag–fredag'"""
    names = DAYS_NO if lang == 'no' else DAYS_EN
    if len(days) == 1: return names[days[0]]
    return f'{names[days[0]]}–{names[days[-1]]}'

def hhmm(t): return t.replace(':', '.')

def esc(s): return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
