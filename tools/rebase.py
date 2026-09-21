#!/usr/bin/env python3
"""Flytter nettstedet til en undermappe (f.eks. /kverneriet på <bruker>.github.io/kverneriet/) ved å skrive om
alle rot-relative lenker («/assets/…», «/majorstua/») til «<base>/assets/…». Brukes av GitHub Actions-workflowen
med base_path fra actions/configure-pages; med eget domene er basen tom og ingenting endres.
Absolutte adresser (canonical, og:url, sitemap, JSON-LD) røres ikke – de skal peke på kverneriet.com.

Bruk: python3 tools/rebase.py <base> <mappe>     f.eks. python3 tools/rebase.py /kverneriet /tmp/site"""
import os, re, sys

base = (sys.argv[1] if len(sys.argv) > 1 else '').rstrip('/')
root = sys.argv[2] if len(sys.argv) > 2 else '.'
EXT = ('.html', '.css', '.js', '.webmanifest', '.json')
TOP = r'(?:assets|majorstua|solli|tonsberg|meny|takeaway|lunsj|julebord|selskap|late-night|packages|giftcard|gc|static-pdf|content|kverneriet\.css|site\.js|meny\.js|styles\.css|site\.css|favicon\.ico|site\.webmanifest|sitemap\.xml|robots\.txt|llms\.txt|404\.html)'
# Rot-relativ sti rett etter et anførselstegn, «(», «=», komma eller mellomrom (srcset), og ikke «//»
PATH_RE = re.compile(r'(?<=["\'(=,\s\\])/(?=' + TOP + r'(?:[/"\'?#\s,)]|$))')
HOME_RE = re.compile(r'(href|start_url)(=|":\s*)(["\'])/(["\'])')

def rebase(text):
    text = PATH_RE.sub(base + '/', text)
    text = HOME_RE.sub(lambda m: f'{m.group(1)}{m.group(2)}{m.group(3)}{base}/{m.group(4)}', text)
    return text

if not base:
    print('rebase: tom base, ingenting å gjøre'); sys.exit(0)
n = 0
for d, _, files in os.walk(root):
    if '/.git' in d or '/tools' in d: continue
    for f in files:
        if not f.endswith(EXT): continue
        p = os.path.join(d, f); s = open(p, encoding='utf-8').read(); s2 = rebase(s)
        if s2 != s: open(p, 'w', encoding='utf-8').write(s2); n += 1
print(f'rebase: {n} filer skrevet om til {base}/')
