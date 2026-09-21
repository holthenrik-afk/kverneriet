"""Header, mobilpanel og footer – likt på alle sider, skrevet fra ett sted (tools/chrome.py).
Footeren bærer NAP (navn, adresse, telefon) for alle tre restaurantene, så hver side i nettstedet
sier hvor Kverneriet er. Brukes av build-venue.py, build-landing.py, build-menu.py og build.py."""
import kv

V = kv.venues()
ORG = V['org']

def blog_link(markup):
    """Bloggen lenkes først når det finnes innlegg."""
    return (markup + '\n') if kv.posts() else ''

def header(active=None, menu_href='/meny/'):
    links = ''.join(f'      <a{" class=\"is-active\"" if v["slug"] == active else ""} href="{kv.url(v["slug"])}">{kv.esc(v["name"])}</a>\n' for v in V['venues'])
    panel = ''.join(f'      <a href="{kv.url(v["slug"])}"{" class=\"is-active\"" if v["slug"] == active else ""}>{kv.esc(v["name"])}</a>\n' for v in V['venues'])
    return f'''<a class="skip-link" href="#main" data-i18n="a11y.skip">Hopp til innholdet</a>
<header class="site-header">
  <div class="site-header__inner site-header__inner--grid">
    <a class="site-header__logo" href="/" aria-label="Kverneriet – til forsiden">
      <img src="/assets/logo.svg" alt="Kverneriet" width="479" height="100">
    </a>
    <nav class="venue-nav" aria-label="Restauranter">
{links}    </nav>
    <div class="site-header__actions">
      <div class="lang-switch" role="group" aria-label="Språk / Language">
        <button type="button" data-lang="no" class="is-on" aria-pressed="true">NO</button><span class="sep" aria-hidden="true">/</span><button type="button" data-lang="en" aria-pressed="false">EN</button>
      </div>
      <button class="btn btn--primary btn--sm" type="button" data-book-open data-track="cta:book" data-i18n="act.book">Book bord</button>
      <button class="icon-btn nav-burger" id="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-panel" aria-label="Meny">
        <svg class="icon-menu" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><line x1="4" y1="6" x2="20" y2="6"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/></svg>
        <svg class="icon-close" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><line x1="6" y1="6" x2="18" y2="18"/><line x1="6" y1="18" x2="18" y2="6"/></svg>
      </button>
    </div>
    <div class="mobile-panel" id="mobile-panel">
      <a href="/" data-i18n="act.home">Hjem</a>
{panel}      <a href="{menu_href}" data-i18n="act.menu">Meny</a>
      <a href="/takeaway/" data-i18n="act.takeaway">Take-away</a>
      <button type="button" class="mobile-panel__btn" data-book-open data-i18n="act.book">Book bord</button>
      <a href="/lunsj/" data-i18n="lp.lunch">Lunsj</a>
      <a href="/julebord/" data-i18n="lp.xmas">Julebord</a>
      <a href="/selskap/" data-i18n="lp.groups">Selskap og grupper</a>
      <a href="/late-night/" data-i18n="lp.late">Late night</a>
{blog_link('      <a href="/blogg/" data-i18n="blog.title">Blogg</a>')}      <a href="{ORG['giftcard']}" data-i18n="act.giftcards">Gavekort</a>
      <a href="https://join.kverneriet.com/" data-i18n="act.work">Jobb hos oss</a>
    </div>
  </div>
</header>
'''

def hours_summary(v):
    """Kort åpningstid-linje til footeren: 'Kjøkken man 16–21, tir–fre 11–22, lør 12–22, søn 12–21'."""
    parts = [f'{kv.day_range(h["days"])} {kv.hhmm(h["opens"])}–{kv.hhmm(h["closes"])}' for h in v['hours']['kitchen']]
    return ', '.join(parts)

def footer(menu_href='/meny/'):
    cols = ''
    for v in V['venues']:
        a = v['address']
        cols += (f'    <div class="site-footer__venue">\n'
                 f'      <a class="kv-eyebrow" href="{kv.url(v["slug"])}">{kv.esc(v["fullName"])}</a>\n'
                 f'      <p>{kv.esc(a["street"])}, {a["postalCode"]} {kv.esc(a["city"])}</p>\n'
                 f'      <p><a href="tel:{ORG["telephone"]}">{ORG["telephoneDisplay"]}</a> · <a href="{kv.url(v["slug"])}#practical" data-i18n="foot.hours">Åpningstider</a> · <a href="{kv.url(v["slug"] + "-menu")}" data-i18n="act.menu">Meny</a></p>\n'
                 f'    </div>\n')
    return f'''<footer class="site-footer">
  <div class="site-footer__venues">
{cols}  </div>
  <div class="site-footer__row">
    <span class="kv-eyebrow">Kverneriet &copy; 2026</span>
    <span class="pipe" aria-hidden="true">|</span><a href="{menu_href}" data-i18n="act.menu">Meny</a>
    <span class="pipe" aria-hidden="true">|</span><a href="/takeaway/" data-i18n="act.takeaway">Take-away</a>
    <span class="pipe" aria-hidden="true">|</span><a href="/lunsj/" data-i18n="lp.lunch">Lunsj</a>
    <span class="pipe" aria-hidden="true">|</span><a href="/julebord/" data-i18n="lp.xmas">Julebord</a>
    <span class="pipe" aria-hidden="true">|</span><a href="/selskap/" data-i18n="lp.groups">Selskap og grupper</a>
    <span class="pipe" aria-hidden="true">|</span><a href="/late-night/" data-i18n="lp.late">Late night</a>
{blog_link('    <span class="pipe" aria-hidden="true">|</span><a href="/blogg/" data-i18n="blog.title">Blogg</a>')}    <span class="pipe" aria-hidden="true">|</span><a href="{ORG['giftcard']}" data-i18n="act.giftcards">Gavekort</a>
    <span class="pipe" aria-hidden="true">|</span><a href="https://join.kverneriet.com/" data-i18n="foot.work">Jobb hos oss</a>
    <span class="pipe" aria-hidden="true">|</span><a href="{ORG['sameAs'][0]}" rel="noopener" target="_blank">Facebook</a>
  </div>
</footer>
'''

HEADER_RE = r'(?:<a class="skip-link"[^>]*>.*?</a>\n)?<header class="site-header">.*?</header>\n'
FOOTER_RE = r'<footer class="site-footer">.*?</footer>\n'

def apply(html, active=None, menu_href='/meny/'):
    """Bytter header og footer i en eksisterende side."""
    import re
    html, n1 = re.subn(HEADER_RE, lambda m: header(active, menu_href), html, count=1, flags=re.S)
    html, n2 = re.subn(FOOTER_RE, lambda m: footer(menu_href), html, count=1, flags=re.S)
    if n1 != 1 or n2 != 1: raise SystemExit(f'chrome: header {n1} footer {n2}')
    return html
