"""Header, mobilpanel og footer – likt på alle sider, skrevet fra ett sted (tools/chrome.py).
Footeren bærer NAP (navn, adresse, telefon) for alle tre restaurantene, så hver side i nettstedet
sier hvor Kverneriet er. Brukes av build-venue.py, build-landing.py, build-menu.py og build.py."""
import kv, i18n_gen as G

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
    <nav class="mobile-panel" id="mobile-panel" aria-label="Hovedmeny">
      <p class="mobile-panel__gruppe" data-i18n="nav.venues">Restauranter</p>
{panel}      <p class="mobile-panel__gruppe" data-i18n="nav.eat">Mat og drikke</p>
      <a href="{menu_href}" data-i18n="act.menu">Meny</a>
      <a href="/fries/" data-i18n="lp.fries">Fries</a>
      <a href="/soft-serve/" data-i18n="lp.softserve">Soft serve</a>
      <a href="/lunsj/" data-i18n="lp.lunch">Lunsj</a>
      <a href="/middag/" data-i18n="lp.dinner">Middag</a>
      <a href="/cocktails/" data-i18n="lp.cocktails">Cocktails</a>
      <a href="/takeaway/" data-i18n="act.takeaway">Take-away</a>
      <p class="mobile-panel__gruppe" data-i18n="nav.occasions">Anledninger</p>
      <a href="/julebord/" data-i18n="lp.xmas">Julebord</a>
      <a href="/selskap/" data-i18n="lp.groups">Selskap og grupper</a>
      <a href="/late-night/" data-i18n="lp.late">Late night</a>
      <p class="mobile-panel__gruppe" data-i18n="nav.more">Mer</p>
      <a href="/om/" data-i18n="nav.about">Om Kverneriet</a>
      <a href="/sporsmal/" data-i18n="nav.faq">Spørsmål og svar</a>
      <a href="{ORG['giftcard']}" data-i18n="act.giftcards">Gavekort</a>
{blog_link('      <a href="/blogg/" data-i18n="blog.title">Blogg</a>')}      <a href="https://join.kverneriet.com/" data-i18n="act.work">Jobb hos oss</a>
    </nav>
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
    <span class="pipe" aria-hidden="true">|</span><a href="/fries/" data-i18n="lp.fries">Fries</a>
    <span class="pipe" aria-hidden="true">|</span><a href="/soft-serve/" data-i18n="lp.softserve">Soft serve</a>
    <span class="pipe" aria-hidden="true">|</span><a href="/lunsj/" data-i18n="lp.lunch">Lunsj</a>
    <span class="pipe" aria-hidden="true">|</span><a href="/middag/" data-i18n="lp.dinner">Middag</a>
    <span class="pipe" aria-hidden="true">|</span><a href="/cocktails/" data-i18n="lp.cocktails">Cocktails</a>
    <span class="pipe" aria-hidden="true">|</span><a href="/julebord/" data-i18n="lp.xmas">Julebord</a>
    <span class="pipe" aria-hidden="true">|</span><a href="/selskap/" data-i18n="lp.groups">Selskap og grupper</a>
    <span class="pipe" aria-hidden="true">|</span><a href="/late-night/" data-i18n="lp.late">Late night</a>
{blog_link('    <span class="pipe" aria-hidden="true">|</span><a href="/blogg/" data-i18n="blog.title">Blogg</a>')}    <span class="pipe" aria-hidden="true">|</span><a href="/om/" data-i18n="nav.about">Om Kverneriet</a>
    <span class="pipe" aria-hidden="true">|</span><a href="/sporsmal/" data-i18n="nav.faq">Spørsmål og svar</a>
    <span class="pipe" aria-hidden="true">|</span><a href="{ORG['giftcard']}" data-i18n="act.giftcards">Gavekort</a>
    <span class="pipe" aria-hidden="true">|</span><a href="https://join.kverneriet.com/" data-i18n="foot.work">Jobb hos oss</a>
    <span class="pipe" aria-hidden="true">|</span><a href="{ORG['sameAs'][0]}" rel="noopener" target="_blank">Facebook</a>
    <span class="pipe" aria-hidden="true">|</span><button type="button" class="link-btn" data-consent-open data-i18n="consent.title">Informasjonskapsler</button>
  </div>
</footer>
'''


# Googles kildevelger kjente ikke kverneriet.no 23.10.2026. Nettstedet er nytt, og
# Google skriver at kilder som ikke oppdateres jevnlig kan mangle i velgeren.
# Knappen er derfor ferdig bygget, men skrudd av: en knapp som sender gjesten til
# Google og ikke finner Kverneriet, er verre enn ingen knapp.
#
# SLIK SKRUR DU DEN PÅ: åpne https://www.google.com/preferences/source?q=kverneriet.no
# mens du er logget inn på Google og søk opp kverneriet.no. Dukker den opp som et valg,
# setter du linja under til True og bygger på nytt. Ingenting annet trengs.
PREFERRED_SOURCE_PA = False


def preferred_source():
    """Googles «foretrukne kilder» – knappen som lar leseren velge Kverneriet i Google.

    Google dokumenterer to måter: et JavaScript fra news.google.com som rendrer en
    ferdig knapp, og en ren lenke. Vi bruker lenken. Skriptet er på 140 kB, det er en
    tredjepart som kan sette informasjonskapsler før gjesten har svart på
    samtykkebanneret, og knappen ville kommet i Googles utseende midt i vårt eget.
    Lenken går til nøyaktig samme sted.

    Ordlyden på knappen er den Google selv bruker i sin norske knappegrafikk, så
    gjesten kjenner igjen det hun møter på den andre siden.
    Kilde: https://developers.google.com/search/docs/appearance/preferred-sources
    """
    if not PREFERRED_SOURCE_PA:
        return ''
    domene = kv.DOMAIN.split('//', 1)[-1].strip('/')
    G.add('pref.body',
          f'Velger du {ORG["name"]} som foretrukket kilde i Google, viser Google oss oftere når vi har skrevet noe nytt.',
          f'Choose {ORG["name"]} as a preferred source in Google and we show up more often when we have written something new.')
    G.add('pref.cta', 'Legg til som foretrukket kilde på Google', 'Add as a preferred source on Google')
    return (f'    <aside class="pref-kilde">\n'
            f'      <p class="caption" data-i18n="pref.body">{kv.esc(G._D["no"]["pref.body"])}</p>\n'
            f'      <a class="btn btn--outline btn--sm" href="https://www.google.com/preferences/source?q={domene}"'
            f' target="_blank" rel="noopener" data-track="cta:preferred:google" data-i18n="pref.cta">'
            f'Legg til som foretrukket kilde på Google</a>\n'
            f'    </aside>\n')

G.add('nav.venues', 'Restauranter', 'Restaurants')
G.add('nav.eat', 'Mat og drikke', 'Food and drink')
G.add('nav.occasions', 'Anledninger', 'Occasions')
G.add('nav.more', 'Mer', 'More')
G.add('nav.about', 'Om Kverneriet', 'About Kverneriet')
G.add('nav.faq', 'Spørsmål og svar', 'Questions and answers')

SECTIONS = [('about', 'v.about', 'Om'), ('bar', 'v.barEyebrow', 'Baren'), ('gallery', 'v.gallery', 'Galleri'), ('booking', 'v.booking', 'Booking'),
            ('practical', 'v.practical', 'Praktisk info'), ('faq', 'v.faq', 'Spørsmål')]

def venue_nav(slug, on_menu=False):
    """Raden med restaurantens egne seksjoner. Samme rekkefølge på restaurantsiden og på menysiden,
    så gjesten ikke mister veien tilbake til «Om» når hun står i menyen (ønske fra Henrik 07.10.2026).
    Første punkt heter restauranten, ikke «Om». På menysiden peker lenkene hjem til restaurantsiden."""
    v = kv.venue(slug)
    base = kv.url(slug) if on_menu else ''
    items = f'<li><a href="{base}#about">{kv.esc(v["name"])}</a></li>'
    items += ''.join(f'<li><a href="{base}#{i}" data-i18n="{k}">{kv.esc(t)}</a></li>' for i, k, t in SECTIONS[1:])
    items += (f'<li><a href="{kv.url(slug + "-menu")}" aria-current="page" class="is-active" data-i18n="act.menu">Meny</a></li>'
              if on_menu else
              f'<li><a href="{kv.url(slug + "-menu")}" data-i18n="act.menu">Meny</a></li>')
    spy = '' if on_menu else ' data-scrollspy'
    return (f'<nav class="section-nav section-nav--venue" aria-label="{kv.esc(v["name"])}"{spy}>\n'
            f'  <ul>{items}</ul>\n</nav>')

# Metricool-sporingspiksel. Et rent bilde-kall, ingen JavaScript og ingen informasjonskapsel fra
# vår side. Ligger rett før </body> på hver side så den ikke forsinker noe som gjesten ser.
PIXEL = ('<img src="https://tracker.metricool.com/c3po.jpg?hash=bfb4103a56494b4aa00b3a58c4162aaf" '
         'alt="" width="1" height="1" aria-hidden="true" referrerpolicy="no-referrer-when-downgrade" '
         'style="position:absolute;width:1px;height:1px;opacity:0;pointer-events:none">')
PIXEL_RE = r'<img src="https://tracker\.metricool\.com/c3po\.jpg[^>]*>\n?'

def add_pixel(html):
    """Setter inn sporingspikselen én gang per side, og bytter den ut hvis den finnes fra før."""
    import re as _re
    html = _re.sub(PIXEL_RE, '', html)
    return html.replace('</body>', PIXEL + '\n</body>', 1)

# Google-taggen: GA4 (G-QP2HX05YNB) og Google Ads (AW-679169843), de samme ID-ene som kverneriet.com,
# så historikken henger sammen. Consent Mode v2: alt står som «denied» til gjesten har sagt ja i
# banneret (site.js), og et tidligere valg leses fra localStorage før taggen lastes.
GA4, ADS = 'G-QP2HX05YNB', 'AW-679169843'
TAG_HEAD = f'''<!-- sporing:start -->
<script>
window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}
(function(){{var c=null;try{{c=localStorage.getItem('kv-consent');}}catch(e){{}}var g=c==='granted'?'granted':'denied';
gtag('consent','default',{{ad_storage:g,ad_user_data:g,ad_personalization:g,analytics_storage:g,wait_for_update:500}});}})();
gtag('set','ads_data_redaction',true);gtag('set','url_passthrough',true);
gtag('js',new Date());gtag('config','{GA4}');gtag('config','{ADS}');
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4}"></script>
<!-- sporing:end -->
'''
CONSENT = '''<!-- samtykke:start -->
<div class="consent" role="dialog" aria-labelledby="consent-title" hidden>
  <p class="consent__title kv-eyebrow" id="consent-title" data-i18n="consent.title">Informasjonskapsler</p>
  <p class="consent__text" data-i18n="consent.text">Vi bruker informasjonskapsler fra Google og Meta for å se hvordan siden brukes og om annonsene våre virker. Du velger selv, og kan endre valget nederst på siden.</p>
  <div class="consent__actions">
    <button type="button" class="btn btn--outline btn--md" data-consent="denied" data-i18n="consent.deny">Bare nødvendige</button>
    <button type="button" class="btn btn--solid btn--md" data-consent="granted" data-i18n="consent.accept">Godta</button>
  </div>
</div>
<!-- samtykke:end -->
'''
G.add('consent.title', 'Informasjonskapsler', 'Cookies')
G.add('consent.text', 'Vi bruker informasjonskapsler fra Google og Meta for å se hvordan siden brukes og om annonsene våre virker. Du velger selv, og kan endre valget nederst på siden.',
      'We use cookies from Google and Meta to see how the site is used and whether our ads work. It is your choice, and you can change it at the bottom of the page.')
G.add('consent.deny', 'Bare nødvendige', 'Only necessary')
G.add('consent.accept', 'Godta', 'Accept')

def add_tracking(html):
    """Google-taggen øverst i <head> og samtykkebanneret før </body>, én gang per side."""
    import re as _re
    html = _re.sub(r'<!-- sporing:start -->.*?<!-- sporing:end -->\n', '', html, flags=_re.S)
    html = _re.sub(r'<!-- samtykke:start -->.*?<!-- samtykke:end -->\n', '', html, flags=_re.S)
    html = _re.sub(r'(<meta name="viewport"[^>]*>\n)', lambda m: m.group(1) + TAG_HEAD, html, count=1)
    return html.replace('</body>', CONSENT + '</body>', 1)

HEADER_RE = r'(?:<a class="skip-link"[^>]*>.*?</a>\n)?<header class="site-header">.*?</header>\n'
FOOTER_RE = r'<footer class="site-footer">.*?</footer>\n'

def apply(html, active=None, menu_href='/meny/'):
    """Bytter header og footer i en eksisterende side."""
    import re
    html, n1 = re.subn(HEADER_RE, lambda m: header(active, menu_href), html, count=1, flags=re.S)
    html, n2 = re.subn(FOOTER_RE, lambda m: footer(menu_href), html, count=1, flags=re.S)
    if n1 != 1 or n2 != 1: raise SystemExit(f'chrome: header {n1} footer {n2}')
    return html
