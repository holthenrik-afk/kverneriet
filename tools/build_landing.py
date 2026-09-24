#!/usr/bin/env python3
"""Landingssidene (/lunsj/, /julebord/, /selskap/, /late-night/) fra én mal. Header/footer fra chrome.py,
modal fra modal.py, mediekort fra media.py, FAQ fra faq.py, titler fra pages.py. Fakta (åpningstider,
pakker, priser) hentes fra content/venues.json så sidene aldri lover noe restaurantene ikke har.
Kjør: python3 tools/build.py"""
import os, sys, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv, chrome, modal, media as MD, faq, pages, i18n_gen as G
os.chdir(kv.ROOT)

V = kv.venues(); ORG = V['org']; PK = ORG['packages']
e = kv.esc
def vv(slug): return kv.venue(slug)

def page(p):
    slug = p['slug']; meta = pages.PAGES[slug]
    gallery = ''
    if p.get('gallery'):
        cells = ''.join(f'<figure class="photo" style="aspect-ratio:{g[2] if len(g) > 2 else "1/1"}"><img src="{g[0]}" alt="{e(g[1])}" loading="lazy"></figure>' for g in p['gallery'])
        gallery = f'''
  <section class="section section--flush-top">
    <div class="wrap"><div class="gallery-grid" style="grid-template-columns:repeat({len(p['gallery'])},1fr)">{cells}</div></div>
  </section>'''
    press = ('\n' + MD.section(MD.by_key(*p['media']))) if p.get('media') else ''
    facts = ''.join(
        f'<div class="upgrade-row"><span class="upgrade-row__glyph" aria-hidden="true">➼</span><span class="upgrade-row__body">'
        f'<span class="upgrade-row__name">{("<a href=\"" + f[2] + "\">" + e(f[0]) + "</a>") if len(f) > 2 and f[2] else e(f[0])}</span><span class="upgrade-row__note">{e(f[1])}</span></span></div>'
        for f in p['facts'])
    others = ''.join(f'<a class="btn btn--outline btn--sm" href="{kv.url(o)}" data-i18n="lp.{k}">{t}</a>' for o, k, t in p['others'])
    venues = ''.join(f'<a class="btn btn--ghost btn--sm" href="{kv.url(v["slug"])}">{e(v["fullName"])}</a>' for v in V['venues'])
    if p['cta'] == 'book':
        cta_primary = f'<a class="btn btn--primary btn--lg" href="/majorstua/#booking" data-book-open data-track="lp:{slug}:book" data-i18n="lp.bookNow">Book bord nå</a>'
    else:
        cta_primary = f'<a class="btn btn--primary btn--lg" href="/majorstua/#booking" data-book-open data-book-mode="large" data-track="lp:{slug}:group" data-i18n="lp.groupCta">Send gruppeforespørsel</a>'
    cta_secondary = (f'<a class="btn btn--ghost btn--md" href="/meny/" data-i18n="act.seeMenu">Se menyen</a>' if p.get('cta2') == 'menu'
                     else f'<a class="btn btn--ghost btn--md" href="/takeaway/" data-order-open data-track="lp:{slug}:takeaway" data-i18n="act.order">Bestill take-away</a>')
    crumbs = f'<nav class="crumbs" aria-label="Brødsmuler"><ol><li><a href="/">Kverneriet</a></li><li><span aria-current="page">{e(p["crumb"])}</span></li></ol></nav>'
    G.add('lp.venues', 'Restaurantene', 'The restaurants')
    return f'''<!DOCTYPE html>
<html lang="nb">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(meta['title'])}</title>
<meta name="description" content="{e(meta['desc'])}">
<!-- seo:start -->
<!-- seo:end -->
<link rel="stylesheet" href="/styles.css">
<link rel="stylesheet" href="/site.css">
<script src="/content/i18n.js" defer></script>
<script src="/content/i18n-gen.js" defer></script>
<script src="/site.js" defer></script>
</head>
<body>

{chrome.header()}
<main id="main">

  <section class="hero-dark hero-dark--short">
    <img class="hero-dark__img" src="{meta['img']}" alt="{e(p['imgAlt'])}" fetchpriority="high" decoding="async"{(' style="object-position:' + p['pos'] + '"') if p.get('pos') else ''}><div class="hero-dark__scrim" aria-hidden="true"></div>
    <div class="hero-dark__content">
      <span class="kv-eyebrow">{e(p['eyebrow'])}</span>
      <h1 class="hero-title" style="margin-top:var(--space-3);max-width:16ch">{e(p['h1'])}</h1>
      <p class="hero-sub">{e(p['sub'])}</p>
      <div style="display:flex;gap:12px;margin-top:var(--space-6);flex-wrap:wrap">
        {cta_primary}
        <a class="btn btn--paper btn--lg" href="/meny/" data-i18n="act.seeMenu">Se menyen</a>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      {crumbs}
      <div class="grid-2 grid-2--start">
      <div>
        <header class="sec-head">
          <div class="sec-head__rule"></div>
          <span class="kv-eyebrow">{e(p['sec_eyebrow'])}</span>
          <h2 class="display-2">{e(p['h2'])}</h2>
        </header>
        {''.join(f'<p class="lede" style="margin-top:var(--space-5)">{t}</p>' for t in p['body'])}
        <div style="margin-top:var(--space-6);display:flex;gap:12px;flex-wrap:wrap">
          {cta_primary.replace('btn--lg', 'btn--md')}
          {cta_secondary}
        </div>
      </div>
      <div>
        <div class="card">
          <div class="kv-eyebrow" style="margin-bottom:var(--space-3)">{e(p['facts_title'])}</div>
          {facts}
          <p class="caption" style="margin-top:var(--space-4)">{e(p['facts_note'])}</p>
        </div>
      </div>
      </div>
    </div>
  </section>
{gallery}{press}
{faq.section(faq.landing_faq(slug))}
  <section class="section section--flush-top">
    <div class="wrap">
      <div class="divider"><span data-i18n="lp.venues">Restaurantene</span></div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:var(--space-5)">{venues}</div>
      <div class="divider" style="margin-top:var(--space-7)"><span data-i18n="lp.moreEyebrow">Se også</span></div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:var(--space-5)">{others}</div>
    </div>
  </section>

</main>

{chrome.footer()}
{modal.MODAL}
</body>
</html>
'''

def lunch_sub():
    return ', '.join(f'{vv(s)["lunch"]} på {vv(s)["name"]}' for s in ('majorstua', 'solli')) + f' og {vv("tonsberg")["lunch"]} i Tønsberg'

def tonsberg_unique():
    """Retter som bare finnes på Tønsberg-menyen (fra content/menus.js)."""
    m = kv.menus(); names = {}
    for v in m['venues']: names[v['slug']] = {it['name'] for s in v['menu']['sections'] for it in s['items']}
    uniq = sorted(names['tonsberg'] - names['majorstua'] - names['solli'])
    return ' og '.join([', '.join(uniq[:-1]), uniq[-1]]) if len(uniq) > 1 else (uniq[0] if uniq else 'flere retter')

def hours_line(slug):
    v = vv(slug)
    return ', '.join(f'{kv.day_range(h["days"])} {kv.hhmm(h["opens"])}–{kv.hhmm(h["closes"])}' for h in v['hours']['kitchen'])

# Tekstene ligger i content/landing.json (redigeres i Sanity → tools/fetch_sanity.py). Faktakortene med åpningstider
# regnes fortsatt ut fra venues.json når teksten er tom, så tidene aldri spriker.
def _pages():
    out = []
    for p in kv.landing():
        d = dict(p)
        d['facts'] = [tuple(f) for f in d.get('facts', [])]
        d['others'] = [tuple(o) for o in d.get('others', [])]
        if d.get('gallery'): d['gallery'] = [tuple(g) for g in d['gallery']]
        if isinstance(d.get('body'), list) and d['body'] and isinstance(d['body'][0], dict):
            import portable as PT
            d['body'] = PT.paragraphs(d['body'])
        out.append(d)
    return out
PAGES = _pages()

def build():
    for p in PAGES:
        kv.write(p['slug'], page(p)); print(kv.path(p['slug']), 'ok')

if __name__ == '__main__':
    build(); G.write()
