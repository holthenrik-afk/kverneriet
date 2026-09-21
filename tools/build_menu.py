#!/usr/bin/env python3
"""Menysidene: /majorstua/menu/, /solli/menu/, /tonsberg/menu/ (samme adresser som kverneriet.com i dag) og
/meny/ (velg restaurant). Menyen forhåndsrendres fra content/menus.js i nøyaktig samme markup som meny.js
lager, så retter, priser og allergener ligger i HTML-en for søkemotorer og svarmotorer; meny.js oppdaterer
bare de oversettbare etikettene ved språkbytte. Kjør: python3 tools/build.py"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv, chrome, modal, i18n_gen as G, pages
os.chdir(kv.ROOT)

C = kv.menus(); V = kv.venues()
e = kv.esc

def tag(code, maybe=False, parens=False):
    label = C['allergenKey'].get(code, code)
    return f'<span class="kv-tag{" kv-tag--maybe" if maybe else ""}" title="{e(label)}">{"(" + e(code) + ")" if parens else e(code)}</span>'

def item_html(it):
    h = f'<article class="menu-item"><div class="menu-item__row"><h3>{e(it["name"])}</h3><span class="menu-item__price">{e(it["price"])}</span></div>'
    if it.get('description'): h += f'<p class="menu-item__desc">{e(it["description"])}{(" <strong>" + e(it["emphasis"]) + "</strong>") if it.get("emphasis") else ""}</p>'
    elif it.get('emphasis'): h += f'<p class="menu-item__desc"><strong>{e(it["emphasis"])}</strong></p>'
    if it.get('quote'): h += f'<p class="menu-item__quote">{e(it["quote"])}</p>'
    tags = [tag(a) for a in it.get('allergens', [])] + [tag(a, True, True) for a in it.get('maybeAllergens', [])]
    if tags: h += f'<div class="menu-item__tags">{"".join(tags)}</div>'
    return h + '</article>'

def upgrade_html(u):
    delta = u.get('delta', '')
    h = f'<div class="upgrade-row"><span class="upgrade-row__glyph" aria-hidden="true">➼</span><span class="upgrade-row__body"><span class="upgrade-row__name">{e(u["name"])}</span>'
    if u.get('note'): h += f'<span class="upgrade-row__note">{e(u["note"])}</span>'
    h += '</span>'
    tags = [tag(a, True) for a in u.get('allergens', [])]
    if tags: h += f'<span class="upgrade-row__tags">{"".join(tags)}</span>'
    if delta: h += f'<span class="upgrade-row__delta{" upgrade-row__delta--free" if delta == "free" else ""}">{e(delta)}</span>'
    return h + '</div>'

def section_html(s, kids_pdf):
    h = f'<section class="menu-sec" id="{e(s["id"])}"><header class="sec-head"><div class="sec-head__rule"></div><h2 class="display-2">{e(s["title"])}</h2>'
    if s.get('intro'): h += f'<p class="sec-head__intro">{e(s["intro"])}</p>'
    h += f'</header><div style="margin-top:var(--space-5)">{"".join(item_html(i) for i in s["items"])}</div>'
    if s.get('upgrades'): h += f'<div style="margin-top:var(--space-7)"><div class="divider"><span>{e(s["upgradesTitle"])}</span></div><div style="margin-top:var(--space-3)">{"".join(upgrade_html(u) for u in s["upgrades"])}</div></div>'
    if s.get('dips'): h += f'<div style="margin-top:var(--space-7)"><div class="divider"><span>{e(s["dipsTitle"])}</span></div><div style="margin-top:var(--space-3)">{"".join(upgrade_html(u) for u in s["dips"])}</div></div>'
    if s['id'] == 'kids' and kids_pdf:
        h += f'<p style="margin-top:var(--space-6);color:var(--text-muted);font-size:var(--type-body-sm)"><a href="{kids_pdf}" target="_blank" rel="noopener" data-i18n="menu.kidsPdf">Barnemenyen finnes også som utskriftsvennlig PDF.</a></p>'
    return h + '</section>'

def allergen_key():
    return ''.join(f'<div class="allergen-row"><span class="kv-tag" title="{e(n)}">{e(k)}</span><span class="caption">{e(n)}</span></div>' for k, n in C['allergenKey'].items())

def switcher(active):
    return ''.join(f'<a href="{kv.url(v["slug"] + "-menu")}"{" class=\"is-on\" aria-current=\"page\"" if v["slug"] == active else ""}>{e(v["name"])}</a>' for v in C['venues'])

def head(slug, p):
    return f'''<!DOCTYPE html>
<html lang="nb">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(p['title'])}</title>
<meta name="description" content="{e(p['desc'])}">
<!-- seo:start -->
<!-- seo:end -->
<link rel="stylesheet" href="/styles.css">
<link rel="stylesheet" href="/site.css">
<script src="/content/i18n.js" defer></script>
<script src="/content/i18n-gen.js" defer></script>
<script src="/content/menus.js" defer></script>
<script src="/site.js" defer></script>
<script src="/meny.js" defer></script>
</head>
'''

def venue_menu_page(v):
    slug = v['slug']; vv = kv.venue(slug); p = pages.PAGES[slug + '-menu']; m = v['menu']
    G.add('menu.eyebrow', 'Én meny per restaurant', 'One menu per restaurant')
    G.add(f'menu.h1.{slug}', f'Menyen – Kverneriet {v["name"]}', f'The menu – Kverneriet {v["name"]}')
    G.add(f'menu.intro.{slug}', f'Hele menyen på Kverneriet {v["name"]} med priser i kroner og allergener per rett. Burgerne har 150 g patty av kjøtt vi kverner selv og serveres medium pluss; friesene er trippelkokte og naturlig glutenfrie. Rettene står på engelsk, som på menyen i restauranten.',
          f'The full menu at Kverneriet {v["name"]} with prices in NOK and allergens per dish. Burgers come with a 150 g patty of beef we grind ourselves, cooked medium plus; the fries are triple-cooked and naturally gluten-free.')
    G.add('menu.drinksPdf', 'Drikkemeny (PDF)', 'Drinks menu (PDF)'); G.add('menu.back', 'Tilbake til', 'Back to')
    nav = ''.join(f'<li><a href="#{e(s["id"])}">{e(s["label"])}</a></li>' for s in m['sections'])
    content = ''.join(section_html(s, m.get('kidsPdf')) for s in m['sections'])
    crumbs = f'<nav class="crumbs" aria-label="Brødsmuler"><ol><li><a href="/">Kverneriet</a></li><li><a href="{kv.url(slug)}">{e(v["name"])}</a></li><li><span aria-current="page" data-i18n="act.menu">Meny</span></li></ol></nav>'
    return head(slug, p) + f'''<body data-venue="{slug}" data-menu-venue="{slug}">

{chrome.header(active=slug, menu_href=kv.url(slug + '-menu'))}
<nav class="section-nav" aria-label="Menyseksjoner" data-scrollspy id="menu-section-nav">
  <ul id="menu-sections-list">{nav}</ul>
</nav>

<main id="main">
  <div class="wrap" style="padding-top:var(--space-7);padding-bottom:var(--section-y)">
    {crumbs}
    <header class="sec-head">
      <div class="sec-head__rule"></div>
      <span class="kv-eyebrow" data-i18n="menu.eyebrow">Én meny per restaurant</span>
      <h1 class="hero-title" style="font-size:var(--type-display-1)" data-i18n="menu.h1.{slug}">Menyen – Kverneriet {e(v['name'])}</h1>
      <p class="sec-head__intro" data-i18n="menu.intro.{slug}">{e(G._D['no'][f'menu.intro.{slug}'])}</p>
      <nav class="seg" id="venue-switch" aria-label="Velg restaurant" style="margin-top:var(--space-5)">{switcher(slug)}</nav>
    </header>

    <div class="menu-layout">
      <div id="menu-content" lang="en">{content}</div>

      <aside class="menu-aside">
        <figure class="photo" style="aspect-ratio:4/5" id="menu-photo"><img src="{m['photo']}" alt="{e(m['photoLabel'])}"></figure>
        <div class="card" id="allergen-card">
          <div class="kv-eyebrow" data-i18n="menu.allergen">Allergen-nøkkel</div>
          <div class="stack-2" style="margin-top:var(--space-4);gap:6px" id="allergen-key">{allergen_key()}</div>
          <p class="caption" style="margin-top:var(--space-4)" data-i18n="menu.allergenNote">Koder i parentes betyr at retten kan inneholde spor.</p>
        </div>
        <a class="btn btn--primary btn--md btn--block" href="{kv.url(slug)}#booking" data-book-open data-book-venue="{slug}" data-track="cta:book:{slug}" data-i18n="act.book">Book bord</a>
        <button class="btn btn--outline btn--md btn--block" type="button" data-order-open data-track="cta:takeaway:{slug}" data-i18n="act.order">Bestill take-away</button>
        <a class="btn btn--ghost btn--sm btn--block" href="{m['drinksPdf']}" target="_blank" rel="noopener" data-i18n="menu.drinksPdf">Drikkemeny (PDF)</a>
        <a class="btn btn--ghost btn--sm btn--block" id="back-to-venue" href="{kv.url(slug)}"><span class="btn__glyph" aria-hidden="true">«</span> <span data-i18n="menu.back">Tilbake til</span> {e(v['name'])}</a>
      </aside>
    </div>

  </div>
</main>

{chrome.footer(menu_href=kv.url(slug + '-menu'))}
{modal.MODAL}
</body>
</html>
'''

def hub_page():
    p = pages.PAGES['meny']
    G.add('menu.hub.h1', 'Menyene våre', 'Our menus')
    G.add('menu.hub.intro', 'Hver restaurant har sin egen meny, men grunnlaget er det samme: burgere med 150 g patty av kjøtt vi kverner selv, ferske brød, trippelkokte fries som tar tre dager, hot wings, salater, soft serve på Jersey-melk og milkshakes. Velg restaurant for hele menyen med priser og allergener.',
          'Each restaurant has its own menu, built on the same foundation: burgers with a 150 g patty of beef we grind ourselves, fresh buns, triple-cooked fries that take three days, hot wings, salads, Jersey-milk soft serve and milkshakes. Pick a restaurant for the full menu with prices and allergens.')
    G.add('menu.hub.cta', 'Se menyen', 'See the menu'); G.add('menu.hub.dishes', 'retter', 'dishes')
    cards = ''
    for v in C['venues']:
        vv = kv.venue(v['slug']); n = sum(len(s['items']) for s in v['menu']['sections'])
        secs = ', '.join(s['label'] for s in v['menu']['sections'])
        cards += (f'      <article class="card venue-card"><figure class="photo" style="aspect-ratio:4/3"><img src="{v["menu"]["photo"]}" alt="{e(v["menu"]["photoLabel"])}" loading="lazy"></figure>'
                  f'<div class="kv-eyebrow" style="margin-top:var(--space-4)">{e(vv["area"])}, {e(vv["city"])}</div><h2 class="display-3">Kverneriet {e(v["name"])}</h2>'
                  f'<p class="caption" style="margin-top:var(--space-2)">{n} <span data-i18n="menu.hub.dishes">retter</span> · {e(secs)}</p>'
                  f'<div class="venue-card__actions"><a class="btn btn--primary btn--md" href="{kv.url(v["slug"] + "-menu")}" data-i18n="menu.hub.cta">Se menyen</a></div></article>\n')
    return head('meny', p) + f'''<body>

{chrome.header()}
<main id="main">
  <div class="wrap" style="padding-top:var(--space-8);padding-bottom:var(--section-y)">
    <header class="sec-head sec-head--center">
      <div class="sec-head__rule"></div>
      <span class="kv-eyebrow" data-i18n="menu.eyebrow">Én meny per restaurant</span>
      <h1 class="hero-title" style="font-size:var(--type-display-1)" data-i18n="menu.hub.h1">Menyene våre</h1>
      <p class="sec-head__intro" data-i18n="menu.hub.intro">{e(G._D['no']['menu.hub.intro'])}</p>
    </header>
    <div class="grid-3" style="margin-top:var(--space-7)">
{cards}    </div>
  </div>
</main>

{chrome.footer()}
{modal.MODAL}
</body>
</html>
'''

def build():
    for v in C['venues']:
        kv.write(v['slug'] + '-menu', venue_menu_page(v)); print(kv.path(v['slug'] + '-menu'), 'ok')
    kv.write('meny', hub_page()); print(kv.path('meny'), 'ok')

if __name__ == '__main__':
    build(); G.write()
