#!/usr/bin/env python3
"""Pakker en side til én selvstendig HTML-fil (CSS, Bourton, bilder og logoer inlinet) for
import til Figma via html.to.design. Bruk: python3 tools/bundle.py index.html > /tmp/index.bundle.html"""
import re, os, sys, base64, subprocess, tempfile
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
page = sys.argv[1]
MAXW = int(sys.argv[2]) if len(sys.argv) > 2 else 900

def data_uri(path, mime): return f'data:{mime};base64,' + base64.b64encode(open(path, 'rb').read()).decode()
def jpg_uri(path):
    tmp = tempfile.mktemp(suffix='.jpg')
    subprocess.run(['sips', '--resampleWidth', str(MAXW), '-s', 'format', 'jpeg', '-s', 'formatOptions', '58', path, '--out', tmp], capture_output=True)
    return data_uri(tmp, 'image/jpeg')
def svg_uri(path): return 'data:image/svg+xml;base64,' + base64.b64encode(open(path, 'rb').read()).decode()

# CSS: styles.css → tokens (med @import), + site.css
def read_css(p): return open(p, encoding='utf-8').read()
css = ''
for m in re.findall(r'@import url\("([^"?]+)', read_css('styles.css')):
    c = read_css(m)
    if m.endswith('fonts.css'):
        c = re.sub(r'src:url\("\.\./assets/fonts/BourtonBase\.ttf"\)', 'src:url("' + data_uri('assets/fonts/BourtonBase.ttf', 'font/ttf') + '")', c)
    css += c + '\n'
site = read_css('site.css')
site = re.sub(r'url\("(assets/press/[^"]+\.svg)"\)', lambda m: 'url("' + svg_uri(m.group(1)) + '")', site)
css += site

html = open(page, encoding='utf-8').read()
html = re.sub(r'<link rel="stylesheet" href="styles\.css[^"]*">\n<link rel="stylesheet" href="site\.css[^"]*">', '<style>' + css + '</style>', html, count=1)
html = re.sub(r'<script src="[^"]+" defer></script>\n?', '', html)
html = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', html, flags=re.S)
html = re.sub(r'<link rel="icon"[^>]*>\n?', '', html)
html = html.replace(' loading="lazy"', '').replace(' loading="eager"', '')
cache = {}
def img(m):
    src = m.group(1)
    if src not in cache:
        cache[src] = svg_uri(src) if src.endswith('.svg') else jpg_uri(src)
    return 'src="' + cache[src] + '"'
html = re.sub(r'src="(assets/(?:img|press)/[^"]+|assets/logo[^"]*\.svg)"', img, html)
html = re.sub(r'<!--.*?-->\n?', '', html, flags=re.S)
sys.stdout.write(html)
sys.stderr.write(f'{page}: {len(html)/1e6:.1f} MB, {len(cache)} images inlined\n')
