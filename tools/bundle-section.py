#!/usr/bin/env python3
"""Pakker én seksjon (CSS-selektor-ish: mellom to markører i index.html) som selvstendig HTML for html.to.design.
Bruk: python3 tools/bundle-section.py <page> <start-marker> <end-marker> [maxw] [--no-font]"""
import re, os, sys, base64, subprocess, tempfile
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
page, start, end = sys.argv[1], sys.argv[2], sys.argv[3]
MAXW = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else 640
NOFONT = '--no-font' in sys.argv
def data_uri(p, mime): return f'data:{mime};base64,' + base64.b64encode(open(p, 'rb').read()).decode()
def jpg_uri(p):
    tmp = tempfile.mktemp(suffix='.jpg'); subprocess.run(['sips', '--resampleWidth', str(MAXW), '-s', 'format', 'jpeg', '-s', 'formatOptions', '55', p, '--out', tmp], capture_output=True); return data_uri(tmp, 'image/jpeg')
def svg_uri(p): return 'data:image/svg+xml;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
css = ''
for m in re.findall(r'@import url\("([^"?]+)', open('styles.css').read()):
    c = open(m, encoding='utf-8').read()
    if m.endswith('fonts.css'):
        c = re.sub(r'@font-face\{[^}]*Bourton[^}]*\}', '' if NOFONT else lambda mm: mm.group(0).replace('url("../assets/fonts/BourtonBase.ttf")', 'url("' + data_uri('assets/fonts/BourtonBase.ttf', 'font/ttf') + '")'), c)
    css += c + '\n'
html0 = open(page, encoding='utf-8').read()
i0 = html0.index(start); j0 = html0.index(end, i0); frag0 = html0[i0:j0]
used = set(re.findall(r'press-logo--([a-z]+)', frag0))
site = open('site.css', encoding='utf-8').read()
site = re.sub(r'url\("(assets/press/([a-z]+)\.svg)"\)', lambda m: ('url("' + svg_uri(m.group(1)) + '")') if m.group(2) in used else 'none', site)
css += site
# Minimer CSS litt
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S); css = re.sub(r'\n\s*\n', '\n', css)
html = open(page, encoding='utf-8').read()
i = html.index(start); j = html.index(end, i)
frag = html[i:j]
frag = frag.replace(' loading="lazy"', '').replace(' loading="eager"', '')
cache = {}
def img(m):
    src = m.group(1)
    if src not in cache: cache[src] = svg_uri(src) if src.endswith('.svg') else jpg_uri(src)
    return 'src="' + cache[src] + '"'
frag = re.sub(r'src="(assets/(?:img|press)/[^"]+|assets/logo[^"]*\.svg)"', img, frag)
frag = re.sub(r'<!--.*?-->\n?', '', frag, flags=re.S)
out = f'<style>{css}</style>\n<div style="width:1440px;background:#FAF8F5">{frag}</div>'
sys.stdout.write(out)
sys.stderr.write(f'{len(out)/1e3:.0f} KB, {len(cache)} images, font={"no" if NOFONT else "yes"}\n')
