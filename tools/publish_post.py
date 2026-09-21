#!/usr/bin/env python3
"""Publiserer et blogginnlegg til Sanity fra en JSON-fil {title, slug, seoTitle, excerpt, markdown, faq[], author?, publishedAt?, image?}.
FAQ-en legges til som «## Ofte stilte spørsmål» med spørsmål som ### og svar som avsnitt (blir FAQ-blokk i HTML via portable.py).
Bruk: python3 tools/publish_post.py post.json [--image /assets/img/x.jpg]   (krever `npx sanity login` i studio-kverneriet)"""
import json, os, sys, subprocess, datetime, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kv, md2pt
os.chdir(kv.ROOT)

src = json.load(open(sys.argv[1], encoding='utf-8'))
image = sys.argv[sys.argv.index('--image') + 1] if '--image' in sys.argv else src.get('image')
md = src['markdown'].rstrip() + '\n'
if src.get('faq'):
    md += '\n## Ofte stilte spørsmål\n\n' + ''.join(f'### {f["q"]}\n\n{f["a"]}\n\n' for f in src['faq'])
slug = re.sub(r'[^a-z0-9-]+', '-', src['slug'].lower().replace('æ', 'ae').replace('ø', 'o').replace('å', 'a')).strip('-')
doc = {
    '_id': f'post-{slug}', '_type': 'post', 'title': src['title'], 'slug': {'_type': 'slug', 'current': slug},
    'publishedAt': src.get('publishedAt') or datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
    'excerpt': src['excerpt'][:160], 'seoTitle': src['seoTitle'][:60], 'author': src.get('author', 'Kverneriet'), 'body': md2pt.convert(md),
}
if image:
    doc['mainImage'] = {'_type': 'photo', '_sanityAsset': 'image@file://' + os.path.abspath(image.lstrip('/')), 'alt': src.get('imageAlt', src['title'])}
    # bilder må gå via dataset import (documents create støtter ikke _sanityAsset)
    nd = f'/tmp/post-{slug}.ndjson'; open(nd, 'w', encoding='utf-8').write(json.dumps(doc, ensure_ascii=False) + '\n')
    r = subprocess.run(['npx', 'sanity', 'dataset', 'import', nd, 'production', '--replace'], cwd='studio-kverneriet', capture_output=True, text=True)
else:
    jf = f'/tmp/post-{slug}.json'; json.dump(doc, open(jf, 'w', encoding='utf-8'), ensure_ascii=False)
    r = subprocess.run(['npx', 'sanity', 'documents', 'create', jf, '--replace'], cwd='studio-kverneriet', capture_output=True, text=True)
print((r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else 'ok', '→', f'https://kverneriet.com/blogg/{slug}/')
