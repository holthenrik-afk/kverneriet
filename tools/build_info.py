#!/usr/bin/env python3
"""/kontakt/ og /personvern/.

Kontaktsiden samler adresse, telefon, e-post og åpningstider for hver restaurant, og
hvilket selskap som driver hvert sted. Alt hentes fra content/venues.json, så siden
følger med når noe endres der.

Personvernsiden beskriver det nettsiden faktisk gjør. Endrer du sporing, samtykke eller
bookingsystem i tools/chrome.py, site.js eller tools/modal.py, må teksten her endres likt.
Selskapene og organisasjonsnumrene er slått opp i Enhetsregisteret 03.11.2026.
Kjør: python3 tools/build.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv, chrome, modal, pages, i18n_gen as G
os.chdir(kv.ROOT)

V = kv.venues()
ORG = V['org']
e = kv.esc

# Bookingsystemet som åpnes i bookingvinduet (tools/modal.py). Kverneriet bytter til
# Easytable senest 16.11.2026. Bytt navn og land her samme dag, så personvernsiden stemmer.
BOOKING = ('Zenchef', 'Frankrike', 'France')

# Datoen teksten sist ble gjennomgått. Oppdateres når innholdet endres, ikke ved hvert bygg.
OPPDATERT = ('3. november 2026', '3 November 2026')


def orgnr(n):
    return f'{n[:3]} {n[3:6]} {n[6:]}'


def side(slug, crumb_key, crumb, body):
    meta = pages.PAGES[slug]
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
  <section class="section">
    <div class="wrap wrap--narrow">
      <nav class="crumbs" aria-label="Brødsmuler"><ol><li><a href="/">Kverneriet</a></li><li><span aria-current="page" data-i18n="{crumb_key}">{e(crumb)}</span></li></ol></nav>
{body}
</main>

{chrome.footer()}
{modal.MODAL}
</body>
</html>
'''


def build_kontakt():
    G.add('kontakt.eyebrow', 'Kontakt', 'Contact')
    G.add('kontakt.title', 'Kontakt oss', 'Contact us')
    G.add('kontakt.lede',
          'Ring oss eller send en e-post til restauranten det gjelder. Vil du booke bord, går det raskest online.',
          'Call us or e-mail the restaurant you want to reach. Booking a table is quickest online.')
    G.add('kontakt.phone', 'Telefon', 'Phone')
    G.add('kontakt.email', 'E-post', 'E-mail')
    G.add('kontakt.kitchen', 'Kjøkkenet', 'Kitchen')
    G.add('kontakt.directions', 'Veibeskrivelse', 'Directions')
    G.add('kontakt.hours', 'Alle åpningstider', 'All opening hours')

    kort = ''
    for v in V['venues']:
        s, a = v['slug'], v['address']
        kn = ', '.join(f'{kv.day_range(h["days"])} {kv.hhmm(h["opens"])}–{kv.hhmm(h["closes"])}' for h in v['hours']['kitchen'])
        ke = ', '.join(f'{kv.day_range(h["days"], "en")} {kv.hhmm(h["opens"])}–{kv.hhmm(h["closes"])}' for h in v['hours']['kitchen'])
        G.add(f'kontakt.{s}.kitchen', kn, ke)
        mail = (f'          <p style="margin-top:var(--space-2)"><span data-i18n="kontakt.email">E-post</span>: '
                f'<a href="mailto:{v["email"]}">{e(v["email"])}</a></p>\n') if v.get('email') else ''
        kort += (f'        <article class="card bar-kort">\n'
                 f'          <h2 class="display-4"><a href="{kv.url(s)}">{e(v["fullName"])}</a></h2>\n'
                 f'          <p style="margin-top:var(--space-3)">{e(a["street"])}, {a["postalCode"]} {e(a["city"])}'
                 f' · <a href="{v["maps"]["google"]}" target="_blank" rel="noopener" data-i18n="kontakt.directions">Veibeskrivelse</a></p>\n'
                 f'          <p style="margin-top:var(--space-2)"><span data-i18n="kontakt.phone">Telefon</span>: '
                 f'<a href="tel:{ORG["telephone"]}">{ORG["telephoneDisplay"]}</a></p>\n'
                 f'{mail}'
                 f'          <p class="caption" style="margin-top:var(--space-3)"><span data-i18n="kontakt.kitchen">Kjøkkenet</span>: '
                 f'<span data-i18n="kontakt.{s}.kitchen">{e(kn)}</span>. '
                 f'<a href="{kv.url(s)}#practical" data-i18n="kontakt.hours">Alle åpningstider</a></p>\n'
                 f'          <button class="btn btn--primary btn--sm" type="button" style="margin-top:var(--space-5)" data-book-open data-book-venue="{s}" '
                 f'data-track="lp:kontakt:book:{s}" data-i18n="act.book">Book bord</button>\n'
                 f'        </article>\n')

    pk = ORG['packages']
    over = {v['slug']: v['groupThreshold'] for v in V['venues']}
    G.add('kontakt.groupsTitle', 'Selskap og julebord', 'Parties and Christmas parties')
    pris = min(p['price'] for p in pk['items'])
    G.add('kontakt.groups',
          f'Er dere flere enn {over["majorstua"]} ({over["tonsberg"]} i Tønsberg), sender dere en forespørsel og velger én matpakke for hele bordet, fra {pris} kr per person.',
          f'Groups larger than {over["majorstua"]} ({over["tonsberg"]} in Tønsberg) send a request and choose one food package for the whole table, from NOK {pris} per person.')
    G.add('kontakt.groupsCta', 'Send forespørsel', 'Send a request')
    G.add('kontakt.moreTitle', 'Mer', 'More')
    G.add('kontakt.companiesTitle', 'Selskapene bak Kverneriet', 'The companies behind Kverneriet')
    G.add('kontakt.companies', 'Hver restaurant drives av sitt eget selskap.', 'Each restaurant is run by its own company.')
    G.add('kontakt.privacy', 'Les om personvern', 'Read about privacy')

    selskap = ''
    for v in V['venues']:
        c = ORG['companies'][v['slug']]
        no = f'{v["fullName"]}: {c["name"]}, org.nr. {orgnr(c["orgNumber"])}'
        G.add(f'kontakt.company.{v["slug"]}', no, no.replace('org.nr.', 'org. no.'))
        selskap += f'<li data-i18n="kontakt.company.{v["slug"]}">{e(no)}</li>'
    oa = ORG['address']
    orgline = f'{ORG["legalName"]}, org.nr. {orgnr(ORG["orgNumber"])}, {oa["street"]}, {oa["postalCode"]} {oa["city"]}'
    G.add('kontakt.orgline', f'Nettsiden drives av {orgline}.', f'The website is run by {orgline.replace("org.nr.", "org. no.")}.')

    body = f'''      <header class="sec-head">
        <div class="sec-head__rule"></div>
        <span class="kv-eyebrow" data-i18n="kontakt.eyebrow">Kontakt</span>
        <h1 class="display-1" data-i18n="kontakt.title">Kontakt oss</h1>
      </header>
      <p class="lede" style="margin-top:var(--space-5)" data-i18n="kontakt.lede">Ring eller send en e-post til restauranten det gjelder. Vil du booke bord, går det raskest online.</p>
    </div>
  </section>

  <section class="section section--flush-top">
    <div class="wrap">
      <div class="grid-3">
{kort}      </div>
    </div>
  </section>

  <section class="section section--flush-top">
    <div class="wrap wrap--narrow">
      <header class="sec-head">
        <div class="sec-head__rule"></div>
        <h2 class="display-3" data-i18n="kontakt.groupsTitle">Selskap og julebord</h2>
      </header>
      <p style="margin-top:var(--space-4)" data-i18n="kontakt.groups">{e(G._D['no']['kontakt.groups'])}</p>
      <div style="margin-top:var(--space-5);display:flex;gap:10px;flex-wrap:wrap">
        <a class="btn btn--outline btn--md" href="{kv.url('selskap')}" data-track="lp:kontakt:selskap" data-i18n="kontakt.groupsCta">Send forespørsel</a>
        <a class="btn btn--ghost btn--md" href="{kv.url('julebord')}" data-i18n="lp.xmas">Julebord</a>
      </div>

      <div class="divider" style="margin-top:var(--space-8)"><span data-i18n="kontakt.moreTitle">Annet</span></div>
      <div style="margin-top:var(--space-5);display:flex;gap:10px;flex-wrap:wrap">
        <a class="btn btn--ghost btn--md" href="{kv.url('sporsmal')}" data-i18n="nav.faq">Spørsmål og svar</a>
        <a class="btn btn--ghost btn--md" href="{kv.url('takeaway')}" data-i18n="act.takeaway">Take-away</a>
        <a class="btn btn--ghost btn--md" href="{ORG['giftcard']}" data-i18n="act.giftcards">Gavekort</a>
        <a class="btn btn--ghost btn--md" href="https://join.kverneriet.com/" data-i18n="act.work">Jobb hos oss</a>
      </div>

      <header class="sec-head" style="margin-top:var(--space-8)">
        <div class="sec-head__rule"></div>
        <h2 class="display-3" data-i18n="kontakt.companiesTitle">Selskapene bak Kverneriet</h2>
      </header>
      <div class="post__body" style="margin-top:var(--space-4)">
        <p data-i18n="kontakt.companies">Hver restaurant drives av sitt eget selskap.</p>
        <ul>{selskap}</ul>
        <p data-i18n="kontakt.orgline">Nettsiden drives av {e(orgline)}.</p>
        <p><a href="{kv.url('personvern')}" data-i18n="kontakt.privacy">Les om personvern</a></p>
      </div>
    </div>
  </section>'''
    kv.write('kontakt', side('kontakt', 'kontakt.title', 'Kontakt oss', body))
    print(kv.path('kontakt'), 'ok')


def build_personvern():
    """Hvert avsnitt er (type, nøkkel, norsk, engelsk). «html» og «ul_html» får data-i18n-html.

    Teksten beskriver det siden gjør i dag: Google-taggen lastes alltid (Consent Mode, standard
    «denied»), Google Ads og Meta får remarketing når gjesten trykker «Godta», Metricool-pikselen
    lastes uten samtykke, og bookingvinduet på restaurantsidene lastes når gjesten blar ned til det."""
    c = ORG['companies']
    pv = ORG['privacyEmail']
    pv_a = f'<a href="mailto:{pv}">{pv}</a>'
    oa = ORG['address']
    selskap_no = [f'{v["fullName"]}: {c[v["slug"]]["name"]} (org.nr. {orgnr(c[v["slug"]]["orgNumber"])})' for v in V['venues']]
    bk, bk_land_no, bk_land_en = BOOKING
    ansvarlig = f'{ORG["legalName"]} (org.nr. {orgnr(ORG["orgNumber"])}), {oa["street"]}, {oa["postalCode"]} {oa["city"]}'

    deler = [
        ('ansvar', 'Hvem som er ansvarlig', 'Who is responsible', [
            ('p', 'p1',
             f'{ansvarlig}, er ansvarlig for nettsiden kverneriet.no og informasjonskapslene på den. '
             'Hver restaurant drives av sitt eget selskap, som er ansvarlig for bookinger og henvendelser til restauranten:',
             f'{ansvarlig.replace("org.nr.", "org. no.")}, is responsible for the website kverneriet.no and the cookies on it. '
             'Each restaurant is run by its own company, which is responsible for bookings and enquiries to that restaurant:'),
            ('ul', 'selskap', selskap_no, [s.replace('org.nr.', 'org. no.') for s in selskap_no]),
            ('html', 'p2',
             f'Spørsmål om personvern sender du til {pv_a}.',
             f'Send questions about privacy to {pv_a}.'),
        ]),
        ('besok', 'Når du besøker nettsiden', 'When you visit the website', [
            ('p', 'p1',
             'Dette skjer uansett hva du svarer på spørsmålet om informasjonskapsler. Vi bruker ikke opplysningene til markedsføring.',
             'This happens whatever you answer to the cookie question. We do not use this information for marketing.'),
            ('ul_html', 'liste', [
                '<strong>Drift.</strong> Siden ligger hos GitHub Pages. Som ved alle nettsider får GitHub IP-adressen din og ser hvilken nettleser du bruker. Det trengs for å sende deg siden og stoppe misbruk.',
                '<strong>Skrifttyper og bilder.</strong> Skrifttypene hentes fra Google Fonts, og en del av bildene fra Sanity, som vi bruker til å redigere innholdet. Nettleseren din henter dem direkte, så IP-adressen din sendes også til Google og Sanity.',
                f'<strong>Bookingvinduet.</strong> På restaurantsidene lastes bookingvinduet fra {bk} når du blar ned til «Book bord». Da får {bk} IP-adressen din og ser hvilken nettleser du bruker, også om du ikke booker.',
                '<strong>Besøkstall.</strong> Metricool teller sidevisninger med et lite, usynlig bilde. Det setter ingen informasjonskapsler.',
                '<strong>Valgene dine.</strong> Nettleseren husker om du har svart på spørsmålet om informasjonskapsler, hvilket språk du har valgt og om du har satt bakgrunnsvideoen på pause. Dette lagres bare i nettleseren din (localStorage) og sendes ikke til oss.',
            ], [
                '<strong>Hosting.</strong> The site is hosted by GitHub Pages. As with any website, GitHub receives your IP address and sees which browser you use. This is needed to send you the page and to stop abuse.',
                '<strong>Fonts and images.</strong> The fonts come from Google Fonts, and some of the images from Sanity, which we use to edit the content. Your browser fetches them directly, so your IP address is also sent to Google and Sanity.',
                f'<strong>The booking window.</strong> On the restaurant pages, the booking window from {bk} loads when you scroll down to “Book a table”. {bk} then receives your IP address and sees which browser you use, even if you do not book.',
                '<strong>Visitor numbers.</strong> Metricool counts page views with a small, invisible image. It sets no cookies.',
                '<strong>Your choices.</strong> Your browser remembers whether you have answered the cookie question, which language you chose and whether you paused the background video. This is stored only in your browser (localStorage) and is not sent to us.',
            ]),
            ('html', 'p2',
             'Det rettslige grunnlaget er vår berettigede interesse i å drive en nettside som virker og er trygg, og i å vite hvor mange som besøker den (personvernforordningen artikkel 6 nr. 1 bokstav f). '
             f'Du kan når som helst protestere mot dette ved å sende en e-post til {pv_a}.',
             'The legal basis is our legitimate interest in running a website that works and is secure, and in knowing how many people visit it (GDPR Article 6(1)(f)). '
             f'You can object to this at any time by e-mailing {pv_a}.'),
        ]),
        ('kapsler', 'Informasjonskapsler fra Google og Meta', 'Cookies from Google and Meta', [
            ('p', 'p1',
             'Informasjonskapslene fra Google og Meta settes bare hvis du trykker på «Godta» i banneret. Trykker du på «Bare nødvendige» eller ikke svarer, settes de ikke. '
             'Du kan endre valget når som helst med knappen lenger ned, eller med «Informasjonskapsler» nederst på hver side.',
             'Cookies from Google and Meta are set only if you press “Accept” in the banner. If you press “Only necessary” or do not answer, they are not set. '
             'You can change your choice at any time with the button further down, or with “Cookies” at the bottom of every page.'),
            ('ul_html', 'liste', [
                '<strong>Google Analytics</strong> viser hvordan siden brukes, for eksempel hvilke sider folk leser og hvor mange som booker. Informasjonskapsler: _ga og _ga_QP2HX05YNB, som varer i 2 år. Dataene lagres i 14 måneder.',
                '<strong>Google Ads</strong> viser om annonsene våre fører til besøk og bookinger. Har du trykket på «Godta», kan vi også vise annonsene våre til deg senere. Informasjonskapsler: _gcl_au og _gcl_aw på kverneriet.no, som varer i 90 dager. Google setter i tillegg egne informasjonskapsler på sine domener.',
                '<strong>Meta-pikselen</strong> gjør det samme for annonser på Facebook og Instagram. Den lastes ikke i det hele tatt før du har trykket på «Godta». Informasjonskapsler: _fbp og _fbc på kverneriet.no, som varer i 90 dager. Meta setter i tillegg egne informasjonskapsler på sine domener.',
            ], [
                '<strong>Google Analytics</strong> shows how the site is used, for example which pages people read and how many book. Cookies: _ga and _ga_QP2HX05YNB, which last 2 years. The data is kept for 14 months.',
                '<strong>Google Ads</strong> shows whether our ads lead to visits and bookings. If you have pressed “Accept”, we may also show you our ads later. Cookies: _gcl_au and _gcl_aw on kverneriet.no, which last 90 days. Google also sets its own cookies on its own domains.',
                '<strong>The Meta pixel</strong> does the same for ads on Facebook and Instagram. It is not loaded at all until you have pressed “Accept”. Cookies: _fbp and _fbc on kverneriet.no, which last 90 days. Meta also sets its own cookies on its own domains.',
            ]),
            ('p', 'p2',
             'Det rettslige grunnlaget er samtykket ditt (artikkel 6 nr. 1 bokstav a).',
             'The legal basis is your consent (Article 6(1)(a)).'),
            ('p', 'p3',
             'Google-taggen lastes på alle sider, også før du har svart og når du har valgt «Bare nødvendige». Da setter den ingen informasjonskapsler, men Google får likevel et enkelt signal ved hvert sidebesøk, med IP-adressen din, hvilken nettleser du bruker og adressen til siden. '
             'Ut fra signalene anslår Google hvor mange som besøker siden og booker bord, uten å kjenne deg igjen. Kommer du fra en Google-annonse, kan en kode fra annonsen bli med i nettadressen når du går videre til andre sider hos oss, slik at klikket kan telles uten informasjonskapsler. '
             'Grunnlaget for dette er vår berettigede interesse i å vite om annonsene våre virker (artikkel 6 nr. 1 bokstav f), og du kan protestere mot det på samme måte som over.',
             'The Google tag loads on every page, also before you have answered and when you have chosen “Only necessary”. It then sets no cookies, but Google still receives a simple signal for each page visit, with your IP address, which browser you use and the address of the page. '
             'From these signals Google estimates how many people visit the site and book a table, without recognising you. If you arrive from a Google ad, a code from the ad may be carried in the web address as you move to other pages on our site, so the click can be counted without cookies. '
             'The legal basis for this is our legitimate interest in knowing whether our ads work (Article 6(1)(f)), and you can object to it in the same way as above.'),
            ('knapp', 'endre', 'Endre valget', 'Change your choice'),
        ]),
        ('booking', 'Når du booker bord', 'When you book a table', [
            ('p', 'p1',
             f'Bookingen skjer i {bk}, som åpnes i et vindu på siden vår. Restauranten får navnet ditt, telefonnummeret, e-postadressen, antall gjester, tidspunktet og det du skriver i kommentarfeltet. '
             'Vi bruker opplysningene til å holde av bordet og ta kontakt hvis noe endrer seg. Grunnlaget er at vi trenger dem for å gi deg bordet du har bestilt (artikkel 6 nr. 1 bokstav b).',
             f'Bookings are made in {bk}, which opens in a window on our site. The restaurant receives your name, phone number, e-mail address, number of guests, the time and what you write in the comment field. '
             'We use this information to hold your table and to contact you if something changes. The legal basis is that we need it to give you the table you booked (Article 6(1)(b)).'),
            ('p', 'p2',
             'Etter besøket kan du få en e-post eller SMS der vi spør hvordan det var. Det kan du velge bort når du booker, og grunnlaget er vår berettigede interesse i å vite hva gjestene synes. '
             'Krysser du av for nyheter og tilbud i bookingen, bruker vi kontaktinformasjonen din til det også, og da er grunnlaget samtykket ditt.',
             'After your visit you may get an e-mail or text message asking how it was. You can opt out of this when you book, and the legal basis is our legitimate interest in knowing what guests think. '
             'If you tick the box for news and offers when you book, we also use your contact details for that, and then the legal basis is your consent.'),
            ('p', 'p3',
             'Allergier og andre matbehov er helseopplysninger. Skriver du dem i bookingen eller i en forespørsel, bruker vi dem bare til å lage maten slik at den er trygg for deg. '
             'Grunnlaget er ditt uttrykkelige samtykke (artikkel 9 nr. 2 bokstav a). Du trenger ikke skrive dem, du kan også si fra når du kommer.',
             'Allergies and other dietary needs are health data. If you write them in your booking or in a request, we use them only to make sure your food is safe for you. '
             'The legal basis is your explicit consent (Article 9(2)(a)). You do not have to write them down, you can also tell us when you arrive.'),
            ('p', 'p4',
             f'{bk} behandler opplysningene på vegne av restauranten og har egne retningslinjer for informasjonskapsler i bookingvinduet.',
             f'{bk} processes the information on behalf of the restaurant and has its own cookie policy for the booking window.'),
        ]),
        ('nyhetsbrev', 'Nyhetsbrevet', 'The newsletter', [
            ('p', 'p1',
             'Melder du deg på nyhetsbrevet, lagrer vi e-postadressen din i Mailchimp, og navnet ditt hvis du oppgir det. Mailchimp registrerer om du åpner brevet og hva du klikker på, så vi ser hva gjestene er interessert i. '
             'Krysser du av for nyheter i skjemaet for selskap og julebord, kan vi sende deg nyheter og tilbud på e-post og SMS. '
             'Grunnlaget er samtykket ditt. Du melder deg av med lenken nederst i hvert brev, og da får du ikke flere brev fra oss.',
             'If you sign up for the newsletter, we store your e-mail address in Mailchimp, and your name if you give it. Mailchimp records whether you open the newsletter and what you click, so we can see what guests are interested in. '
             'If you tick the box for news in the form for parties and Christmas parties, we may send you news and offers by e-mail and text message. '
             'The legal basis is your consent. You can unsubscribe with the link at the bottom of every newsletter, and you will not receive any more from us.'),
        ]),
        ('kontakt', 'Når du kontakter oss', 'When you contact us', [
            ('p', 'p1',
             'Sender du en e-post, ringer eller ber om tilbud på selskap eller julebord, bruker vi opplysningene til å svare deg og planlegge besøket. '
             'Når du ber om tilbud, er grunnlaget at vi trenger opplysningene for å gi deg tilbudet og avtale besøket (artikkel 6 nr. 1 bokstav b). Ved andre spørsmål er grunnlaget vår berettigede interesse i å svare deg (artikkel 6 nr. 1 bokstav f).',
             'If you e-mail us, call us or ask for a quote for a party or Christmas party, we use the information to reply to you and plan your visit. '
             'When you ask for a quote, the legal basis is that we need the information to give you the quote and arrange the visit (Article 6(1)(b)). For other questions, the legal basis is our legitimate interest in replying to you (Article 6(1)(f)).'),
        ]),
        ('andre', 'Take-away, gavekort og jobb', 'Take-away, gift cards and jobs', [
            ('p', 'p1',
             'Bestiller du take-away hos Order X, Wolt eller Foodora, kjøper gavekort i gavekortbutikken eller søker jobb via jobbsidene våre, gjelder personvernerklæringen til den tjenesten.',
             'If you order take-away from Order X, Wolt or Foodora, buy a gift card in the gift card shop or apply for a job through our job pages, the privacy policy of that service applies.'),
        ]),
        ('deling', 'Hvem som får opplysningene', 'Who receives your information', [
            ('p', 'p1',
             'Vi selger ikke opplysninger om deg. Disse selskapene får opplysninger:',
             'We do not sell information about you. These companies receive information:'),
            ('ul', 'liste', [
                'Google (Analytics, Ads, Fonts og e-posten vår), Meta, GitHub (nettsiden), Mailchimp (nyhetsbrevet) og Sanity (bildene) i USA',
                f'Metricool i Spania og {bk} i {bk_land_no}',
            ], [
                'Google (Analytics, Ads, Fonts and our e-mail), Meta, GitHub (the website), Mailchimp (the newsletter) and Sanity (the images) in the USA',
                f'Metricool in Spain and {bk} in {bk_land_en}',
            ]),
            ('html', 'p2',
             'De fleste behandler opplysningene bare på våre vegne. Google (Ads og Fonts) og Meta bruker dem også til egne formål og er selv ansvarlige for det. '
             'For Meta-pikselen er vi og Meta felles ansvarlige for at opplysningene samles inn og sendes til Meta. Resten svarer Meta for, se '
             '<a href="https://www.facebook.com/legal/controller_addendum" target="_blank" rel="noopener">Metas avtale om felles ansvar</a>.',
             'Most of them process the information only on our behalf. Google (Ads and Fonts) and Meta also use it for their own purposes and are responsible for that themselves. '
             'For the Meta pixel, we and Meta are jointly responsible for collecting the information and sending it to Meta. Meta is responsible for the rest, see '
             '<a href="https://www.facebook.com/legal/controller_addendum" target="_blank" rel="noopener">Meta’s joint controller addendum</a>.'),
            ('p', 'p3',
             'Når opplysninger går til USA, skjer det etter rammeverket for personvern mellom EU og USA (EU–US Data Privacy Framework) eller EU-kommisjonens standardkontrakter. Du kan be oss om en kopi av standardkontraktene.',
             'When information goes to the USA, this happens under the EU–US Data Privacy Framework or the European Commission’s standard contractual clauses. You can ask us for a copy of the standard contractual clauses.'),
        ]),
        ('rettigheter', 'Rettighetene dine', 'Your rights', [
            ('html', 'p1',
             'Du kan be om å få se opplysningene vi har om deg, og om å få dem rettet, slettet eller utlevert. Du kan også be oss begrense bruken av dem, eller protestere mot at vi bruker dem. '
             f'Har du gitt samtykke, kan du trekke det tilbake når som helst. Send en e-post til {pv_a} eller til restauranten det gjelder, så svarer vi innen én måned.',
             'You can ask to see the information we hold about you, and to have it corrected, deleted or handed over to you. You can also ask us to restrict how we use it, or object to our use of it. '
             f'If you have given consent, you can withdraw it at any time. E-mail {pv_a} or the restaurant in question, and we will reply within one month.'),
            ('html', 'p2',
             'Mener du at vi behandler opplysninger om deg i strid med reglene, kan du klage til <a href="https://www.datatilsynet.no/" target="_blank" rel="noopener">Datatilsynet</a>.',
             'If you believe we process information about you in breach of the rules, you can complain to <a href="https://www.datatilsynet.no/" target="_blank" rel="noopener">Datatilsynet</a>, the Norwegian Data Protection Authority.'),
        ]),
    ]

    G.add('pv.eyebrow', 'Personvern', 'Privacy')
    G.add('pv.title', 'Personvern og informasjonskapsler', 'Privacy and cookies')
    G.add('pv.lede',
          'Her forklarer vi hvilke opplysninger vi samler inn når du bruker kverneriet.no, booker bord eller får nyhetsbrevet vårt, hva vi bruker dem til og hvilke rettigheter du har.',
          'This page explains what information we collect when you use kverneriet.no, book a table or receive our newsletter, what we use it for and what rights you have.')
    G.add('pv.updated', f'Sist oppdatert {OPPDATERT[0]}.', f'Last updated {OPPDATERT[1]}.')

    tekst = ''
    for dk, hn, he, blokker in deler:
        G.add(f'pv.{dk}.t', hn, he)
        tekst += f'        <h2 class="display-3" data-i18n="pv.{dk}.t">{e(hn)}</h2>\n'
        for kind, k, no, en in blokker:
            key = f'pv.{dk}.{k}'
            if kind == 'p':
                G.add(key, no, en); tekst += f'        <p data-i18n="{key}">{e(no)}</p>\n'
            elif kind == 'html':
                G.add(key, no, en); tekst += f'        <p data-i18n-html="{key}">{no}</p>\n'
            elif kind in ('ul', 'ul_html'):
                tekst += '        <ul>\n'
                for i, (pn, pe) in enumerate(zip(no, en)):
                    G.add(f'{key}{i + 1}', pn, pe)
                    attr, inner = ('data-i18n-html', pn) if kind == 'ul_html' else ('data-i18n', e(pn))
                    tekst += f'          <li {attr}="{key}{i + 1}">{inner}</li>\n'
                tekst += '        </ul>\n'
            elif kind == 'knapp':
                G.add(key, no, en)
                tekst += (f'        <p><button type="button" class="btn btn--outline btn--md" data-consent-open '
                          f'data-i18n="{key}">{e(no)}</button></p>\n')

    body = f'''      <header class="sec-head">
        <div class="sec-head__rule"></div>
        <span class="kv-eyebrow" data-i18n="pv.eyebrow">Personvern</span>
        <h1 class="display-1" data-i18n="pv.title">Personvern og informasjonskapsler</h1>
      </header>
      <p class="lede" style="margin-top:var(--space-5)" data-i18n="pv.lede">{e(G._D['no']['pv.lede'])}</p>
      <p class="caption" style="margin-top:var(--space-3)" data-i18n="pv.updated">Sist oppdatert {OPPDATERT[0]}.</p>
      <div class="post__body">
{tekst}      </div>
    </div>
  </section>'''
    kv.write('personvern', side('personvern', 'pv.eyebrow', 'Personvern', body))
    print(kv.path('personvern'), 'ok')


def build():
    build_kontakt(); build_personvern()


if __name__ == '__main__':
    build(); G.write()
