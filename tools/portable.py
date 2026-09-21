"""Portable Text (Sanity) → HTML. Dekker det redaktørene kan lage i Studio: avsnitt, h2/h3, sitat, punkt- og
nummerlister, fet/kursiv/lenke og bilder (type «photo» med url + alt fra fetch_sanity.py)."""
import html as H
import re

def _esc(s): return H.escape(s, quote=False)

def _spans(block):
    defs = {d['_key']: d for d in block.get('markDefs', [])}
    out = ''
    for ch in block.get('children', []):
        t = _esc(ch.get('text', '')).replace('\n', '<br>')
        for m in ch.get('marks', []):
            if m == 'strong': t = f'<strong>{t}</strong>'
            elif m == 'em': t = f'<em>{t}</em>'
            elif m in defs and defs[m].get('_type') == 'link':
                href = defs[m].get('href', '#'); ext = href.startswith('http') and 'kverneriet.com' not in href
                t = f'<a href="{H.escape(href, quote=True)}"{" target=\"_blank\" rel=\"noopener\"" if ext else ""}>{t}</a>'
        out += t
    return out

def _faq_html(items):
    rows = ''.join(f'<details class="faq__item"><summary><h3 class="faq__q">{q}</h3></summary><div class="faq__a"><p>{a}</p></div></details>' for q, a in items)
    return f'<section class="faq-inline" id="faq"><h2 class="display-3">Ofte stilte spørsmål</h2><div class="faq" style="margin-top:var(--space-4)">{rows}</div></section>'

def to_html(blocks, cls_p=''):
    """Full HTML (blogginnlegg, landingssider). En «## Ofte stilte spørsmål»-seksjon med ### spørsmål + svar
    blir til samme <details>-markup som resten av siden (og dermed FAQPage-markup via seo_head)."""
    blocks = list(blocks or [])
    for i, b in enumerate(blocks):
        if b.get('_type') == 'block' and b.get('style') == 'h2' and _spans(b).strip().lower().startswith('ofte stilte'):
            items = []; q = None; j = i + 1
            while j < len(blocks) and not (blocks[j].get('_type') == 'block' and blocks[j].get('style') == 'h2'):
                bj = blocks[j]
                if bj.get('_type') == 'block' and bj.get('style') == 'h3': q = _spans(bj); items.append([q, ''])
                elif bj.get('_type') == 'block' and items: items[-1][1] = (items[-1][1] + ' ' + _spans(bj)).strip()
                j += 1
            if items:
                return to_html(blocks[:i], cls_p) + '\n' + _faq_html([(q, a) for q, a in items if a]) + ('\n' + to_html(blocks[j:], cls_p) if j < len(blocks) else '')
    out = []; lst = None
    def close():
        nonlocal lst
        if lst: out.append('</ul>' if lst == 'bullet' else '</ol>'); lst = None
    for b in blocks or []:
        t = b.get('_type')
        if t == 'block':
            if b.get('listItem'):
                if lst != b['listItem']:
                    close(); lst = b['listItem']; out.append('<ul>' if lst == 'bullet' else '<ol>')
                out.append(f'<li>{_spans(b)}</li>'); continue
            close()
            st = b.get('style', 'normal'); inner = _spans(b)
            if st == 'h2': out.append(f'<h2 class="display-3">{inner}</h2>')
            elif st == 'h3': out.append(f'<h3 class="display-4">{inner}</h3>')
            elif st == 'blockquote': out.append(f'<blockquote class="pullquote">{inner}</blockquote>')
            else: out.append(f'<p{(" class=\"" + cls_p + "\"") if cls_p else ""}>{inner}</p>')
        elif t == 'photo' and b.get('url'):
            close()
            w, h = b.get('w'), b.get('h')
            out.append(f'<figure class="photo photo--inline"><img src="{H.escape(b["url"], quote=True)}" alt="{H.escape(b.get("alt", ""), quote=True)}" loading="lazy"{f" width=\"{w}\" height=\"{h}\"" if w and h else ""}></figure>')
    close()
    return '\n'.join(out)

def paragraphs(blocks):
    """Til landingssidene, som forventer en liste av avsnitt (HTML-strenger)."""
    return [(_spans(b)) for b in (blocks or []) if b.get('_type') == 'block' and not b.get('listItem')]

def plain(blocks, limit=None):
    txt = ' '.join(' '.join(ch.get('text', '') for ch in b.get('children', [])) for b in (blocks or []) if b.get('_type') == 'block')
    txt = re.sub(r'\s+', ' ', txt).strip()
    return (txt[:limit].rsplit(' ', 1)[0] + '…') if limit and len(txt) > limit else txt
