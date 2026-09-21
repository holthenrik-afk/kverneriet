"""Genererte oversettelser (tekst generatorene skriver, f.eks. om-tekster, FAQ, åpningstider).
Samles her mens tools/build.py kjører og skrives til content/i18n-gen.js, som site.js legger oppå
content/i18n.js. Nøkler med HTML (lenker) merkes data-i18n-html på elementet."""
import json, os
import kv

_D = {'no': {}, 'en': {}}

def add(key, no, en):
    _D['no'][key] = no; _D['en'][key] = en
    return key

def write():
    out = ('// Generert av tools/build.py – ikke rediger. Kilder: build_venue.py, build_landing.py, faq.py.\n'
           'window.KV_I18N_GEN=' + json.dumps(_D, ensure_ascii=False, separators=(',', ':')) + ';\n')
    open(os.path.join(kv.ROOT, 'content/i18n-gen.js'), 'w', encoding='utf-8').write(out)
    return len(_D['no'])
