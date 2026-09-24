"""Ofte stilte spørsmål – korte, sanne svar bygget fra content/venues.json og content/menus.js, på norsk og engelsk.
Vises som <details> på siden og speiles i FAQPage-markup (kun spørsmålene som faktisk vises).
Brukes av build_venue.py, build_landing.py, build.py (forside/take-away) og seo_head.py."""
import re
import kv, i18n_gen as G

V = kv.venues(); ORG = V['org']
PK = ORG['packages']

def burger_range(slug):
    try: m = kv.menus()
    except Exception: return None
    v = next((x for x in m['venues'] if x['slug'] == slug), None)
    prices = [int(p) for s in (v['menu']['sections'] if v else []) if s['id'] == 'burgers' for it in s['items'] for p in re.findall(r'\d+', it['price'])]
    return (min(prices), max(prices)) if prices else None

def fries_from():
    try: m = kv.menus()
    except Exception: return None
    prices = [int(p) for v in m['venues'] for s in v['menu']['sections'] if s['id'] == 'fries' for it in s['items'] for p in re.findall(r'\d+', it['price'])]
    return min(prices) if prices else None

def kids_items(slug):
    try: m = kv.menus()
    except Exception: return []
    v = next((x for x in m['venues'] if x['slug'] == slug), None)
    return [it for s in (v['menu']['sections'] if v else []) if s['id'] == 'kids' for it in s['items']]

def kitchen_text(v, lang='no'):
    return ', '.join(f'{kv.day_range(h["days"], lang)} {kv.hhmm(h["opens"])}–{kv.hhmm(h["closes"])}' for h in v['hours']['kitchen'])

def bar_text(v, lang='no'):
    w = 'til' if lang == 'no' else 'until'
    return ', '.join(f'{kv.day_range(h["days"], lang)} {w} {kv.hhmm(h["closes"])}' for h in v['hours']['bar'])

LUNCH_EN = {'majorstua': 'Tuesday–Friday from 11.00', 'solli': 'Tuesday–Friday from 11.30', 'tonsberg': 'Thursday–Sunday from 12.00'}
AREA_EN = {'majorstua': 'Majorstuen', 'solli': 'Solli plass', 'tonsberg': 'Kaldnes'}

def venue_faq(v):
    """Liste av (nøkkel, spørsmål-no, svar-no, spørsmål-en, svar-en)."""
    a = v['address']; slug = v['slug']; name = v['fullName']; thr = v['groupThreshold']
    rng = burger_range(slug); c = v['channels']
    deliv = [x for x in ('Wolt', 'Foodora') if c.get(x.lower())]
    ta_no = ('Ja. Du kan hente selv (forhåndsbestill på OrderX)' + (f', eller få levert hjem med {" og ".join(deliv)} (15–20 % dyrere enn å hente selv)' if deliv else '')
             + f'. <a href="/takeaway/">Bestill take-away</a> eller <a href="{c["pickup"]}" rel="noopener" target="_blank">forhåndsbestill henting {"i" if slug == "tonsberg" else "på"} {v["name"]}</a>.')
    ta_en = ('Yes. Pre-order for pick-up on OrderX' + (f', or get it delivered with {" and ".join(deliv)} (15–20% more than pick-up)' if deliv else '')
             + f'. <a href="/takeaway/">Order take-away</a> or <a href="{c["pickup"]}" rel="noopener" target="_blank">pick up at {v["name"]}</a>.')
    q = [
        (f'faq.{slug}.where', f'Hvor ligger {name}?',
         f'{name} ligger i {a["street"]}, {a["postalCode"]} {a["city"]} ({v["area"]}). <a href="{v["maps"]["google"]}" rel="noopener" target="_blank">Vis i Google Maps</a>.',
         f'Where is {name}?',
         f'{name} is at {a["street"]}, {a["postalCode"]} {a["city"]} ({AREA_EN[slug]}). <a href="{v["maps"]["google"]}" rel="noopener" target="_blank">Open in Google Maps</a>.'),
        (f'faq.{slug}.hours', f'Hva er åpningstidene på {name}?',
         f'Kjøkkenet: {kitchen_text(v)}. Baren holder åpent {bar_text(v)}. Lunsj serveres {v["lunch"]}.',
         f'What are the opening hours at {name}?',
         f'Kitchen: {kitchen_text(v, "en")}. The bar stays open {bar_text(v, "en")}. Lunch is served {LUNCH_EN[slug]}.'),
        (f'faq.{slug}.book', f'Kan jeg booke bord på {name}?',
         f'Ja. Bord for inntil {thr} personer booker du online og får bekreftelse med en gang. Grupper over {thr} sender en forespørsel og velger én matpakke for hele bordet (fra {PK["items"][0]["price"]} kr per person). Vi har også mange drop-in-bord. <a href="#booking">Book bord her</a>.',
         f'Can I book a table at {name}?',
         f'Yes. Tables for up to {thr} guests are booked online with instant confirmation. Groups larger than {thr} send a request and choose one food package for the whole table (from NOK {PK["items"][0]["price"]} per person). We also keep plenty of walk-in tables. <a href="#booking">Book a table here</a>.'),
        (f'faq.{slug}.takeaway', f'Har {name} take-away?', ta_no, f'Does {name} do take-away?', ta_en),
        (f'faq.{slug}.kids', 'Har dere barnemeny?', kids_answer(v, 'no'), 'Do you have a kids menu?', kids_answer(v, 'en')),
        (f'faq.{slug}.dropin', 'Må jeg booke bord, eller kan jeg bare komme?',
         f'Du er velkommen til å stikke innom – vi har mange drop-in-bord. Vil du være sikker på plass, særlig fredag og lørdag, booker du online på et par sekunder.',
         'Do I need to book, or can I just turn up?',
         'You are welcome to drop by – we keep plenty of walk-in tables. To be sure of a table, especially on Friday and Saturday, book online in a few seconds.'),
    ]
    if False and rng:
        q.append((f'faq.{slug}.price', 'Hva koster en burger hos Kverneriet?',
                  f'Burgerne på {name} koster fra {rng[0]} til {rng[1]} kr, med 150 g patty av kjøtt vi kverner selv. Fries kommer i tillegg (fra {fries_from() or 84} kr). <a href="{kv.url(slug + "-menu")}">Se hele menyen med priser</a>.',
                  'How much is a burger at Kverneriet?',
                  f'Burgers at {name} cost NOK {rng[0]}–{rng[1]}, with a 150 g patty of beef we grind ourselves. Fries are extra (from NOK {fries_from() or 84}). <a href="{kv.url(slug + "-menu")}">See the full menu with prices</a>.'))
    getting = {
        'majorstua': ('Hvordan kommer jeg til Kverneriet Majorstua?', 'Vi ligger i Kirkeveien, tre minutter å gå fra Majorstuen T-banestasjon og trikkeholdeplassen på Majorstuen. Kollektivt er enklest; gateparkering i området er begrenset.',
                      'How do I get to Kverneriet Majorstua?', 'We are on Kirkeveien, a three-minute walk from Majorstuen metro station and the Majorstuen tram stop. Public transport is easiest; street parking nearby is limited.'),
        'solli': ('Hvordan kommer jeg til Kverneriet Solli?', 'Vi ligger ved Solli plass, i enden av Henrik Ibsens gate, et par minutter fra trikk og buss på Solli plass og ti minutter å gå fra Nationaltheatret stasjon og Aker Brygge.',
                  'How do I get to Kverneriet Solli?', 'We are at Solli plass, at the end of Henrik Ibsens gate, a couple of minutes from the tram and bus stops at Solli plass and a ten-minute walk from Nationaltheatret station and Aker Brygge.'),
        'tonsberg': ('Hvordan kommer jeg til Kverneriet Tønsberg?', 'Vi ligger på Kaldnes brygge i Rambergveien 15, rett over kanalbrua fra Tønsberg brygge og sentrum, omtrent ti minutter å gå fra Tønsberg stasjon. Uteservering ved kanalen når været tillater.',
                     'How do I get to Kverneriet Tønsberg?', 'We are on Kaldnes brygge at Rambergveien 15, just across the canal bridge from Tønsberg brygge and the town centre, about a ten-minute walk from Tønsberg station. Outdoor seating by the canal when the weather allows.'),
    }[slug]
    q.append((f'faq.{slug}.getthere',) + getting)
    return q + extra(slug)

def kids_answer(v, lang):
    items = kids_items(v['slug']); pdf = v['menuPdf']['kids']
    if items:
        lo = min(int(re.search(r'\d+', i['price']).group()) for i in items); hi = max(int(re.search(r'\d+', i['price']).group()) for i in items)
        names = ', '.join(i['name'] for i in items)
        if lang == 'no': return f'Ja. Barnemenyen har {names} ({lo}–{hi} kr). <a href="{pdf}" rel="noopener" target="_blank">Se barnemenyen (PDF)</a>.'
        return f'Yes. The kids menu has {names} (NOK {lo}–{hi}). <a href="{pdf}" rel="noopener" target="_blank">See the kids menu (PDF)</a>.'
    if lang == 'no': return f'Ved selskapsbooking tilbyr vi barnemeny til {PK["kids"]} kr for gjester under 12. Ellers finner du barnevennlige retter som fries, chicken tenders og soft serve på menyen – spør oss, så hjelper vi.'
    return f'For group bookings we offer a kids menu at NOK {PK["kids"]} for guests under 12. Otherwise the menu has child-friendly options like fries, chicken tenders and soft serve – just ask.'

def general_faq():
    return _general_faq() + extra('index')

def _general_faq():
    vs = V['venues']
    where_no = ', '.join(f'{v["name"]} ({v["address"]["street"]}, {v["address"]["city"]})' for v in vs)
    links = ' · '.join(f'<a href="{kv.url(v["slug"])}">{v["fullName"]}</a>' for v in vs)
    return [
        ('faq.g.where', 'Hvor finner jeg Kverneriet?', f'Kverneriet har tre restauranter: {where_no}. {links}.',
         'Where can I find Kverneriet?', f'Kverneriet has three restaurants: {where_no}. {links}.'),
        ('faq.g.dropin', 'Må jeg booke bord?',
         'Nei, alle restaurantene har mange drop-in-bord. Vil du være sikker på plass, booker du online for inntil 8 personer (7 i Tønsberg) og får bekreftelse med en gang.',
         'Do I need to book a table?',
         'No, all three restaurants keep plenty of walk-in tables. To be sure of a table, book online for up to 8 guests (7 in Tønsberg) and get instant confirmation.'),
        ('faq.g.gluten', 'Hva gjør dere med allergier og glutenfritt?',
         'Alle retter er merket med allergener i menyen. Friesene er naturlig glutenfrie, og glutenfritt burgerbrød koster +15 kr. Si fra til oss når du bestiller, så hjelper vi deg med hva som passer.',
         'What about allergies and gluten-free?',
         'Every dish is labelled with allergens on the menu. The fries are naturally gluten-free, and a gluten-free bun is +NOK 15. Tell us when you order and we will help you find what works.'),
        ('faq.g.alcoholfree', 'Har dere alkoholfrie alternativer?',
         'Ja. Alle restaurantene har en ordentlig bar, og vi har en egen meny med alkoholfrie cocktails, øl og vin – i tillegg til milkshakes.',
         'Do you have alcohol-free options?',
         'Yes. All three restaurants have a proper bar, and we have a separate menu of alcohol-free cocktails, beer and wine – as well as milkshakes.'),
        ('faq.g.groups', 'Kan vi komme som gruppe eller ha selskap?',
         f'Ja. Grupper over 8 (7 i Tønsberg) booker som selskap og velger én matpakke for bordet, fra {PK["items"][0]["price"]} kr per person. Send en forespørsel med antall, dato og tidsrom, så svarer vi på e-post.',
         'Can we come as a group or book a party?',
         f'Yes. Groups larger than 8 (7 in Tønsberg) book as a party and choose one food package for the table, from NOK {PK["items"][0]["price"]} per person. Send a request with headcount, date and time window and we reply by e-mail.'),
        ('faq.g.takeaway', 'Har Kverneriet take-away?',
         'Ja, på alle tre restaurantene. Hent selv via OrderX, eller få levert med Wolt og Foodora i Oslo. Take-awayen fikk terningkast 6 i Dagbladet og ble kåret til Oslos beste av Finansavisen. <a href="/takeaway/">Bestill take-away</a>.',
         'Does Kverneriet do take-away?',
         'Yes, at all three restaurants. Pick up via OrderX, or get delivery with Wolt and Foodora in Oslo. Our take-away scored 6/6 in Dagbladet and was named Oslo’s best by Finansavisen. <a href="/takeaway/">Order take-away</a>.'),
    ]

def takeaway_faq():
    return _takeaway_faq() + extra('takeaway')

def _takeaway_faq():
    return [
        ('faq.ta.how', 'Hvordan bestiller jeg take-away fra Kverneriet?',
         'Velg restaurant og trykk «Hent selv» for å forhåndsbestille på OrderX, eller bestill hjemlevering med Wolt eller Foodora (Majorstua og Solli). I Tønsberg henter du selv.',
         'How do I order take-away from Kverneriet?',
         'Choose a restaurant and press “Pick up” to pre-order on OrderX, or order delivery with Wolt or Foodora (Majorstua and Solli). Tønsberg is pick-up only.'),
        ('faq.ta.cost', 'Hva koster hjemlevering?',
         'Hjemlevering kjøres av Wolt og Foodora og koster 15–20 % mer enn å hente selv. Henter du selv, betaler du menypris.',
         'What does delivery cost?',
         'Delivery is run by Wolt and Foodora and costs 15–20% more than pick-up. If you pick up yourself, you pay the menu price.'),
        ('faq.ta.warm', 'Holder burgeren seg varm og i form?',
         'Ja. Emballasjen er designet av oss: en boks i naturmaterialer der burgeren skyves ut, så den holder formen og varmen. Dagbladet skrev at burgeren «holder seg perfekt i formen».',
         'Does the burger stay warm and in shape?',
         'Yes. The packaging is our own design: a box in natural materials that the burger slides out of, so it keeps its shape and heat. Dagbladet wrote that the burger “keeps its shape perfectly”.'),
    ]

def landing_faq(slug):
    return _landing_faq(slug) + extra(slug)

def _landing_faq(slug):
    vs = V['venues']
    lunch_no = '; '.join(f'{v["name"]} {v["lunch"]}' for v in vs)
    lunch_en = '; '.join(f'{v["name"]} {LUNCH_EN[v["slug"]]}' for v in vs)
    pk_no = ', '.join(f'{p["name"]} {p["price"]} kr' for p in PK['items'])
    pk_en = ', '.join(f'{p["name"]} NOK {p["price"]}' for p in PK['items'])
    return {
        'lunsj': [
            ('faq.lunsj.when', 'Når serverer Kverneriet lunsj?', f'Kjøkkenet åpner {lunch_no}. Hele menyen serveres fra åpning, så du får den samme burgeren til lunsj som om kvelden.',
             'When does Kverneriet serve lunch?', f'The kitchen opens {lunch_en}. The full menu is served from opening, so you get the same burger at lunch as in the evening.'),
            ('faq.lunsj.book', 'Kan vi booke bord til lunsj?', 'Ja. Book online for inntil 8 personer (7 i Tønsberg), eller send forespørsel for større grupper fra kontoret, så står bordet klart når dere kommer.',
             'Can we book a table for lunch?', 'Yes. Book online for up to 8 people (7 in Tønsberg), or send a request for larger office groups, and the table is ready when you arrive.'),
            ('faq.lunsj.fast', 'Rekker jeg en burger på en times lunsjpause?', 'Ja. Burgerne stekes på bestilling og kommer raskt, og friesene er ferdig forberedt gjennom tre dager. Har du dårlig tid, kan du forhåndsbestille take-away og hente selv.',
             'Can I fit a burger into a one-hour lunch break?', 'Yes. Burgers are cooked to order and come out fast, and the fries are prepped over three days. Short on time? Pre-order take-away and pick it up.'),
        ],
        'julebord': [
            ('faq.jul.price', 'Hva koster julebord hos Kverneriet?', f'Grupper over 8 (7 i Tønsberg) velger én matpakke for hele bordet: {pk_no} per person. Barnemeny {PK["kids"]} kr for gjester under 12.',
             'How much is a Christmas party at Kverneriet?', f'Groups larger than 8 (7 in Tønsberg) choose one food package for the whole table: {pk_en} per person. Kids menu NOK {PK["kids"]} for guests under 12.'),
            ('faq.jul.where', 'Hvor kan vi ha julebord?', 'På alle tre restaurantene: Majorstua og Solli i Oslo, og Tønsberg. Baren holder åpent til 23 tirsdag–lørdag, så kvelden kan fortsette etter maten.',
             'Where can we hold the party?', 'At all three restaurants: Majorstua and Solli in Oslo, and Tønsberg. The bar stays open until 23.00 Tuesday–Saturday, so the evening can continue after dinner.'),
            ('faq.jul.how', 'Hvordan bestiller vi julebord?', 'Send en gruppeforespørsel med antall, dato og tidsrom. Vi svarer på e-post med forslag til bord og meny. Bordet er bekreftet når du har fått bekreftelsen fra oss.',
             'How do we book?', 'Send a group request with headcount, date and time window. We reply by e-mail with a table and menu proposal. The table is confirmed once you have our confirmation.'),
            ('faq.jul.allergy', 'Kan dere ta hensyn til allergier?', 'Ja. Alle retter er merket med allergener, og med matpakkene finner vi alternativer om vi får beskjed på forhånd.',
             'Can you accommodate allergies?', 'Yes. Every dish is labelled with allergens, and with the food packages we arrange alternatives if you let us know in advance.'),
        ],
        'selskap': [
            ('faq.sel.size', 'Hvor stor må gruppen være?', 'Grupper over 8 (7 i Tønsberg) booker som selskap og velger matpakke for bordet. Mindre grupper booker online som vanlig, eller kommer innom – vi har mange drop-in-bord.',
             'How big does the group need to be?', 'Groups larger than 8 (7 in Tønsberg) book as a party and choose a food package for the table. Smaller groups book online as usual, or just drop in – we keep plenty of walk-in tables.'),
            ('faq.sel.packages', 'Hva inneholder matpakkene?', ' '.join(f'{p["name"]} ({p["price"]} kr): {p["desc"]}' for p in PK['items']),
             'What is in the food packages?', 'Burger Package (NOK 429): a 150 g burger of your choice for everyone, the table shares thin- and thick-cut fries (original, truffle & parsley, parmesan & parsley) and a selection of dips. Dinner Package (NOK 579): truffled tater tots and hot wings to share, then a burger of your choice with fries and dips. Full Package (NOK 779): chili cheese balls, truffled tater tots, hot wings and romaine salad to share, a burger of your choice with fries and dips, and the chef’s dessert.'),
            ('faq.sel.kids', 'Kan barn være med?', f'Selvfølgelig. Barnemeny til {PK["kids"]} kr for gjester under 12 – hamburger, chicken tenders eller toast med fries.',
             'Can children come?', f'Of course. Kids menu at NOK {PK["kids"]} for guests under 12 – hamburger, chicken tenders or a toastie with fries.'),
            ('faq.sel.how', 'Hvordan booker vi?', 'Trykk «Send gruppeforespørsel», velg restaurant og fyll inn antall, dato og tidsrom. Vi svarer på e-post, og bordet er bekreftet når du har fått bekreftelsen.',
             'How do we book?', 'Press “Send group request”, choose a restaurant and fill in headcount, date and time window. We reply by e-mail, and the table is confirmed once you have our confirmation.'),
        ],
        'late-night': [
            ('faq.ln.late', 'Hvor sent kan jeg spise burger hos Kverneriet?', 'Kjøkkenet på Majorstua og Solli serverer hele menyen til kl. 22 tirsdag–lørdag (21 søndag og mandag). I Tønsberg til 22 tirsdag–lørdag. Baren holder åpent en time lenger.',
             'How late can I get a burger at Kverneriet?', 'The kitchens at Majorstua and Solli serve the full menu until 22.00 Tuesday–Saturday (21.00 Sunday and Monday). Tønsberg until 22.00 Tuesday–Saturday. The bar stays open an hour longer.'),
            ('faq.ln.book', 'Må jeg booke bord sent på kvelden?', 'Nei. Vi har mange drop-in-bord, så kom innom etter kino eller kampen. Vil du være sikker, booker du online på et par sekunder.',
             'Do I need to book late in the evening?', 'No. We keep plenty of walk-in tables, so come by after the cinema or the match. To be sure, book online in a few seconds.'),
            ('faq.ln.drinks', 'Hva kan jeg drikke sent?', 'Milkshake med 4 cl matchende sprit («Make it grown-up»), øl fra tappen, vin og cocktails fra baren. Se drikkemenyen på restaurantsiden.',
             'What can I drink late?', 'A milkshake with 4 cl of matching spirit (“Make it grown-up”), draught beer, wine and cocktails from the bar. See the drinks menu on the restaurant page.'),
        ],
    }.get(slug, [])

def extra(page):
    """Redaktørenes egne spørsmål (Sanity «faqItem») for en side."""
    out = []
    for i, f in enumerate(kv.site_copy().get('faqExtra') or []):
        if f.get('page') != page or not f.get('question') or not f.get('answer'): continue
        qn, an = f['question'].get('no', ''), f['answer'].get('no', '')
        out.append((f'faq.x.{page}.{i}', qn, kv.esc(an).replace('\n', '<br>'), f['question'].get('en') or qn, kv.esc(f['answer'].get('en') or an).replace('\n', '<br>')))
    return out

def strip(s): return re.sub(r'<[^>]+>', '', s).replace('&nbsp;', ' ')

def section(items, title='Ofte stilte spørsmål', eyebrow='Godt å vite', sec_id='faq', flush=True):
    """Registrerer oversettelsene og returnerer seksjonen. items = (key, q_no, a_no, q_en, a_en)."""
    if not items: return ''
    rows = ''
    for key, qn, an, qe, ae in items:
        G.add(key + '.q', qn, qe); G.add(key + '.a', an, ae)
        rows += (f'<details class="faq__item"><summary><h3 class="faq__q" data-i18n="{key}.q">{kv.esc(qn)}</h3></summary>'
                 f'<div class="faq__a"><p data-i18n-html="{key}.a">{an}</p></div></details>')
    G.add('faq.title', 'Ofte stilte spørsmål', 'Frequently asked questions'); G.add('faq.eyebrow', 'Godt å vite', 'Good to know')
    return (f'  <section class="section{" section--flush-top" if flush else ""}" id="{sec_id}">\n    <div class="wrap wrap--narrow">\n'
            f'      <header class="sec-head"><div class="sec-head__rule"></div><span class="kv-eyebrow" data-i18n="faq.eyebrow">{kv.esc(eyebrow)}</span><h2 class="display-2" data-i18n="faq.title">{kv.esc(title)}</h2></header>\n'
            f'      <div class="faq" style="margin-top:var(--space-5)">{rows}</div>\n    </div>\n  </section>\n')

def from_html(html):
    """Leser Q/A tilbake fra en side (så FAQPage alltid speiler det som vises)."""
    out = []
    for q, a in re.findall(r'<h3 class="faq__q"[^>]*>(.*?)</h3></summary><div class="faq__a"><p[^>]*>(.*?)</p></div>', html, re.S):
        out.append((strip(q).replace('&amp;', '&').replace('&quot;', '"'), strip(a).replace('&amp;', '&').replace('&quot;', '"')))
    return out

def ld(pairs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]}
