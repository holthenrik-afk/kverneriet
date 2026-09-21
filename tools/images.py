#!/usr/bin/env python3
"""Bildepipeline (LCP/CWV): lager responsive varianter av assets/img/*.jpg i assets/img/r/ som
<navn>-<bredde>.jpg og .webp (sips + cwebp), og imgopt() skriver <picture>/srcset/sizes/width/height inn i
HTML-en. Originalene røres ikke. Kjør: python3 tools/build.py (varianter lages bare når de mangler)."""
import os, re, subprocess, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv
os.chdir(kv.ROOT)

WIDTHS = [480, 800, 1200, 1600, 2000]
SRC = 'assets/img'; OUT = 'assets/img/r'
CACHE = os.path.join(OUT, 'index.json')

def dims(path):
    out = subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', path], capture_output=True, text=True).stdout
    return int(re.search(r'pixelWidth: (\d+)', out).group(1)), int(re.search(r'pixelHeight: (\d+)', out).group(1))

def build_variants():
    os.makedirs(OUT, exist_ok=True)
    index = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    if not (shutil.which('sips') and shutil.which('cwebp')):
        print('  images: sips/cwebp mangler (CI) – bruker variantene som ligger i assets/img/r'); return index
    for f in sorted(os.listdir(SRC)):
        if not f.lower().endswith('.jpg'): continue
        src = os.path.join(SRC, f); name = f[:-4]
        w, h = dims(src)
        entry = index.get(name)
        if entry and entry['w'] == w and entry['mtime'] == int(os.path.getmtime(src)) and all(os.path.exists(os.path.join(OUT, f'{name}-{x}.webp')) for x in entry['widths']):
            continue
        widths = [x for x in WIDTHS if x < w] + [w if w <= max(WIDTHS) else max(WIDTHS)]
        widths = sorted(set(widths))
        for x in widths:
            jpg = os.path.join(OUT, f'{name}-{x}.jpg'); webp = os.path.join(OUT, f'{name}-{x}.webp')
            if x == w: subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '82', src, '--out', jpg], capture_output=True)
            else: subprocess.run(['sips', '--resampleWidth', str(x), '-s', 'format', 'jpeg', '-s', 'formatOptions', '82', src, '--out', jpg], capture_output=True)
            subprocess.run(['cwebp', '-quiet', '-q', '80', jpg, '-o', webp], capture_output=True)
        index[name] = {'w': w, 'h': h, 'widths': widths, 'mtime': int(os.path.getmtime(src))}
        print(f'  {name}: {w}x{h} → {widths}')
    json.dump(index, open(CACHE, 'w'), indent=0)
    return index

# sizes etter kontekst (klasse på <img> eller nærmeste figure/section)
def sizes_for(tag, before):
    if 'hero-dark__img' in tag or 'fries-band' in before[-600:]: return '100vw'
    if 'wrap--wide' in before[-300:]: return '(max-width:1440px) calc(100vw - 48px), 1392px'
    if 'media-card' in before[-400:]: return '(max-width:760px) 88vw, 340px'
    if 'gallery-grid' in before[-1500:]: return '(max-width:760px) 50vw, 25vw'
    if 'grid-3' in before[-2500:] or 'venue-card' in before[-600:]: return '(max-width:760px) 100vw, 33vw'
    if 'menu-aside' in before[-800:]: return '(max-width:1024px) 100vw, 30vw'
    return '(max-width:760px) 100vw, 50vw'

IMG_RE = re.compile(r'<img ([^>]*?)src="/assets/img/([a-z0-9-]+)\.jpg"([^>]*)>')
CDN_RE = re.compile(r'<img ([^>]*?)src="(https://cdn\.sanity\.io/images/[^"?]+-(\d+)x(\d+)\.[a-z]+)(?:\?[^"]*)?"([^>]*)>')

def cdnopt(html):
    """Bilder fra Sanity: samme srcset/sizes/width/height som lokale, men via CDN-parametre."""
    def one(m):
        attrs = (m.group(1) + m.group(5)).strip(); url, w, h = m.group(2), int(m.group(3)), int(m.group(4))
        if 'srcset=' in attrs: return m.group(0)
        before = html[max(0, m.start() - 2500):m.start()]
        sizes = sizes_for(attrs, before)
        widths = [x for x in WIDTHS if x < w] + [min(w, max(WIDTHS))]
        attrs = re.sub(r'\s*(width|height)="\d+"', '', attrs)
        srcset = ', '.join(f'{url}?w={x}&auto=format&q=80 {x}w' for x in sorted(set(widths)))
        fallback = max([x for x in widths if x <= 1200] or widths)
        return f'<img {attrs} src="{url}?w={fallback}&auto=format&q=80" srcset="{srcset}" sizes="{sizes}" width="{w}" height="{h}">'
    return CDN_RE.sub(one, html)
PIC_RE = re.compile(r'<picture><source type="image/webp"[^>]*><img ([^>]*?)src="/assets/img/r/([a-z0-9-]+)-\d+\.jpg"([^>]*)></picture>')

def unwrap(html):
    """Tilbake til ren <img src="/assets/img/<navn>.jpg"> så nye varianter/bilder alltid tas med."""
    def one(m):
        attrs = (m.group(1) + m.group(3)).strip()
        attrs = re.sub(r'\s*(srcset|sizes|width|height)="[^"]*"', '', attrs)
        return f'<img {attrs} src="/assets/img/{m.group(2)}.jpg">'
    return PIC_RE.sub(one, html)

def imgopt(html, index):
    html = cdnopt(unwrap(html))
    out = []; pos = 0
    for m in IMG_RE.finditer(html):
        name = m.group(2); entry = index.get(name)
        if not entry: continue
        attrs = (m.group(1) + m.group(3)).strip()
        if 'srcset=' in attrs: continue
        before = html[max(0, m.start() - 2500):m.start()]
        sizes = sizes_for(attrs, before)
        w, h = entry['w'], entry['h']
        # width/height for CLS – bevar bildets format; CSS setter visningsstørrelsen
        attrs = re.sub(r'\s*(width|height)="\d+"', '', attrs)
        srcset_jpg = ', '.join(f'/assets/img/r/{name}-{x}.jpg {x}w' for x in entry['widths'])
        srcset_webp = ', '.join(f'/assets/img/r/{name}-{x}.webp {x}w' for x in entry['widths'])
        fallback = max(x for x in entry['widths'] if x <= 1200) if any(x <= 1200 for x in entry['widths']) else entry['widths'][0]
        img = f'<img {attrs} src="/assets/img/r/{name}-{fallback}.jpg" srcset="{srcset_jpg}" sizes="{sizes}" width="{w}" height="{h}">'
        pic = f'<picture><source type="image/webp" srcset="{srcset_webp}" sizes="{sizes}">{img}</picture>'
        out.append(html[pos:m.start()]); out.append(pic); pos = m.end()
    out.append(html[pos:])
    return ''.join(out)

def apply_all(index=None):
    index = index or json.load(open(CACHE))
    for f in kv.all_files():
        if not os.path.exists(f): continue
        s = open(f, encoding='utf-8').read(); s2 = imgopt(s, index)
        if s2 != s: open(f, 'w', encoding='utf-8').write(s2)
    print('imgopt ok')

if __name__ == '__main__':
    idx = build_variants(); apply_all(idx)
