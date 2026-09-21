#!/usr/bin/env python3
"""Pakker en side som selvstendig HTML der bilder, logoer og Bourton peker på offentlige CDN-adresser
(wf-urls.json fra Webflow-opplastingen). Til html.to.design-import. Bruk: bundle-cdn.py <page> <urls.json>"""
import re, os, sys, json
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
page, urls = sys.argv[1], json.load(open(sys.argv[2]))
def cdn(local):
    name = 'kv-' + os.path.basename(local).replace('BourtonBase', 'bourton')
    return urls[name]
css = ''
for m in re.findall(r'@import url\("([^"?]+)', open('styles.css').read()):
    c = open(m, encoding='utf-8').read()
    if m.endswith('fonts.css'): c = c.replace('url("../assets/fonts/BourtonBase.ttf")', 'url("' + cdn('assets/fonts/BourtonBase.ttf') + '")')
    css += c + '\n'
site = open('site.css', encoding='utf-8').read()
site = re.sub(r'url\("(assets/press/[^"]+\.(?:svg|png))"\)', lambda m: 'url("' + cdn(m.group(1)) + '")', site)
css += site
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S); css = re.sub(r'\n\s*\n', '\n', css)
html = open(page, encoding='utf-8').read()
html = re.sub(r'<link rel="stylesheet" href="styles\.css[^"]*">\n<link rel="stylesheet" href="site\.css[^"]*">', '<style>' + css + '</style>', html, count=1)
html = re.sub(r'<script src="[^"]+" defer></script>\n?', '', html)
html = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', html, flags=re.S)
html = re.sub(r'<link rel="icon"[^>]*>\n?', '', html)
html = re.sub(r'<meta (?:name="description"|property="og:[^"]+"|name="twitter:card")[^>]*>\n?', '', html)
html = re.sub(r'<link rel="canonical"[^>]*>\n?', '', html)
html = html.replace(' loading="lazy"', '').replace(' loading="eager"', '')
html = re.sub(r'src="(assets/(?:img|press)/[^"]+|assets/logo[^"]*\.svg)"', lambda m: 'src="' + cdn(m.group(1)) + '"', html)
html = re.sub(r'<!--.*?-->\n?', '', html, flags=re.S)
# Modalen og mobilpanelet er skjult i nettleseren; ta dem ut så de ikke blir tomme lag i Figma
html = re.sub(r'<div class="modal-root" id="order-modal".*?\n</div>\n', '', html, flags=re.S)
html = re.sub(r'<div class="mobile-panel" id="mobile-panel">.*?</div>\n', '', html, flags=re.S)
html = re.sub(r'\n\s*\n', '\n', html)

# --- Beskjær CSS til det siden faktisk bruker (html.to.design har en grense for HTML-størrelse) ---
DROP = ['.menu-', '.kv-tag', '.upgrade-row', '.allergen-row', '.hours', '.field', '.select-wrap', '.check', '.form-grid', '.seg', '.modal',
        '.order-group', '.bk', '.notice', '.badge', '.pullquote', '.press-card', '.press-grid', '.press-head', '.press-row', '.gallery-grid',
        '.booking-grid', '.practical-grid', '.hero-dark', '.mobile-panel', '.nav-burger', '.icon-btn', '.lang-switch', '.venue-card', '.sr-only',
        '.site-nav', '.section-nav', '.terning--generic', '[id]', 'html{scroll', '@keyframes', '.divider', '.sec-head--center', '.display-1',
        '.hero-title', '.body-strong', '.stack-', '.center', '.measure', '.caption', '.lede', '.grid-2', '.btn--paper', '.btn--ghost', '.btn--sm',
        '.btn--md', '.btn--block', '.btn__glyph', '.card--raised', '.card--pad-lg', '.trust__sep', '.kv-photo']
m = re.search(r'<style>(.*?)</style>', html, re.S); body_html = html[m.end():]
def used(sel):
    sel = sel.strip()
    for pre in DROP:
        if sel.startswith(pre):
            cls = re.match(r'\.([a-zA-Z0-9_-]+)', sel)
            return bool(cls and re.search(r'class="[^"]*\b' + re.escape(cls.group(1)) + r'\b', body_html))
    return True
def split_rules(block):
    rules, depth, start = [], 0, 0
    for k, ch in enumerate(block):
        if ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0: rules.append(block[start:k+1]); start = k+1
    return rules
def filter_block(block):
    res = []
    for r in split_rules(block):
        if r.lstrip().startswith('@media'):
            head, body = r.split('{', 1); inner = filter_block(body.rsplit('}', 1)[0])
            if inner.strip(): res.append(head + '{' + inner + '}')
        elif r.lstrip().startswith(('@font-face', '@import', ':root', 'html', 'body', '*', 'h1', 'p{', 'a{', 'a:', ':focus', 'img', '::selection')):
            res.append(r)
        elif any(used(x) for x in r.split('{', 1)[0].split(',')): res.append(r)
    return ''.join(res)
css2 = filter_block(m.group(1))
css2 = re.sub(r'\s*\n\s*', '', css2); css2 = re.sub(r'\s*([{}:;,>])\s*', r'\1', css2).replace(';}', '}')
# Figma-eksport: vis alle mediekort i rutenett i stedet for horisontal scroll
css2 += '.media-scroller{grid-auto-flow:row;grid-template-columns:repeat(4,1fr);overflow:visible;margin-inline:0;padding-inline:0}'
html = html[:m.start()] + '<style>' + css2 + '</style>' + html[m.end():]
html = re.sub(r'\n\s+', ' \n', html)
sys.stdout.write(html); sys.stderr.write(f'{page}: {len(html)/1e3:.0f} KB (css {len(m.group(1))//1000}→{len(css2)//1000} KB)\n')
