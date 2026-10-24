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
    if rng:
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
            ('faq.sel.kids', 'Kan barn være med?', f'Selvfølgelig. Barnemeny til {PK["kids"]} kr for gjester under 12 – hamburger med fries, chicken tenders med fries eller ostetoast.',
             'Can children come?', f'Of course. Kids menu at NOK {PK["kids"]} for guests under 12 – a hamburger with fries, chicken tenders with fries, or a ham and cheese toastie.'),
            ('faq.sel.how', 'Hvordan booker vi?', 'Trykk «Send gruppeforespørsel», velg restaurant og fyll inn antall, dato og tidsrom. Vi svarer på e-post, og bordet er bekreftet når du har fått bekreftelsen.',
             'How do we book?', 'Press “Send group request”, choose a restaurant and fill in headcount, date and time window. We reply by e-mail, and the table is confirmed once you have our confirmation.'),
        ],
        'middag': [
            ('faq.mid.book', 'Må jeg booke bord til middag?', 'Nei, vi har mange drop-in-bord. Vil du være sikker på plass, særlig fredag og lørdag, booker du online for inntil 8 personer (7 i Tønsberg) og får bekreftelse med en gang.',
             'Do I need to book for dinner?', 'No, we keep plenty of walk-in tables. To be sure of a table, especially on Friday and Saturday, book online for up to 8 guests (7 in Tønsberg) with instant confirmation.'),
            ('faq.mid.late', 'Hvor lenge er kjøkkenet åpent?', f'Kjøkkenet serverer til kl. 22 tirsdag–lørdag og til 21 søndag og mandag. Baren holder åpent til 23 tirsdag–lørdag, så dere kan bli sittende etter maten.',
             'How late is the kitchen open?', 'The kitchen serves until 22.00 Tuesday–Saturday and until 21.00 Sunday and Monday. The bar stays open until 23.00 Tuesday–Saturday, so you can stay on after dinner.'),
            ('faq.mid.groups', 'Kan vi komme mange?', f'Ja. Grupper over 8 (7 i Tønsberg) booker som selskap og velger én matpakke for bordet, fra {PK["items"][0]["price"]} kr per person. <a href="/selskap/">Les mer om selskap</a>.',
             'Can we come as a big group?', f'Yes. Groups larger than 8 (7 in Tønsberg) book as a party and choose one food package for the table, from NOK {PK["items"][0]["price"]} per person. <a href="/selskap/">More about parties</a>.'),
        ],
        'cocktails': [
            ('faq.cock.food', 'Må jeg spise for å sitte i baren?', 'Nei. Du er like velkommen til å slå deg ned med en cocktail, et glass vin eller en øl som til en full middag. Alle tre restaurantene har bar.',
             'Do I have to eat to sit at the bar?', 'No. You are just as welcome for a cocktail, a glass of wine or a beer as for a full dinner. All three restaurants have a bar.'),
            ('faq.cock.free', 'Har dere alkoholfrie cocktails?', 'Ja, vi har et stort alkoholfritt utvalg med cocktails, øl og vin – laget for å være et ordentlig alternativ, ikke et kompromiss.',
             'Do you have alcohol-free cocktails?', 'Yes, we have a large alcohol-free selection of cocktails, beer and wine – made to be a real alternative, not a compromise.'),
            ('faq.cock.late', 'Hvor lenge er baren åpen?', 'Baren holder åpent til kl. 23 tirsdag–lørdag og til 22 søndag og mandag, på alle tre restaurantene.',
             'How late is the bar open?', 'The bar is open until 23.00 Tuesday–Saturday and until 22.00 Sunday and Monday, at all three restaurants.'),
        ],
        'fries': [
            ('faq.fries.why', 'Hvorfor tar friesene tre dager?', 'Fordi de går gjennom tre runder: først koking, så kjøling, og til slutt frityr når du bestiller. De to første rundene gjør innmaten myk og potetaktig, den siste gir skallet som knaser.',
             'Why do the fries take three days?', 'Because they go through three rounds: first boiling, then chilling, and finally the fryer when you order. The first two make the inside soft and potatoey, the last gives the crisp shell.'),
            ('faq.fries.gluten', 'Er friesene glutenfrie?', 'Ja, de er naturlig glutenfrie. Si fra til kelneren om du har cøliaki, så tar kjøkkenet forholdsregler i frityren.',
             'Are the fries gluten free?', 'Yes, they are naturally gluten free. Tell your server if you are coeliac so the kitchen can take precautions in the fryer.'),
            ('faq.fries.topping', 'Hva kan jeg ha på friesene?', 'Trøffel og persille, parmesan og persille, eller Fully Loaded med ostesaus, pico de gallo, syltet løk, jalapeño og barbacoa. Fully Loaded står på menyen på Majorstua og i Tønsberg.',
             'What can I put on the fries?', 'Truffle and parsley, parmesan and parsley, or Fully Loaded with cheese sauce, pico de gallo, pickled onions, jalapeños and barbacoa. Fully Loaded is on the menu at Majorstua and in Tønsberg.'),
            ('faq.fries.takeaway', 'Blir friesene sprø på veien hjem?', 'Take-away-esken har lufting, så dampen slipper ut i stedet for å bli sittende. Henter du selv, får du dem rett fra frityren.',
             'Do the fries stay crisp on the way home?', 'The take-away box is vented, so the steam escapes instead of being trapped. If you pick up yourself, they come straight from the fryer.'),
        ],
        'soft-serve': [
            ('faq.ss.jersey', 'Hva er Jersey-melk?', 'Melk fra jerseykyr. Den har mer fett og protein enn vanlig helmelk, og det er derfor softisen vår blir tyngre og mer kremet. Vi får melken fra Jerseymeieriet.',
             'What is Jersey milk?', 'Milk from Jersey cattle. It has more fat and protein than ordinary whole milk, which is why our soft serve is richer and creamier. We get it from Jerseymeieriet.'),
            ('faq.ss.topping', 'Er toppingene like på alle restaurantene?', 'Nei. Oreo-smuler får du overalt, men resten er forskjellig: Blueberry Cheesecake og Chocolate Deluxe på Majorstua, Lemon and Crumble og Choco-nuts på Solli, Pistachio Twist og Choco-nuts i Tønsberg.',
             'Are the toppings the same at every restaurant?', 'No. Oreo crumbs are everywhere, but the rest differ: Blueberry Cheesecake and Chocolate Deluxe at Majorstua, Lemon and Crumble and Choco-nuts at Solli, Pistachio Twist and Choco-nuts in Tønsberg.'),
            ('faq.ss.shake', 'Er milkshaken laget på den samme softisen?', 'Ja, på den samme Jersey-melken. Du velger mellom Oreo, sjokolade og jordbær.',
             'Is the milkshake made from the same dairy?', 'Yes, the same Jersey dairy. Choose between Oreo, chocolate and strawberry.'),
            ('faq.ss.only', 'Kan jeg komme bare for dessert?', 'Ja. Softis og milkshake står på menyen hele åpningstiden, og du trenger ikke bestille mat først.',
             'Can I come just for dessert?', 'Yes. Soft serve and milkshakes are on the menu all opening hours, and you do not have to order food first.'),
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

def _ord(*deler):
    return ' '.join(' '.join(d.replace('&nbsp;', ' ').split()) for d in deler).lower()

def sokeindeks(key, qn, an, qe, ae):
    """To lag, fordi ett lag gir falske treff.

    Sterkt lag er spørsmålet selv og synonymene i SOKEORD. Her holder det at et ord
    begynner på det gjesten har skrevet, så «uteser» finner «uteservering».
    Svakt lag er svarteksten. Her kreves hele ord, ellers ville «hund» truffet
    «hundrevis» i svaret om utdrikningslag."""
    return _ord(qn, qe, SOKEORD.get(key, '')), _ord(strip(an), strip(ae))

def rows(items, sok=False):
    """Selve <details>-radene. Formen må stå urørt: from_html() leser den tilbake for FAQPage-markup."""
    out = ''
    for key, qn, an, qe, ae in items:
        G.add(key + '.q', qn, qe); G.add(key + '.a', an, ae)
        attr = ''
        if sok:
            sterk, svak = sokeindeks(key, qn, an, qe, ae)
            attr = f' data-sok="{kv.esc(sterk)}" data-sok-tekst="{kv.esc(svak)}"'
        out += (f'<details class="faq__item"{attr}><summary><h3 class="faq__q" data-i18n="{key}.q">{kv.esc(qn)}</h3></summary>'
                f'<div class="faq__a"><p data-i18n-html="{key}.a">{an}</p></div></details>')
    return out

def section(items, title='Ofte stilte spørsmål', eyebrow='Godt å vite', sec_id='faq', flush=True):
    """Registrerer oversettelsene og returnerer seksjonen. items = (key, q_no, a_no, q_en, a_en)."""
    if not items: return ''
    rows_html = rows(items)
    G.add('faq.title', 'Ofte stilte spørsmål', 'Frequently asked questions'); G.add('faq.eyebrow', 'Godt å vite', 'Good to know')
    G.add('faq.allLink', 'Se alle spørsmål og svar', 'See all questions and answers')
    # Siden har sine egne spørsmål, men resten ligger samlet på /sporsmal/.
    alle = ('' if sec_id != 'faq' else
            '\n      <p class="caption" style="margin-top:var(--space-5)">'
            '<a href="/sporsmal/" data-i18n="faq.allLink">Se alle spørsmål og svar</a></p>')
    return (f'  <section class="section{" section--flush-top" if flush else ""}" id="{sec_id}">\n    <div class="wrap wrap--narrow">\n'
            f'      <header class="sec-head"><div class="sec-head__rule"></div><span class="kv-eyebrow" data-i18n="faq.eyebrow">{kv.esc(eyebrow)}</span><h2 class="display-2" data-i18n="faq.title">{kv.esc(title)}</h2></header>\n'
            f'      <div class="faq" style="margin-top:var(--space-5)">{rows_html}</div>{alle}\n    </div>\n  </section>\n')

def from_html(html):
    """Leser Q/A tilbake fra en side (så FAQPage alltid speiler det som vises)."""
    out = []
    for q, a in re.findall(r'<h3 class="faq__q"[^>]*>(.*?)</h3></summary><div class="faq__a"><p[^>]*>(.*?)</p></div>', html, re.S):
        out.append((strip(q).replace('&amp;', '&').replace('&quot;', '"'), strip(a).replace('&amp;', '&').replace('&quot;', '"')))
    return out

def ld(pairs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]}


# ---------------------------------------------------------------------------
# /sporsmal/ – den samlede spørsmålssiden.
#
# Svarene her kommer fra lista Viktor sendte (content/faq-viktor.txt), skrevet om
# til Henriks stemme og faktasjekket mot content/venues.json og content/menus.js.
# Åpningstider, adresser, gruppeterskler og priser regnes ut, så de aldri blir
# stående igjen når noe endres i Sanity.
#
# Alkoholloven §9-2 forbyr reklame for alkohol, og Tønsberg har fått advarsel før.
# Viktors svar om «vårt store utvalg av vin, øl og håndlagde cocktails» er derfor
# skrevet om til å handle om baren som sted og om det alkoholfrie utvalget.
# ---------------------------------------------------------------------------

def _steder_no():
    return ', '.join(f'{v["name"]} i {v["address"]["street"]} ({v["area"]})' for v in V['venues'])

def _steder_en():
    return ', '.join(f'{v["name"]} at {v["address"]["street"]} ({AREA_EN[v["slug"]]})' for v in V['venues'])

def _tider_no():
    return ' '.join(f'{v["name"]}: {kitchen_text(v)}.' for v in V['venues'])

def _tider_en():
    return ' '.join(f'{v["name"]}: {kitchen_text(v, "en")}.' for v in V['venues'])

def _bar_no():
    """Barens åpningstid. Er den lik alle tre steder, skrives den én gang."""
    t = {bar_text(v) for v in V['venues']}
    return t.pop() if len(t) == 1 else ' '.join(f'{v["name"]}: {bar_text(v)}.' for v in V['venues'])

def _bar_en():
    t = {bar_text(v, 'en') for v in V['venues']}
    return t.pop() if len(t) == 1 else ' '.join(f'{v["name"]}: {bar_text(v, "en")}.' for v in V['venues'])

def _levering():
    """Byene som faktisk har Wolt eller Foodora i content/venues.json."""
    return [v['name'] for v in V['venues'] if v['channels'].get('wolt') or v['channels'].get('foodora')]



# Ekstra søkeord per spørsmål på /sporsmal/. Nøkkelen er den samme som i GRUPPER().
# Dette er ord gjesten skriver, men som ikke nødvendigvis står i spørsmålet eller svaret:
# synonymer, hverdagsord og de engelske variantene. Uten disse finner et søk på «hund»
# ingenting før gjesten tilfeldigvis skriver «hunder».
SOKEORD = {
    'faq.s.walkin':     'drop-in dropin reservasjon reservere bestille bord plass kø walk-in walk in table reservation',
    'faq.s.size':       'selskap bursdag jubileum firmafest langbord mange stort bord 30 40 gruppe group party birthday',
    'faq.s.bachelor':   'utdrikningslag polterabend bachelor bachelorette hen stag party jentekveld gutterkveld',
    'faq.s.business':   'møte møterom business jobb konferanse firma lukket avdeling meeting conference work',
    'faq.s.gluten':     'glutenfri gluten cøliaki celiaki melkefri laktose laktosefri eggefri brød bolle bun coeliac dairy free lactose egg',
    'faq.s.allergy':    'allergi allergener intoleranse nøtter nøtteallergi skalldyr laktose soya allergy allergen intolerance nuts shellfish',
    'faq.s.veg':        'vegetar vegetarianer vegansk vegan plantebasert kjøttfri veggie meat free plant based',
    'faq.s.kids':       'barn unger barnemeny barnestol høystol familie baby kids children child high chair family',
    'faq.s.pris':       'pris priser koster kost hva koster billig dyrt kroner penger price cost how much cheap',
    'faq.s.craft':      'håndverk kvernet ferskt brød bakt råvarer kvalitet hjemmelaget craft fresh quality homemade',
    'faq.s.dogs':       'hund hunder bikkje dyr kjæledyr hundevennlig dog dogs pet pets dog friendly',
    'faq.s.outside':    'uteservering ute terrasse utendørs sol solen brygge balkong outdoor outdoors terrace patio sun',
    'faq.s.wheelchair': 'rullestol tilgjengelig tilgjengelighet universell utforming handikap bevegelseshemmet trinnfri wheelchair accessible access step free',
    'faq.s.pram':       'barnevogn vogn trille sportsvogn vognplass baby spedbarn plass pram stroller buggy pushchair',
    'faq.s.drink':      'bar drink drikke glass alkoholfri alkoholfritt uten mat bare drikke baren drinks alcohol free',
    'faq.s.hours':      'åpent åpningstid åpningstider stenger stenge åpner klokka klokken når søndag mandag helg hours open opening closing sunday monday',
    'faq.s.where':      'hvor adresse ligger finne veibeskrivelse kart retning t-bane buss trikk kollektivt address directions map metro bus',
    'faq.s.ta':         'takeaway take-away take away hente henting levering hjemlevering wolt foodora orderx bestille delivery pick up',
    'faq.s.tabox':      'emballasje eske pose sprø sprøtt varm kald hjem transport veien packaging box crisp warm',
    'faq.s.gift':       'gavekort gave presang julegave bursdagsgave verdikort gift card voucher present',
}

def GRUPPER():
    """[(nøkkel, tittel-no, tittel-en, [(nøkkel, q-no, a-no, q-en, a-en), ...]), ...]"""
    thr = V['venues'][0]['groupThreshold']
    tbg = next(v['groupThreshold'] for v in V['venues'] if v['slug'] == 'tonsberg')
    fra = PK['items'][0]['price']
    lev = _levering()
    return [
        ('book', 'Booking og grupper', 'Booking and groups', [
            ('faq.s.walkin', 'Må jeg booke bord?',
             'Nei. Vi holder av mange bord til drop-in på alle tre restaurantene, så du kan godt bare komme innom. Vil du være sikker på plass, særlig fredag og lørdag, booker du online og får bekreftelse med en gang.',
             'Do I need to book a table?',
             'No. We keep plenty of walk-in tables at all three restaurants, so you are welcome to just turn up. To be sure of a table, especially on Friday and Saturday, book online and get instant confirmation.'),
            ('faq.s.size', 'Hvor store grupper tar dere imot?',
             f'Opptil 30–40 personer, avhengig av dag og tidspunkt. Grupper over {thr} ({tbg} i Tønsberg) booker som selskap og velger én matpakke for hele bordet, fra {fra} kr per person. <a href="/selskap/">Send en forespørsel</a>, så svarer vi på e-post.',
             'How big a group can you take?',
             f'Up to 30–40 people, depending on the day and time. Groups larger than {thr} ({tbg} in Tønsberg) book as a party and choose one food package for the whole table, from NOK {fra} per person. <a href="/selskap/">Send a request</a> and we reply by e-mail.'),
            ('faq.s.bachelor', 'Passer dere for utdrikningslag?',
             'Ja. Vi har tatt imot hundrevis av dem gjennom årene og liker å være med på feiringen. Send en forespørsel med antall og dato, så finner vi en løsning som passer gjengen.',
             'Do you take bachelor and bachelorette parties?',
             'Yes. We have hosted hundreds of them over the years and enjoy being part of the celebration. Send a request with headcount and date and we will find something that suits the group.'),
            ('faq.s.business', 'Kan vi ha møte hos dere?',
             'Ja. Vi har flere områder og lukkede avdelinger som passer til både korte og lengre møter. Enten dere vil ha kaffe og noe enkelt, småretter underveis eller en full lunsj, tilpasser vi opplegget.',
             'Can we hold a meeting at your place?',
             'Yes. We have several areas and separate rooms that work for both short and long meetings. Whether you want coffee and something simple, small plates along the way or a full lunch, we adapt to what you need.'),
        ]),
        ('mat', 'Mat, allergier og barn', 'Food, allergies and children', [
            ('faq.s.gluten', 'Har dere glutenfrie alternativer?',
             'Ja. Vi har et burgerbrød uten gluten, melk og egg som alternativ til vårt eget nybakte brød (+15 kr), og de fleste burgerne kan lages glutenfrie. Friesene er naturlig glutenfrie, og alle retter er merket med allergener i menyen. Si fra til servitøren, så tar kjøkkenet forholdsregler.',
             'Do you have gluten-free options?',
             'Yes. We have a bun without gluten, milk or egg as an alternative to our own freshly baked one (+NOK 15), and most of the burgers can be made gluten free. The fries are naturally gluten free, and every dish is labelled with allergens on the menu. Tell your server so the kitchen can take precautions.'),
            ('faq.s.allergy', 'Kan dere ta hensyn til allergier?',
             'Ja. Alle retter er merket med allergener i menyen. Gi beskjed når du booker og si fra til servitøren når du kommer, så finner vi noe som passer.',
             'Can you accommodate allergies?',
             'Yes. Every dish is labelled with allergens on the menu. Let us know when you book and tell your server when you arrive, and we will find something that works.'),
            ('faq.s.veg', 'Har dere vegetarretter?',
             'Ja, vi har vegetaralternativer på menyen, og flere retter kan tilpasses. Spør servitøren, så hjelper vi deg å finne noe som passer.',
             'Do you have vegetarian dishes?',
             'Yes, there are vegetarian options on the menu and several dishes can be adapted. Ask your server and we will help you find something.'),
            ('faq.s.kids', 'Er det barnevennlig?',
             'Ja. Barnemenyen finnes på alle tre restaurantene og har hamburger med fries, chicken tenders med fries, ostetoast eller bare fries, fra 89 til 169 kr. Den kommer med tegninger og oppgaver mens de venter på maten.',
             'Is it child friendly?',
             'Yes. The kids menu is available at all three restaurants and has a hamburger with fries, chicken tenders with fries, a ham and cheese toastie, or just fries, from NOK 89 to 169. It comes with drawings and puzzles while they wait.'),
            ('faq.s.pris', 'Hva koster en burger?',
             f'Burgerne koster fra {burger_range("majorstua")[0]} til {burger_range("majorstua")[1]} kr, med 150 g patty av kjøtt vi kverner selv. Fries kommer i tillegg, fra {fries_from() or 84} kr. <a href="/meny/">Se hele menyen med priser</a>.',
             'What does a burger cost?',
             f'Burgers are NOK {burger_range("majorstua")[0]}–{burger_range("majorstua")[1]}, with a 150 g patty of beef we grind ourselves. Fries are extra, from NOK {fries_from() or 84}. <a href="/meny/">See the full menu with prices</a>.'),
            ('faq.s.craft', 'Hva gjør maten deres spesiell?',
             'Vi lager det meste selv, litt om gangen, så råvarene holder seg ferske. Vi baker burgerbrødene, kverner kjøttet her og bruker <a href="/fries/">tre dager på friesene</a>. Samtidig liker vi å utfordre hva en burger kan være, og henter smaker fra hele verden.',
             'What makes your food different?',
             'We make most of it ourselves, in small batches, so the ingredients stay fresh. We bake the buns, grind the beef here and spend <a href="/fries/">three days on the fries</a>. At the same time we like to push what a burger can be, and take flavours from all over the world.'),
        ]),
        ('sted', 'I restauranten', 'At the restaurant', [
            ('faq.s.dogs', 'Er hunder velkomne?',
             'Ja, på alle tre restaurantene. Vi ber bare om at hunden holdes i bånd og ikke forstyrrer andre gjester.',
             'Are dogs welcome?',
             'Yes, at all three restaurants. We only ask that the dog is kept on a lead and does not disturb other guests.'),
            ('faq.s.outside', 'Har dere uteservering?',
             'Solli plass og Tønsberg har store uteserveringer. Ute tar vi ikke reservasjoner, så der gjelder drop-in. Majorstua har ikke egen uteservering, men på varme dager åpner vi de store vinduene.',
             'Do you have outdoor seating?',
             'Solli plass and Tønsberg both have large terraces. We do not take reservations outside, so it is walk-in only there. Majorstua has no terrace of its own, but on warm days we open the big windows.'),
            ('faq.s.wheelchair', 'Er det tilrettelagt for rullestol?',
             'Ja. Si gjerne fra når du booker, så setter vi av god plass til bordet.',
             'Is it wheelchair accessible?',
             'Yes. Do mention it when you book so we can set aside enough room at the table.'),
            ('faq.s.pram', 'Er det plass til barnevogn?',
             'Ja, alle tre restaurantene får plass til barnevogn. Si fra når du booker, så setter vi av plass ved bordet.',
             'Is there room for a pram?',
             'Yes, all three restaurants can make room for a pram. Let us know when you book and we will set aside space at the table.'),
            ('faq.s.drink', 'Kan jeg komme innom bare for noe å drikke?',
             'Ja. Alle tre har egen bar, og du kan like godt sette deg ved et vanlig bord uten å spise. Vi har et stort alkoholfritt utvalg, så det finnes alltid noe ordentlig i glasset. <a href="/cocktails/">Mer om baren</a>.',
             'Can I drop in just for a drink?',
             'Yes. All three have their own bar, and you are just as welcome at an ordinary table without eating. We keep a large alcohol-free selection, so there is always something proper in the glass. <a href="/cocktails/">More about the bar</a>.'),
            ('faq.s.hours', 'Når har dere åpent?',
             f'Kjøkkenet: {_tider_no()} Baren holder åpent {_bar_no()}. Åpningstidene for hver restaurant står på restaurantsidene.',
             'What are your opening hours?',
             f'The kitchen: {_tider_en()} The bar stays open {_bar_en()}. Hours for each restaurant are on its own page.'),
            ('faq.s.where', 'Hvor ligger restaurantene?',
             f'{_steder_no()}. Kart og veibeskrivelse ligger på hver restaurantside.',
             'Where are the restaurants?',
             f'{_steder_en()}. Maps and directions are on each restaurant page.'),
        ]),
        ('ta', 'Take-away og gavekort', 'Take-away and gift cards', [
            ('faq.s.ta', 'Har dere take-away?',
             f'Ja. Du kan forhåndsbestille og hente selv på alle tre restaurantene. Fra {" og ".join(lev)} kan du også få maten levert med Wolt og Foodora. Hjemlevering koster {ORG.get("deliveryMarkup", "15–20 %")} mer enn å hente selv. <a href="/takeaway/">Bestill take-away</a>.',
             'Do you do take-away?',
             f'Yes. You can pre-order and pick up at all three restaurants. From {" and ".join(lev)} you can also have it delivered by Wolt and Foodora. Home delivery costs {ORG.get("deliveryMarkup", "15–20 %").replace(" %", "%")} more than picking it up yourself. <a href="/takeaway/">Order take-away</a>.'),
            ('faq.s.tabox', 'Holder maten seg på veien hjem?',
             'Esken har lufting, så dampen slipper ut og friesene holder seg sprø. Henter du selv, kommer maten rett fra kjøkkenet.',
             'Does the food survive the trip home?',
             'The box is vented, so the steam escapes and the fries stay crisp. If you pick up yourself, the food comes straight from the kitchen.'),
            ('faq.s.gift', 'Kan jeg kjøpe gavekort?',
             f'Ja. Gavekortet kjøper du i <a href="{ORG["giftcard"]}" rel="noopener" target="_blank">nettbutikken vår</a>, og det kan brukes på alle tre restaurantene.',
             'Can I buy a gift card?',
             f'Yes. You buy it in <a href="{ORG["giftcard"]}" rel="noopener" target="_blank">our online shop</a>, and it works at all three restaurants.'),
        ]),
    ]
