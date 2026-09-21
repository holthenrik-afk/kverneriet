#!/usr/bin/env python3
"""Bloggen: /blogg/ (liste) og /blogg/<slug>/ (innlegg) fra content/blog.json (Sanity «post» via fetch_sanity.py).
Innlegg får BlogPosting-markup, brødsmuler og deling; lista har BreadcrumbList. Uten innlegg bygges bare
en tom liste med en vennlig tekst, og bloggen holdes utenfor sitemap/nav."""
import os, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv, chrome, modal, i18n_gen as G, portable as PT
os.chdir(kv.ROOT)

e = kv.esc
POSTS = [p for p in kv.posts() if p.get('slug') and p.get('publishedAt')]
POSTS.sort(key=lambda p: p['publishedAt'], reverse=True)
MONTHS = ['januar', 'februar', 'mars', 'april', 'mai', 'juni', 'juli', 'august', 'september', 'oktober', 'november', 'desember']

def nice_date(iso):
    d = datetime.date.fromisoformat(iso[:10])
    return f'{d.day}. {MONTHS[d.month - 1]} {d.year}'

def head(title, desc, extra=''):
    return f'''<!DOCTYPE html>
<html lang="nb">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<!-- seo:start -->
<!-- seo:end -->
<link rel="stylesheet" href="/styles.css">
<link rel="stylesheet" href="/site.css">
<script src="/content/i18n.js" defer></script>
<script src="/content/i18n-gen.js" defer></script>
<script src="/site.js" defer></script>
</head>
'''

def card(p):
    img = p.get('mainImage') or {}
    pic = f'<figure class="photo" style="aspect-ratio:4/3"><img src="{e(img["url"])}" alt="{e(img.get("alt", ""))}" loading="lazy"{f" width=\"{img['w']}\" height=\"{img['h']}\"" if img.get('w') else ""}></figure>' if img.get('url') else ''
    return (f'<article class="card venue-card post-card">{pic}<div class="kv-eyebrow" style="margin-top:var(--space-4)">{nice_date(p["publishedAt"])}</div>'
            f'<h2 class="display-4"><a href="/blogg/{e(p["slug"])}/">{e(p["title"])}</a></h2>'
            f'<p class="menu-item__desc" style="margin-top:var(--space-2)">{e(p.get("excerpt") or PT.plain(p.get("body"), 140))}</p>'
            f'<div class="venue-card__actions"><a class="btn btn--outline btn--sm" href="/blogg/{e(p["slug"])}/" data-i18n="blog.read">Les innlegget</a></div></article>')

def featured(p):
    img = p.get('mainImage') or {}
    pic = f'<figure class="photo" style="aspect-ratio:4/3"><img src="{e(img["url"])}" alt="{e(img.get("alt", ""))}" fetchpriority="high"{f" width=\"{img['w']}\" height=\"{img['h']}\"" if img.get('w') else ""}></figure>' if img.get('url') else ''
    return (f'<article class="post-featured grid-2 grid-2--start">{pic}<div><span class="kv-eyebrow" data-i18n="blog.latest">Nyeste innlegg</span>'
            f'<h2 class="display-2" style="margin-top:var(--space-3)"><a href="/blogg/{e(p["slug"])}/">{e(p["title"])}</a></h2>'
            f'<p class="lede" style="margin-top:var(--space-4)">{e(p.get("excerpt") or PT.plain(p.get("body"), 200))}</p>'
            f'<p class="caption" style="margin-top:var(--space-3)">{nice_date(p["publishedAt"])}{(" · " + e(p["author"])) if p.get("author") else ""}</p>'
            f'<div style="margin-top:var(--space-5)"><a class="btn btn--primary btn--md" href="/blogg/{e(p["slug"])}/" data-i18n="blog.read">Les innlegget</a></div></div></article>')

def index_page():
    sc = kv.site_copy(); bt = sc.get('blogTitle') or {}; bi = sc.get('blogIntro') or {}
    G.add('blog.title', bt.get('no') or 'Blogg', bt.get('en') or 'Blog'); G.add('blog.eyebrow', 'Nytt fra Kverneriet', 'News from Kverneriet'); G.add('blog.read', 'Les innlegget', 'Read the post')
    G.add('blog.latest', 'Nyeste innlegg', 'Latest post'); G.add('blog.more', 'Flere innlegg', 'More posts')
    G.add('blog.intro', bi.get('no') or 'Her skriver vi om burgere og håndverket bak dem: kjøttet vi kverner selv, fries som tar tre dager, det som skjer på kjøkkenet, og guider til å spise godt i Oslo og Tønsberg.',
          bi.get('en') or 'Here we write about burgers and the craft behind them: the beef we grind ourselves, fries that take three days, what happens in the kitchen, and guides to eating well in Oslo and Tønsberg.')
    G.add('blog.empty', 'Første innlegg er på vei. I mellomtiden finner du menyene og restaurantene under.', 'The first post is on its way. Meanwhile, the menus and restaurants are below.')
    G.add('blog.ctaTitle', 'Sulten etter å ha lest?', 'Hungry after reading?'); G.add('blog.ctaBody', 'Book bord på Majorstua, Solli plass eller i Tønsberg, eller bestill take-away og hent selv.', 'Book a table at Majorstua, Solli plass or in Tønsberg, or order take-away for pick-up.')
    if POSTS:
        rest = POSTS[1:]
        body = featured(POSTS[0]) + ((f'<div class="divider" style="margin-top:var(--space-8)"><span data-i18n="blog.more">Flere innlegg</span></div><div class="grid-3" style="margin-top:var(--space-6)">{"".join(card(p) for p in rest)}</div>') if rest else '')
    else:
        body = '<p class="lede" style="margin-top:var(--space-5)" data-i18n="blog.empty">Første innlegg er på vei. I mellomtiden finner du menyene og restaurantene under.</p>'
    venues = ''.join(f'<a class="btn btn--outline btn--md" href="{kv.url(v["slug"])}">{e(v["fullName"])}</a>' for v in kv.venues()['venues'])
    return head(f'{G._D["no"]["blog.title"]} – nytt fra Kverneriet', 'Nyheter, nye retter og historier fra kjøkkenet på Kverneriet i Oslo og Tønsberg.') + f'''<body>

{chrome.header()}
<main id="main">
  <section class="section">
    <div class="wrap">
      <nav class="crumbs" aria-label="Brødsmuler"><ol><li><a href="/">Kverneriet</a></li><li><span aria-current="page" data-i18n="blog.title">{e(G._D["no"]["blog.title"])}</span></li></ol></nav>
      <header class="sec-head">
        <div class="sec-head__rule"></div>
        <span class="kv-eyebrow" data-i18n="blog.eyebrow">Nytt fra Kverneriet</span>
        <h1 class="hero-title" style="font-size:var(--type-display-1)" data-i18n="blog.title">{e(G._D["no"]["blog.title"])}</h1>
        <p class="sec-head__intro" data-i18n="blog.intro">{e(G._D["no"]["blog.intro"])}</p>
      </header>
      <div style="margin-top:var(--space-7)">{body}</div>
    </div>
  </section>

  <section class="section section--tint">
    <div class="wrap grid-2 grid-2--start">
      <div>
        <header class="sec-head"><div class="sec-head__rule"></div><h2 class="display-3" data-i18n="blog.ctaTitle">Sulten etter å ha lest?</h2></header>
        <p class="lede" style="margin-top:var(--space-4)" data-i18n="blog.ctaBody">Book bord på Majorstua, Solli plass eller i Tønsberg, eller bestill take-away og hent selv.</p>
        <div style="margin-top:var(--space-5);display:flex;gap:10px;flex-wrap:wrap"><a class="btn btn--primary btn--md" href="/majorstua/#booking" data-book-open data-i18n="act.book">Book bord</a><a class="btn btn--outline btn--md" href="/takeaway/" data-order-open data-i18n="act.order">Bestill take-away</a></div>
      </div>
      <div><div class="kv-eyebrow" style="margin-bottom:var(--space-3)" data-i18n="home.restTitle">Restaurantene</div><div style="display:flex;gap:10px;flex-wrap:wrap">{venues}<a class="btn btn--ghost btn--md" href="/meny/" data-i18n="act.seeMenu">Se menyen</a></div></div>
    </div>
  </section>
</main>

{chrome.footer()}
{modal.MODAL}
</body>
</html>
'''

def post_page(p):
    img = p.get('mainImage') or {}
    hero = f'<figure class="photo post__hero" style="aspect-ratio:16/9;margin-top:var(--space-6)"><img src="{e(img["url"])}" alt="{e(img.get("alt", ""))}" fetchpriority="high"{f" width=\"{img['w']}\" height=\"{img['h']}\"" if img.get('w') else ""}></figure>' if img.get('url') else ''
    author = f' · {e(p["author"])}' if p.get('author') else ''
    desc = p.get('excerpt') or PT.plain(p.get('body'), 150)
    return head(p.get('seoTitle') or f'{p["title"]} – Kverneriet', desc) + f'''<body>

{chrome.header()}
<main id="main">
  <article class="wrap wrap--narrow post" style="padding-top:var(--space-8);padding-bottom:var(--section-y)">
    <nav class="crumbs" aria-label="Brødsmuler"><ol><li><a href="/">Kverneriet</a></li><li><a href="/blogg/" data-i18n="blog.title">Blogg</a></li><li><span aria-current="page">{e(p['title'])}</span></li></ol></nav>
    <header class="sec-head">
      <div class="sec-head__rule"></div>
      <span class="kv-eyebrow"><time datetime="{e(p['publishedAt'][:10])}">{nice_date(p['publishedAt'])}</time>{author}</span>
      <h1 class="display-1">{e(p['title'])}</h1>
      {('<p class="lede" style="margin-top:var(--space-4)">' + e(p['excerpt']) + '</p>') if p.get('excerpt') else ''}
    </header>
    {hero}
    <div class="post__body">
{PT.to_html(p.get('body'))}
    </div>
    <div style="margin-top:var(--space-8);display:flex;gap:10px;flex-wrap:wrap">
      <a class="btn btn--outline btn--md" href="/blogg/"><span class="btn__glyph" aria-hidden="true">«</span> <span data-i18n="blog.all">Alle innlegg</span></a>
      <a class="btn btn--primary btn--md" href="/majorstua/#booking" data-book-open data-i18n="act.book">Book bord</a>
    </div>
  </article>
</main>

{chrome.footer()}
{modal.MODAL}
</body>
</html>
'''

def register():
    import pages
    kv.register('blogg', 'blogg/index.html', '/blogg/')
    pages.PAGES['blogg'] = dict(title='Blogg – nytt fra Kverneriet', desc='Nyheter, nye retter og historier fra kjøkkenet på Kverneriet i Oslo og Tønsberg.', img='/assets/img/index-hero.jpg')
    for p in POSTS:
        kv.register('blog-' + p['slug'], f'blogg/{p["slug"]}/index.html', f'/blogg/{p["slug"]}/')
        img = (p.get('mainImage') or {}).get('url') or '/assets/img/index-hero.jpg'
        pages.PAGES['blog-' + p['slug']] = dict(title=(p.get('seoTitle') or f'{p["title"]} – Kverneriet')[:60], desc=(p.get('excerpt') or PT.plain(p.get('body'), 150))[:155], img=img, post=p)
register()

def build():
    G.add('blog.all', 'Alle innlegg', 'All posts')
    os.makedirs('blogg', exist_ok=True)
    open('blogg/index.html', 'w', encoding='utf-8').write(index_page())
    for p in POSTS:
        os.makedirs(f'blogg/{p["slug"]}', exist_ok=True)
        open(f'blogg/{p["slug"]}/index.html', 'w', encoding='utf-8').write(post_page(p))
    print(f'blogg: {len(POSTS)} innlegg')

if __name__ == '__main__':
    build(); G.write()
