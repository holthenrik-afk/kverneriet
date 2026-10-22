#!/usr/bin/env python3
"""/sporsmal/ – alle spørsmålene på ett sted.

Gruppene kommer fra faq.GRUPPER(), som bygger svarene fra content/venues.json og
content/menus.js. Under gruppene listes spørsmålene som allerede ligger på de andre
sidene, med lenke dit, så siden samler alt uten å kopiere svarene to ganger.

FAQPage-markup lages av seo_head.py, som leser spørsmålene tilbake ut av den ferdige
HTML-en. Kjør: python3 tools/build.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv, chrome, modal, faq, pages, i18n_gen as G
os.chdir(kv.ROOT)

V = kv.venues()
e = kv.esc

# Hvor de øvrige spørsmålene bor. Vi lenker dit i stedet for å gjenta svarene,
# både fordi svarene er knyttet til siden de står på («Book bord her»), og fordi
# Google ikke skal se den samme FAQ-en to ganger på samme nettsted.
ANDRE = [
    ('majorstua', 'Kverneriet Majorstua', 'Kverneriet Majorstua'),
    ('solli', 'Kverneriet Solli', 'Kverneriet Solli'),
    ('tonsberg', 'Kverneriet Tønsberg', 'Kverneriet Tønsberg'),
    ('takeaway', 'Take-away og levering', 'Take-away and delivery'),
    ('lunsj', 'Lunsj', 'Lunch'),
    ('middag', 'Middag', 'Dinner'),
    ('selskap', 'Selskap og grupper', 'Parties and groups'),
    ('julebord', 'Julebord', 'Christmas parties'),
    ('late-night', 'Late night', 'Late night'),
    ('cocktails', 'Baren', 'The bar'),
    ('fries', 'Fries', 'Fries'),
    ('soft-serve', 'Soft serve', 'Soft serve'),
]


def build():
    meta = pages.PAGES['sporsmal']
    G.add('faq.pageEyebrow', 'Godt å vite', 'Good to know')
    G.add('faq.pageTitle', 'Spørsmål og svar', 'Questions and answers')
    G.add('faq.pageLede',
          'Her er det gjestene spør oss om oftest. Finner du ikke svaret, ring oss eller send en e-post, '
          'så hjelper vi deg.',
          'The things guests ask us most often. If the answer is not here, call or e-mail us and we will help you.')
    G.add('faq.moreTitle', 'Spørsmål om én bestemt side', 'Questions about a specific page')
    G.add('faq.moreLede',
          'Åpningstider, booking og veibeskrivelse står på hver restaurantside. Resten av spørsmålene '
          'ligger der de hører hjemme.',
          'Opening hours, booking and directions are on each restaurant page. The rest of the questions '
          'sit where they belong.')
    G.add('faq.contact', 'Kontakt oss', 'Contact us')
    G.add('faq.sokLabel', 'Søk i spørsmålene', 'Search the questions')
    G.add('faq.sokHint', 'Prøv «hund», «uteservering», «glutenfri» eller «gavekort»',
          'Try “dog”, “outdoor”, “gluten free” or “gift card”')
    G.add('faq.sokClear', 'Tøm søket', 'Clear search')
    G.add('faq.sokTreff', 'Viser {n} av {m} spørsmål', 'Showing {n} of {m} questions')
    G.add('faq.sokTom', 'Vi fant ingenting på det. Spør oss direkte, så svarer vi.',
          'We found nothing for that. Ask us directly and we will answer.')

    blokker = ''
    for key, tn, te, items in faq.GRUPPER():
        G.add(f'faq.s.{key}.t', tn, te)
        blokker += (f'      <div class="faq-gruppe">\n'
                    f'        <h2 class="display-3" data-i18n="faq.s.{key}.t">{e(tn)}</h2>\n'
                    f'        <div class="faq" style="margin-top:var(--space-5)">{faq.rows(items, sok=True)}</div>\n'
                    f'      </div>\n')

    andre = ''
    for slug, tn, te in ANDRE:
        G.add(f'faq.more.{slug}', tn, te)
        andre += f'<a class="btn btn--outline btn--sm" href="{kv.url(slug)}#faq" data-i18n="faq.more.{slug}">{e(tn)}</a>'

    # Hver restaurant har sin egen postkasse. Siden dekker alle tre, så én felles
    # «Kontakt oss» ville sendt spørsmål om Solli og Tønsberg til Majorstua.
    G.add('faq.contactEyebrow', 'Spør oss direkte', 'Ask us directly')
    kontakt = ''.join(
        f'<a class="btn btn--ghost btn--md" href="mailto:{v["email"]}">{e(v["name"])}</a>'
        for v in V['venues'] if v.get('email'))

    org = V['org']
    html = f'''<!DOCTYPE html>
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
  <section class="section">
    <div class="wrap wrap--narrow">
      <nav class="crumbs" aria-label="Brødsmuler"><ol><li><a href="/">Kverneriet</a></li><li><span aria-current="page" data-i18n="faq.pageTitle">Spørsmål og svar</span></li></ol></nav>
      <header class="sec-head">
        <div class="sec-head__rule"></div>
        <span class="kv-eyebrow" data-i18n="faq.pageEyebrow">Godt å vite</span>
        <h1 class="display-1" data-i18n="faq.pageTitle">Spørsmål og svar</h1>
      </header>
      <p class="lede" style="margin-top:var(--space-5)" data-i18n="faq.pageLede">Her er det gjestene spør oss om oftest. Finner du ikke svaret, ring oss eller send en e-post, så hjelper vi deg.</p>
      <div class="faq-sok" data-faq-sok>
        <label class="field__label" for="faq-sok" data-i18n="faq.sokLabel">Søk i spørsmålene</label>
        <div class="faq-sok__felt">
          <svg class="faq-sok__ikon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><line x1="16.5" y1="16.5" x2="21" y2="21"/></svg>
          <input id="faq-sok" type="search" autocomplete="off" enterkeyhint="search"
                 data-i18n-ph="faq.sokHint" placeholder="Prøv «hund», «uteservering», «glutenfri» eller «gavekort»"
                 aria-describedby="faq-sok-status">
          <button class="faq-sok__tom" type="button" hidden data-faq-tom data-i18n-label="faq.sokClear" aria-label="Tøm søket">&times;</button>
        </div>
        <p class="caption" id="faq-sok-status" role="status" aria-live="polite" data-faq-status></p>
      </div>
    </div>
  </section>

  <section class="section section--flush-top" id="faq">
    <div class="wrap wrap--narrow">
{blokker}      <div class="faq-tomt" hidden data-faq-tomt>
        <p class="lede" data-i18n="faq.sokTom">Vi fant ingenting på det. Spør oss direkte, så svarer vi.</p>
        <div style="margin-top:var(--space-5);display:flex;gap:10px;flex-wrap:wrap">{kontakt}</div>
      </div>
    </div>
  </section>

  <section class="section section--flush-top">
    <div class="wrap wrap--narrow">
      <header class="sec-head">
        <div class="sec-head__rule"></div>
        <h2 class="display-3" data-i18n="faq.moreTitle">Spørsmål om én bestemt side</h2>
      </header>
      <p style="margin-top:var(--space-4);color:var(--text-muted)" data-i18n="faq.moreLede">Åpningstider, booking og veibeskrivelse står på hver restaurantside. Resten av spørsmålene ligger der de hører hjemme.</p>
      <div style="margin-top:var(--space-5);display:flex;gap:10px;flex-wrap:wrap">{andre}</div>
      <div class="divider" style="margin-top:var(--space-8)"><span data-i18n="faq.contactEyebrow">Spør oss direkte</span></div>
      <div style="margin-top:var(--space-5);display:flex;gap:10px;flex-wrap:wrap;align-items:center">
        <button class="btn btn--primary btn--md" type="button" data-book-open data-track="lp:sporsmal:book" data-i18n="act.book">Book bord</button>
        {kontakt}
      </div>
    </div>
  </section>
</main>

{chrome.footer()}
{modal.MODAL}
</body>
</html>
'''
    kv.write('sporsmal', html)
    print(kv.path('sporsmal'), 'ok')


if __name__ == '__main__':
    build(); G.write()
