// Gjør et blogginnlegg fra Sanity om til samme HTML som nettsiden lager.
//
// Nettsiden er statisk: tools/build_blog.py bygger sidene i GitHub av *publisert* innhold,
// så det finnes ingen server som kan vise et utkast. Sanitys «Presentation»-visning krever
// nettopp det. I stedet tegner Studioet innlegget selv, med nettsidens eget stilark.
//
// ptToHtml() er en linje-for-linje-kopi av tools/portable.py, og postHtml() av post_page()
// i tools/build_blog.py. Endres en av dem, må denne endres likt – ellers viser
// forhåndsvisningen noe annet enn det som blir publisert. preview/parity.test.ts sjekker det.

const PROJECT = 'u0hod2sg'
const DATASET = 'production'
const MONTHS = ['januar', 'februar', 'mars', 'april', 'mai', 'juni', 'juli', 'august', 'september', 'oktober', 'november', 'desember']

// Python: html.escape(s, quote=False)
const esc = (s: string): string => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
// Python: html.escape(s, quote=True)
const escAttr = (s: string): string => esc(s).replace(/"/g, '&quot;').replace(/'/g, '&#x27;')

type Img = {url: string; w: number; h: number}

// Et utkast har bare en referanse til bildet, ikke URL-en som fetch_sanity.py henter.
// Referansen inneholder alt som trengs: image-<id>-<bredde>x<høyde>-<format>.
export function imageFromRef(ref: string | undefined): Img | null {
  const m = /^image-([A-Za-z0-9]+)-(\d+)x(\d+)-(\w+)$/.exec(ref || '')
  if (!m) return null
  return {url: `https://cdn.sanity.io/images/${PROJECT}/${DATASET}/${m[1]}-${m[2]}x${m[3]}.${m[4]}`, w: +m[2], h: +m[3]}
}

function spans(block: any): string {
  const defs: Record<string, any> = {}
  for (const d of block.markDefs || []) defs[d._key] = d
  let out = ''
  for (const ch of block.children || []) {
    let t = esc(ch.text || '').replace(/\n/g, '<br>')
    for (const m of ch.marks || []) {
      if (m === 'strong') t = `<strong>${t}</strong>`
      else if (m === 'em') t = `<em>${t}</em>`
      else if (defs[m] && defs[m]._type === 'link') {
        const href = 'href' in defs[m] ? defs[m].href : '#'
        const ext = href.startsWith('http') && !href.includes('kverneriet.com')
        t = `<a href="${escAttr(href)}"${ext ? ' target="_blank" rel="noopener"' : ''}>${t}</a>`
      }
    }
    out += t
  }
  return out
}

function faqHtml(items: [string, string][]): string {
  const rows = items
    .map(([q, a]) => `<details class="faq__item"><summary><h3 class="faq__q">${q}</h3></summary><div class="faq__a"><p>${a}</p></div></details>`)
    .join('')
  return `<section class="faq-inline" id="faq"><h2 class="display-3">Ofte stilte spørsmål</h2><div class="faq" style="margin-top:var(--space-4)">${rows}</div></section>`
}

export function ptToHtml(input: any[] | undefined, clsP = ''): string {
  const blocks = [...(input || [])]
  // En «Ofte stilte spørsmål»-mellomtittel med ### spørsmål under blir til <details>, som på siden.
  for (let i = 0; i < blocks.length; i++) {
    const b = blocks[i]
    if (b._type === 'block' && b.style === 'h2' && spans(b).trim().toLowerCase().startsWith('ofte stilte')) {
      const items: [string, string][] = []
      let j = i + 1
      while (j < blocks.length && !(blocks[j]._type === 'block' && blocks[j].style === 'h2')) {
        const bj = blocks[j]
        if (bj._type === 'block' && bj.style === 'h3') items.push([spans(bj), ''])
        else if (bj._type === 'block' && items.length) items[items.length - 1][1] = (items[items.length - 1][1] + ' ' + spans(bj)).trim()
        j++
      }
      if (items.length) {
        return ptToHtml(blocks.slice(0, i), clsP) + '\n' + faqHtml(items.filter(([, a]) => a)) + (j < blocks.length ? '\n' + ptToHtml(blocks.slice(j), clsP) : '')
      }
    }
  }
  const out: string[] = []
  let lst: string | null = null
  const close = () => {
    if (lst) {
      out.push(lst === 'bullet' ? '</ul>' : '</ol>')
      lst = null
    }
  }
  for (const b of blocks) {
    if (b._type === 'block') {
      if (b.listItem) {
        if (lst !== b.listItem) {
          close()
          lst = b.listItem
          out.push(lst === 'bullet' ? '<ul>' : '<ol>')
        }
        out.push(`<li>${spans(b)}</li>`)
        continue
      }
      close()
      const st = b.style || 'normal'
      const inner = spans(b)
      if (st === 'h2') out.push(`<h2 class="display-3">${inner}</h2>`)
      else if (st === 'h3') out.push(`<h3 class="display-4">${inner}</h3>`)
      else if (st === 'blockquote') out.push(`<blockquote class="pullquote">${inner}</blockquote>`)
      else out.push(`<p${clsP ? ` class="${clsP}"` : ''}>${inner}</p>`)
    } else if (b._type === 'photo') {
      const img = imageFromRef(b.asset?._ref)
      if (img) {
        close()
        out.push(`<figure class="photo photo--inline"><img src="${escAttr(img.url)}" alt="${escAttr(b.alt || '')}" loading="lazy" width="${img.w}" height="${img.h}"></figure>`)
      }
    }
  }
  close()
  return out.join('\n')
}

export function niceDate(iso: string): string {
  const [y, m, d] = iso.slice(0, 10).split('-').map(Number)
  return `${d}. ${MONTHS[m - 1]} ${y}`
}

// Rammen rundt: stilark og skrifter, tom <body>. Stilarket hentes fra kverneriet.no, så
// forhåndsvisningen følger med når nettsidens utseende endres. Studioet lager rammen én gang
// og bytter bare innholdet i <body> mens du skriver, så siden ikke hopper til toppen.
export function postShell(body = ''): string {
  const dag = new Date().toISOString().slice(0, 10).replace(/-/g, '')
  return `<!DOCTYPE html>
<html lang="nb">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<base target="_blank">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,500;0,600;1,400&family=Barlow+Condensed:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="https://kverneriet.no/kverneriet.css?forhandsvisning=${dag}">
<style>.post__knapper a{pointer-events:none}</style>
</head>
<body>${body}</body>
</html>`
}

// Selve innleggssiden, uten toppmeny og bunnlinje.
export function postBody(doc: any): string {
  const title = doc?.title || 'Uten tittel'
  const img = imageFromRef(doc?.mainImage?.asset?._ref)
  const hero = img
    ? `<figure class="photo post__hero" style="aspect-ratio:16/9;margin-top:var(--space-6)"><img src="${escAttr(img.url)}" alt="${escAttr(doc.mainImage.alt || '')}" fetchpriority="high" width="${img.w}" height="${img.h}"></figure>`
    : ''
  const author = doc?.author ? ` · ${escAttr(doc.author)}` : ''
  const dato = doc?.publishedAt
    ? `<time datetime="${escAttr(doc.publishedAt.slice(0, 10))}">${niceDate(doc.publishedAt)}</time>`
    : '<time>Dato ikke satt</time>'
  const lede = doc?.excerpt ? `<p class="lede" style="margin-top:var(--space-4)">${escAttr(doc.excerpt)}</p>` : ''

  return `<main id="main">
  <article class="wrap wrap--narrow post" style="padding-top:var(--space-8);padding-bottom:var(--section-y)">
    <nav class="crumbs" aria-label="Brødsmuler"><ol><li><a href="https://kverneriet.no/">Kverneriet</a></li><li><a href="https://kverneriet.no/blogg/">Blogg</a></li><li><span aria-current="page">${escAttr(title)}</span></li></ol></nav>
    <header class="sec-head">
      <div class="sec-head__rule"></div>
      <span class="kv-eyebrow">${dato}${author}</span>
      <h1 class="display-1">${escAttr(title)}</h1>
      ${lede}
    </header>
    ${hero}
    <div class="post__body">
${ptToHtml(doc?.body)}
    </div>
    <div class="post__knapper" style="margin-top:var(--space-8);display:flex;gap:10px;flex-wrap:wrap">
      <a class="btn btn--outline btn--md" href="https://kverneriet.no/blogg/"><span class="btn__glyph" aria-hidden="true">«</span> <span>Alle innlegg</span></a>
      <a class="btn btn--primary btn--md" href="https://kverneriet.no/majorstua/#booking">Book bord</a>
    </div>
  </article>
</main>`
}

// Hele siden i ett, til testing og til å åpne i en vanlig nettleser.
export const postHtml = (doc: any): string => postShell(postBody(doc))
