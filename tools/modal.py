#!/usr/bin/env python3
"""Book/take-away-modalen og bookingskjemaet, generert likt på alle sider (fra content/venues.json).
Bookingen skjer i modalen: velg restaurant → online booking (Zenchef, i en ramme inne i modalen) eller
større grupper (forespørsel) → sendt. Ingen lenker ut av modalen. Samme skjema brukes i #booking på
restaurantsidene. Kjør: python3 tools/build.py (eller python3 tools/modal.py for bare modalen)."""
import re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv, i18n_gen as G
os.chdir(kv.ROOT)

# UI-tekster som hører til modalen/skjemaet (norsk + engelsk)
G.add('book.onlineIntro', 'Bord for inntil {n} personer booker du direkte her og får bekreftelse med en gang. Er dere flere, velg «Større grupper».', 'Tables for up to {n} guests are booked right here with instant confirmation. Larger parties: choose “Larger groups”.')
G.add('book.openWindow', 'Åpne online booking i eget vindu', 'Open online booking in a new window')
G.add('book.largeIntro', 'Grupper over 8 (7 i Tønsberg) sender en forespørsel og velger én matpakke for hele bordet. Vi svarer på e-post.', 'Groups larger than 8 (7 in Tønsberg) send a request and choose one food package for the whole table. We reply by e-mail.')
G.add('f.package', 'Matpakke', 'Food package')
G.add('f.packageHint', 'Bordet velger én pakke. Barnemeny 169 kr for gjester under 12.', 'The table chooses one package. Kids menu NOK 169 for guests under 12.')
G.add('f.src.press', 'Avis eller anmeldelse', 'Newspaper or review')
G.add('f.src.other', 'Annet', 'Other')
G.add('f.submit', 'Send forespørsel', 'Send request')
G.add('book.sentBadge', 'Forespørsel klar', 'Request ready')
G.add('book.sentBody', 'E-postprogrammet ditt åpner med forespørselen ferdig utfylt – trykk send. Vi svarer på e-post, og bordet er bekreftet når du har fått svar fra oss.', 'Your e-mail app opens with the request filled in – just press send. We reply by e-mail, and the table is confirmed once you have our answer.')
G.add('book.again', 'Send en ny forespørsel', 'Send another request')
G.add('foot.hours', 'Åpningstider', 'Opening hours')
G.add('a11y.skip', 'Hopp til innholdet', 'Skip to content')
G.add('menu.kidsPdf', 'Barnemenyen finnes også som utskriftsvennlig PDF.', 'The kids menu is also available as a printable PDF.')
G.add('f.consent', 'Forespørselen sendes som e-post til restauranten. Ved å sende inn godtar du at Kverneriet bruker navn, telefon og e-post til å svare deg og håndtere bookingen. Vi deler ikke opplysningene med andre.', 'The request is sent as an e-mail to the restaurant. By submitting you agree that Kverneriet uses your name, phone and e-mail to reply and handle the booking. We never share your details.')
G.add('modal.pickupNote', 'I Tønsberg henter du selv – forhåndsbestill på OrderX.', 'In Tønsberg it is pick-up only – pre-order on OrderX.')
G.add('modal.note', 'Hjemlevering (Majorstua og Solli) kjøres av Wolt og Foodora og koster 15–20 % mer enn å hente selv. I Tønsberg henter du selv.', 'Delivery (Majorstua and Solli) is run by Wolt and Foodora and costs 15–20% more than pick-up. Tønsberg is pick-up only.')

V = kv.venues(); ORG = V['org']
VENUES = [(v['slug'], v['name']) for v in V['venues']]
ZENCHEF = 'https://bookings.zenchef.com/results?rid={rid}&lang=no'

def zenchef_url(slug): return ZENCHEF.format(rid=kv.venue(slug)['zenchef'])

def booking_form(prefix, with_venue_picker, venue='majorstua'):
    """prefix gir unike id-er per instans (modal vs. side). Hooks er klasser (.bk-*).
    data-zenchef-* på rota gir JS bookingadressen per restaurant; lenken er fallback uten JS."""
    picker = ''
    if with_venue_picker:
        picker = ('<div class="field"><span class="field__label" data-i18n="book.venue">Hvilken restaurant?</span>'
                  '<div class="seg seg--block bk-venue" role="group" aria-label="Restaurant">'
                  + ''.join(f'<button type="button" data-bvenue="{slug}"{" class=\"is-on\" aria-pressed=\"true\"" if slug == venue else " aria-pressed=\"false\""}>{name}</button>' for slug, name in VENUES)
                  + '</div></div>')
    zc = ' '.join(f'data-zenchef-{v["slug"]}="{ZENCHEF.format(rid=v["zenchef"])}"' for v in V['venues'])
    thr = ' '.join(f'data-threshold-{v["slug"]}="{v["groupThreshold"]}"' for v in V['venues'])
    mail = ' '.join(f'data-email-{v["slug"]}="{v["email"]}"' for v in V['venues'])
    n = kv.venue(venue)['groupThreshold']
    return f'''<div class="bk" data-venue="{venue}" {zc} {thr} {mail}>
        {picker}
        <div class="seg seg--block bk-mode" role="group" aria-label="Bookingtype">
          <button type="button" class="is-on" aria-pressed="true" data-mode="online" data-i18n="book.online">Online booking</button>
          <button type="button" aria-pressed="false" data-mode="large" data-i18n="book.large">Større grupper</button>
        </div>
        <div class="bk-online stack-4" style="margin-top:var(--space-5)">
          <p class="bk-online__intro" data-i18n="book.onlineIntro" data-i18n-n="{n}">Bord for inntil {n} personer booker du direkte her og får bekreftelse med en gang. Er dere flere, velg «Større grupper».</p>
          <div class="bk-frame" aria-live="polite"></div>
          <p class="caption"><a class="bk-zenchef-link" href="{zenchef_url(venue)}" target="_blank" rel="noopener" data-i18n="book.openWindow">Åpne online booking i eget vindu</a></p>
        </div>
        <form class="bk-large stack-4" style="margin-top:var(--space-5)" hidden>
          <p class="caption" data-i18n="book.largeIntro">Grupper over 8 (7 i Tønsberg) sender en forespørsel og velger én matpakke for hele bordet. Vi svarer på e-post.</p>
          <div class="form-grid-2">
            <div class="field"><label class="field__label" for="{prefix}-lb-name" data-i18n="f.name">Fullt navn</label><input id="{prefix}-lb-name" name="name" type="text" required autocomplete="name"></div>
            <div class="field"><label class="field__label" for="{prefix}-lb-phone" data-i18n="f.phone">Telefonnummer</label><input id="{prefix}-lb-phone" name="phone" type="tel" required autocomplete="tel"></div>
          </div>
          <div class="field"><label class="field__label" for="{prefix}-lb-email" data-i18n="f.email">E-postadresse</label><input id="{prefix}-lb-email" name="email" type="email" required autocomplete="email"></div>
          <div class="form-grid-3">
            <div class="field"><label class="field__label" for="{prefix}-lb-date" data-i18n="f.date">Dato for besøket</label><input id="{prefix}-lb-date" name="date" type="date" required></div>
            <div class="field"><label class="field__label" for="{prefix}-lb-earliest" data-i18n="f.earliest">Tidligste start</label><input id="{prefix}-lb-earliest" name="earliest" type="time"></div>
            <div class="field"><label class="field__label" for="{prefix}-lb-latest" data-i18n="f.latest">Seneste start</label><input id="{prefix}-lb-latest" name="latest" type="time"></div>
          </div>
          <div class="form-grid-2">
            <div class="field"><label class="field__label" for="{prefix}-lb-guests" data-i18n="f.guests">Gjester</label><div class="select-wrap"><select id="{prefix}-lb-guests" name="guests"><option>8</option><option>9</option><option>10</option><option>12</option><option>15</option><option>20+</option></select></div></div>
            <div class="field"><label class="field__label" for="{prefix}-lb-package" data-i18n="f.package">Matpakke</label><div class="select-wrap"><select id="{prefix}-lb-package" name="package">{''.join(f'<option>{p["name"]} ({p["price"]} kr)</option>' for p in ORG['packages']['items'])}</select></div><span class="field__hint" data-i18n="f.packageHint">Bordet velger én pakke. Barnemeny {ORG['packages']['kids']} kr for gjester under 12.</span></div>
          </div>
          <div class="form-grid-2">
            <div class="field"><label class="field__label" for="{prefix}-lb-kids" data-i18n="f.kids">Barnemenyer</label><div class="select-wrap"><select id="{prefix}-lb-kids" name="kids"><option>0</option><option>1</option><option>2</option><option>3</option><option>4</option></select></div></div>
            <div class="field"><label class="field__label" for="{prefix}-lb-occasion" data-i18n="f.occasion">Hva er anledningen?</label><input id="{prefix}-lb-occasion" name="occasion" type="text"></div>
          </div>
          <div class="field"><label class="field__label" for="{prefix}-lb-request" data-i18n="f.request">Andre ønsker?</label><textarea id="{prefix}-lb-request" name="request" rows="3"></textarea></div>
          <div class="field"><label class="field__label" for="{prefix}-lb-source" data-i18n="f.source">Hvor hørte du om oss?</label><div class="select-wrap"><select id="{prefix}-lb-source" name="source">
            <option value="google" data-i18n="f.src.google">Google</option><option value="social" data-i18n="f.src.social">Instagram eller Facebook</option><option value="friends" data-i18n="f.src.friends">Anbefalt av venner</option><option value="walk" data-i18n="f.src.walk">Gikk forbi</option><option value="press" data-i18n="f.src.press">Avis eller anmeldelse</option><option value="other" data-i18n="f.src.other">Annet</option>
          </select></div></div>
          <label class="check"><input type="checkbox" name="consent" required><span data-i18n="f.consent">Forespørselen sendes som e-post til restauranten. Ved å sende inn godtar du at Kverneriet bruker navn, telefon og e-post til å svare deg og håndtere bookingen. Vi deler ikke opplysningene med andre.</span></label>
          <label class="check"><input type="checkbox" name="newsletter"><span data-i18n="f.newsletter">Ja takk, send meg nyheter og tilbud på e-post og SMS. Kan avmeldes når som helst.</span></label>
          <button class="btn btn--primary btn--lg btn--block" type="submit" data-label="Send forespørsel" data-i18n="f.submit">Send forespørsel</button>
        </form>
        <div class="bk-sent stack-4" style="margin-top:var(--space-5)" hidden>
          <span class="badge" data-i18n="book.sentBadge">Forespørsel klar</span>
          <p style="color:var(--text-muted)"><span data-i18n="book.sentBody">E-postprogrammet ditt åpner med forespørselen ferdig utfylt – trykk send. Vi svarer på e-post, og bordet er bekreftet når du har fått svar fra oss.</span></p>
          <button class="btn btn--ghost btn--sm bk-again" type="button" data-i18n="book.again">Send en ny forespørsel</button>
        </div>
      </div>'''

def delivery_note(slug):
    """Påslagsnoten vises bare der det finnes hjemlevering."""
    c = kv.venue(slug)['channels']
    if c.get('wolt') or c.get('foodora'):
        return f'<p class="caption" data-i18n="modal.note">Hjemlevering kjøres av partnerne våre og koster {ORG["deliveryMarkup"]} mer enn å hente selv.</p>'
    return '<p class="caption" data-i18n="modal.pickupNote">I Tønsberg henter du selv – forhåndsbestill på OrderX.</p>'

def order_group(slug):
    v = kv.venue(slug); c = v['channels']
    links = [btn('btn--primary', c['pickup'], 'act.pickup', 'Hent selv', f'order:{slug}:pickup')]
    if c.get('wolt'): links.append(btn('btn--outline', c['wolt'], 'act.wolt', 'Wolt hjemlevering (+15-20%)', f'order:{slug}:wolt'))
    if c.get('foodora'): links.append(btn('btn--outline', c['foodora'], 'act.foodora', 'Foodora hjemlevering (+15-20%)', f'order:{slug}:foodora'))
    label = f'{v["name"]}, {v["city"]}' if v['city'] != v['name'] else v['name']
    return f'<div class="order-group" data-venue="{slug}"><div class="kv-eyebrow">{label}</div><div class="order-group__channels">{"".join(links)}</div></div>'

def btn(cls, href, key, text, track):
    utm = href + ('&' if '?' in href else '?') + f'utm_source=kverneriet.com&utm_medium=website&utm_campaign=takeaway&utm_content={track.split(":")[1]}-{track.split(":")[2]}' if 'orderx.eu' in href else href
    return f'<a class="btn {cls} btn--md btn--block" href="{utm}" target="_blank" rel="noopener" data-track="{track}" data-i18n="{key}">{text}</a>'

TA = ''.join(order_group(v['slug']) for v in V['venues'])

MODAL = f'''<!-- Book / take-away-modal (generert av tools/modal.py) -->
<div class="modal-root" id="order-modal" role="dialog" aria-modal="true" aria-labelledby="order-title">
  <div class="modal-root__backdrop" data-order-close></div>
  <div class="modal modal--wide">
    <button class="icon-btn modal__close" type="button" data-order-close aria-label="Lukk">&times;</button>
    <p class="modal__title display-3" id="order-title">Book bord</p>
    <div class="field" style="margin-top:var(--space-5)"><span class="field__label" data-i18n="book.venue">Hvilken restaurant?</span>
      <div class="seg seg--block" id="modal-venue" role="group" aria-label="Restaurant">{''.join(f'<button type="button" data-mvenue="{s}"{" class=\"is-on\" aria-pressed=\"true\"" if i == 0 else " aria-pressed=\"false\""}>{n}</button>' for i, (s, n) in enumerate(VENUES))}</div>
    </div>
    <div class="seg seg--block" id="action-mode" role="group" aria-label="Book eller take-away" style="margin-top:var(--space-4)">
      <button type="button" class="is-on" aria-pressed="true" data-amode="book" data-i18n="act.book">Book bord</button>
      <button type="button" aria-pressed="false" data-amode="ta" data-i18n="act.takeaway">Take-away</button>
    </div>
    <div id="modal-book" style="margin-top:var(--space-5)">
      {booking_form('m', False)}
    </div>
    <div id="modal-ta" class="stack-6" style="margin-top:var(--space-6)" hidden>
      <span class="kv-eyebrow" lang="en">Stay safe - eat home</span>
      {TA}
      <p class="caption" data-i18n="modal.note">Hjemlevering (Majorstua og Solli) kjøres av Wolt og Foodora og koster {ORG['deliveryMarkup']} mer enn å hente selv. I Tønsberg henter du selv.</p>
    </div>
  </div>
</div>
'''

MODAL_RE = re.compile(r'<!-- (?:Take-away-modal|Book / take-away-modal[^>]*) -->\n<div class="modal-root" id="order-modal".*?\n</div>\n+(?=</body>)', re.S)

def apply(html):
    """Setter inn / erstatter modalen rett før </body>."""
    s2, n = MODAL_RE.subn(lambda m: MODAL.rstrip('\n') + '\n\n', html, count=1)
    if n == 0:
        s2 = html.replace('</body>', MODAL.rstrip('\n') + '\n\n</body>', 1)
    return s2

if __name__ == '__main__':
    for f in kv.all_files():
        if not os.path.exists(f): continue
        s = open(f, encoding='utf-8').read()
        open(f, 'w', encoding='utf-8').write(apply(s)); print(f, 'modal ok')
