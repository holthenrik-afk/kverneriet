"""Begrenset markdown → Portable Text (Sanity). Dekker det bloggen bruker: ## / ### overskrifter, avsnitt,
- punktlister, 1. nummerlister, > sitat, **fet**, *kursiv*, [tekst](url). Brukes av tools/publish_post.py."""
import re, itertools

_k = itertools.count(1)
def key(p='k'): return f'{p}{next(_k)}'

def spans(text):
    """Inline: **fet**, *kursiv*, [tekst](url) → children + markDefs."""
    children, defs = [], []
    tok = re.compile(r'\[([^\]]+)\]\(([^)]+)\)|\*\*(.+?)\*\*|\*(.+?)\*')
    pos = 0
    for m in tok.finditer(text):
        if m.start() > pos: children.append({'_type': 'span', '_key': key('s'), 'text': text[pos:m.start()], 'marks': []})
        if m.group(1):
            d = {'_type': 'link', '_key': key('l'), 'href': m.group(2)}; defs.append(d)
            children.append({'_type': 'span', '_key': key('s'), 'text': m.group(1), 'marks': [d['_key']]})
        elif m.group(3): children.append({'_type': 'span', '_key': key('s'), 'text': m.group(3), 'marks': ['strong']})
        else: children.append({'_type': 'span', '_key': key('s'), 'text': m.group(4), 'marks': ['em']})
        pos = m.end()
    if pos < len(text): children.append({'_type': 'span', '_key': key('s'), 'text': text[pos:], 'marks': []})
    if not children: children.append({'_type': 'span', '_key': key('s'), 'text': '', 'marks': []})
    return children, defs

def block(text, style='normal', list_item=None):
    ch, defs = spans(text)
    b = {'_type': 'block', '_key': key('b'), 'style': style, 'markDefs': defs, 'children': ch}
    if list_item: b['listItem'] = list_item; b['level'] = 1
    return b

def convert(md):
    out = []; para = []
    def flush():
        # to mellomrom på slutten av en linje = linjeskift (markdown), ellers slås linjene sammen
        if para: out.append(block(''.join(t + ('\n' if br else ' ') for t, br in para).strip())); para.clear()
    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip(): flush(); continue
        if line.startswith('### '): flush(); out.append(block(line[4:].strip(), 'h3')); continue
        if line.startswith('## '): flush(); out.append(block(line[3:].strip(), 'h2')); continue
        if line.startswith('# '): flush(); out.append(block(line[2:].strip(), 'h2')); continue
        if line.startswith('> '): flush(); out.append(block(line[2:].strip(), 'blockquote')); continue
        m = re.match(r'^\s*[-*•]\s+(.*)', line)
        if m: flush(); out.append(block(m.group(1), 'normal', 'bullet')); continue
        m = re.match(r'^\s*\d+[.)]\s+(.*)', line)
        if m: flush(); out.append(block(m.group(1), 'normal', 'number')); continue
        if line.startswith('|'): continue  # tabeller støttes ikke i Portable Text – skribentene skal bruke lister
        para.append((line.strip(), raw.endswith('  ')))
    flush()
    return out
