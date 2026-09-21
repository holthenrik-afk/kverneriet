#!/usr/bin/env python3
"""Presse-komponenten: avislogoer (monokrome via CSS-maske), terningkast og sitatkort.
Skriver om presse-seksjonene på index/majorstua/solli/takeaway og eksporterer snippets til build-landing.py.
Kjør: python3 tools/press.py && python3 tools/build-landing.py"""
import re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv, html as H
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def e(s): return H.escape(s, quote=True)

def dice(n=6, source='Dagbladet', size=''):
    """Dagbladets ikoniske røde terning (assets/press/dagbladet-terning.svg) med tallet ved siden."""
    return (f'<span class="terning{(" "+size) if size else ""}">'
            f'<img class="terning__die" src="/assets/press/dagbladet-terning.png" alt="Terningkast {n} fra {source}" width="256" height="192">'
            f'<span class="terning__label" aria-hidden="true">{n}<span class="terning__of">/6</span></span></span>')

def logo(name):
    return f'<span class="press-logo press-logo--{name.lower()}" role="img" aria-label="{name}"></span>'

QUOTES = {
 'db_perfekt':   dict(src='Dagbladet', die=6, q='Burgerne fra Kverneriet er så nære man kommer en perfekt.', ctx='Dagbladets take-away-test'),
 'db_kjott':     dict(src='Dagbladet', die=6, q='Selve kjøttet er det klart beste i testen. Det er også helt perfekt stekt - ikke for mye, ikke for lite.', ctx='Dagbladets take-away-test'),
 'db_solli':     dict(src='Dagbladet', die=6, q='Burgeren fra Kverneriet på Solli Plass rekker å gi et godt inntrykk allerede før noen har sett den: - Dette er jo en suveren innpakning!', ctx='Dagbladets take-away-test'),
 'db_boks':      dict(src='Dagbladet', die=6, q='Burgeren leveres nemlig i en fin pappboks, hvor burgeren kan skyves ut. Det betyr at burgeren holder seg perfekt i formen - og dessuten holder den seg skikkelig god og varm også.', ctx='Dagbladets take-away-test'),
 'fa_riktig':    dict(src='Finansavisen', die=6, q='Her har de gjort alt riktig, sier Long. Brødet er luftig og kjøttet er virkelig godt.', ctx='Finansavisens take-away-test'),
 'fa_tenk':      dict(src='Finansavisen', die=6, q='Tenk at dette er takeaway? Kanskje flere burde kreve at man henter selv?', ctx='Finansavisens take-away-test'),
 'fa_innpakning':dict(src='Finansavisen', die=6, q='Innpakningen på Kverneriet er noe helt annet. Den store boksen ikke bare ser fin ut, men den har bevart burgeren så godt som kan gjøres på en halvlang sykkeltur. Første bit bekrefter førsteinntrykket.', ctx='Finansavisens take-away-test'),
 'fa_krone':     dict(src='Finansavisen', die=6, q='Og hver eneste krone ekstra de bruker på innpakningen er verdt det, legger Short til. Og det er nesten så man hører at friesene er crispy.', ctx='Finansavisens take-away-test'),
}

def card(key):
    q = QUOTES[key]
    return (f'<article class="press-card"><div class="press-card__head">{logo(q["src"])}{dice(6, q["src"], "terning--lg") if q["die"] else ""}</div>'
            f'<p>&laquo;{e(q["q"])}&raquo;</p><span class="caption">{e(q["ctx"])}</span></article>')

def section(keys, tint=True, flush=False):
    cls = 'section' + (' section--tint' if tint else '') + (' section--flush-top' if flush else '')
    return (f'  <section class="{cls}" id="presse">\n    <div class="wrap">\n'
            f'      <div class="press-head"><span class="kv-eyebrow" data-i18n="press.eyebrow">Omtalt i</span>'
            f'<div class="press-head__logos">{logo("Dagbladet")}{logo("Finansavisen")}</div></div>\n'
            f'      <div class="press-grid" style="grid-template-columns:repeat({len(keys)},1fr)">{"".join(card(k) for k in keys)}</div>\n'
            f'    </div>\n  </section>\n')

TRUST = ('    <div class="trust">\n'
         f'      <span class="trust__item">{dice(6, "Dagbladet", "terning--lg")}</span>\n'
         '      <span class="trust__sep" aria-hidden="true"></span>\n'
         f'      <span class="trust__item">{logo("Finansavisen")}<strong data-i18n="home.trustTa">Oslos beste take-away-burger</strong></span>\n'
         '    </div>')

if __name__ == '__main__':
    SEC_RE = re.compile(r'  <!-- Press(?:e)? -->\n  <section class="section[^"]*"(?: id="presse")?>\n    <div class="wrap">\n      <div class="divider"><span data-i18n="home.press">Fra pressen</span></div>.*?\n  </section>\n', re.S)
    SEC2_RE = re.compile(r'  <section class="section[^"]*" id="presse">.*?\n  </section>\n', re.S)
    plan = {
      'index.html':            (['db_perfekt', 'fa_riktig', 'fa_tenk'], True, False),
      'majorstua/index.html':  (['db_perfekt', 'db_kjott', 'fa_riktig'], False, True),
      'solli/index.html':      (['db_solli', 'fa_innpakning', 'fa_tenk'], False, True),
    }
    for f, (keys, tint, flush) in plan.items():
        s = open(f, encoding='utf-8').read()
        new = section(keys, tint, flush)
        s2, n = SEC_RE.subn(lambda m: new, s, count=1)
        if n == 0: s2, n = SEC2_RE.subn(lambda m: new, s, count=1)
        if n != 1: print(f, 'press section owned by media.py – skipped'); continue
        open(f, 'w', encoding='utf-8').write(s2); print(f, 'press ok')

    # Forsidens tillitsrad
    s = open('index.html', encoding='utf-8').read()
    s2, n = re.subn(r'    <div class="trust">.*?\n    </div>\n', TRUST + '\n', s, count=1, flags=re.S)
    if n != 1: raise SystemExit('trust row not found')
    open('index.html', 'w', encoding='utf-8').write(s2); print('trust ok')

    # Takeaway: presse-radene beholder foto + to sitater, men sitatene blir kort
    s = open('takeaway/index.html', encoding='utf-8').read()
    rows = [('3.jpg', ['fa_innpakning', 'db_solli']), ('2.jpg', ['fa_riktig', 'db_kjott']), ('6.jpg', ['fa_krone', 'db_boks']), ('1.jpg', ['fa_tenk', 'db_perfekt'])]
    blocks = re.findall(r'<div class="press-row__quotes">.*?</div>\n        </div>', s, re.S)
    if len(blocks) != 4: raise SystemExit(f'takeaway rows: {len(blocks)}')
    for blk, (_, keys) in zip(blocks, rows):
        s = s.replace(blk, '<div class="press-row__quotes">' + ''.join(card(k) for k in keys) + '</div>\n        </div>', 1)
    s = s.replace('<div class="divider"><span data-i18n="home.press">Fra pressen</span></div>',
                  f'<div class="press-head"><span class="kv-eyebrow" data-i18n="press.eyebrow">Omtalt i</span><div class="press-head__logos">{logo("Dagbladet")}{logo("Finansavisen")}</div></div>', 1)
    open('takeaway/index.html', 'w', encoding='utf-8').write(s); print('takeaway ok')
