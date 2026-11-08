// Oppdaterer «Tekster på nettsiden» i Sanity fra ../sanity-tekster.ndjson (laget av tools/sanity_tekster.py).
//
// Kjør fra studio-kverneriet/:  npx sanity exec scripts/sync-tekster.ts --with-user-token
// Prøvekjøring uten å skrive:   TORR=1 npx sanity exec scripts/sync-tekster.ts --with-user-token
//
// Til forskjell fra `dataset import --missing` oppdateres også «Teksten i dag», plassering og område når
// koden endres. Feltene Kverneriet skriver i (no og en), røres aldri. Tekster som ikke lenger finnes på
// nettsiden, slettes hvis ingen har endret dem. Er de endret, blir de liggende under «Annet» med en merknad.
import {readFileSync} from 'node:fs'
import {resolve} from 'node:path'
import {getCliClient} from 'sanity/cli'

const client = getCliClient({apiVersion: '2025-02-19'})
const TORR = Boolean(process.env.TORR)
const FELT = ['key', 'omrade', 'hvor', 'rekkefolge', 'standardNo', 'standardEn', 'fast', 'merknad'] as const

type Tekst = {_id: string; _type: 'siteText'} & Partial<Record<(typeof FELT)[number], unknown>>

const nye: Tekst[] = readFileSync(resolve(process.cwd(), '../sanity-tekster.ndjson'), 'utf-8')
  .split('\n')
  .filter(Boolean)
  .map((l) => JSON.parse(l))
const ider = new Set(nye.map((t) => t._id))

const finnes: {_id: string; no?: string; en?: string}[] = await client.fetch(
  '*[_type == "siteText" && !(_id in path("drafts.**"))]{_id, no, en}',
)

let tx = client.transaction()
let antall = 0
const send = async () => {
  if (!antall) return
  if (!TORR) await tx.commit({visibility: 'async'})
  tx = client.transaction()
  antall = 0
}

for (const t of nye) {
  const sett = Object.fromEntries(FELT.filter((f) => t[f] !== undefined).map((f) => [f, t[f]]))
  const fjern = FELT.filter((f) => t[f] === undefined)
  tx.createIfNotExists({_id: t._id, _type: 'siteText', key: t.key})
  tx.patch(t._id, (p) => (fjern.length ? p.set(sett).unset([...fjern]) : p.set(sett)))
  if (++antall >= 100) await send()
}

let slettet = 0
let merket = 0
for (const d of finnes.filter((d) => !ider.has(d._id))) {
  if (d.no || d.en) {
    tx.patch(d._id, (p) => p.set({omrade: 'Annet', merknad: 'Brukes ikke lenger på nettsiden. Endringen din vises ikke.'}))
    merket++
  } else {
    tx.delete(d._id)
    slettet++
  }
  if (++antall >= 100) await send()
}
await send()

console.log(
  `${TORR ? 'Prøvekjøring: ' : ''}${nye.length} tekster oppdatert eller opprettet, ${slettet} ubrukte slettet, ${merket} ubrukte med endringer merket.`,
)
