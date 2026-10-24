// Brukes av tools/check_preview_parity.py: leser innlegg som JSON på stdin og skriver
// forhåndsvisningens HTML tilbake, så den kan sammenlignes med det nettsiden bygger.
// Kjøres med: node studio-kverneriet/preview/render-cli.ts < innlegg.json
import {imageFromRef, niceDate, ptToHtml} from './postHtml.ts'

let raw = ''
process.stdin.on('data', (c) => (raw += c))
process.stdin.on('end', () => {
  const posts = JSON.parse(raw)
  const out: Record<string, unknown> = {}
  for (const p of posts) {
    out[p._id] = {
      body: ptToHtml(p.body),
      dato: p.publishedAt ? niceDate(p.publishedAt) : null,
      bilder: [p.mainImage, ...(p.body || []).filter((b: any) => b._type === 'photo')]
        .filter(Boolean)
        .map((b: any) => imageFromRef(b.asset?._ref)?.url ?? null),
    }
  }
  process.stdout.write(JSON.stringify(out))
})
