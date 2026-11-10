// Legger «Endrede åpningstider» (jul, påske) fra ../content/venues.json (hours.special) inn i Sanity.
//
// Kjør fra studio-kverneriet/:  npx sanity exec scripts/endrede-tider.ts --with-user-token
// Prøvekjøring uten å skrive:   TORR=1 npx sanity exec scripts/endrede-tider.ts --with-user-token
//
// Sanity er kilden: bygget på GitHub henter specialHours derfra og skriver venues.json på nytt.
// Skriptet skriver bare feltet specialHours, og bare der det er tomt i Sanity. Har noen lagt inn
// tider i Studio, røres de ikke, med mindre du kjører med OVERSKRIV=1.
import {readFileSync} from 'node:fs'
import {resolve} from 'node:path'
import {getCliClient} from 'sanity/cli'

const client = getCliClient({apiVersion: '2025-02-19'})
const TORR = Boolean(process.env.TORR)
const OVERSKRIV = Boolean(process.env.OVERSKRIV)

type Rad = {from: string; to?: string; closed?: boolean; opens?: string; closes?: string; barCloses?: string}
const venues: {slug: string; hours: {special?: Rad[]}}[] = JSON.parse(
  readFileSync(resolve(process.cwd(), '../content/venues.json'), 'utf-8'),
).venues

const tilSanity = (r: Rad, i: number) => ({
  _key: `s${r.from.replaceAll('-', '')}${i}`,
  _type: 'specialHours',
  from: r.from,
  ...(r.to && r.to !== r.from ? {to: r.to} : {}),
  ...(r.closed ? {closed: true} : {closed: false, opens: r.opens, closes: r.closes, ...(r.barCloses ? {barCloses: r.barCloses} : {})}),
})
const likt = (a: Rad[] = [], b: Rad[] = []) => {
  const n = (x: Rad[]) => JSON.stringify(x.map((r) => [r.from, r.to && r.to !== r.from ? r.to : r.from, Boolean(r.closed), r.closed ? '' : r.opens, r.closed ? '' : r.closes, r.closed ? '' : r.barCloses || '']))
  return n(a) === n(b)
}

let endret = 0
for (const v of venues) {
  const id = `venue-${v.slug}`
  const lokal = v.hours.special || []
  const doc = await client.getDocument(id)
  if (!doc) throw new Error(`fant ikke ${id} i Sanity`)
  const iSanity = (doc.specialHours as Rad[] | undefined) || []
  if (likt(iSanity, lokal)) {
    console.log(`${id}: likt, ingenting å gjøre`)
    continue
  }
  if (iSanity.length && !OVERSKRIV) {
    console.log(`${id}: har allerede ${iSanity.length} rader i Sanity som er ulike de lokale. Hopper over (OVERSKRIV=1 for å bytte).`)
    continue
  }
  console.log(`${id}: ${TORR ? 'ville skrevet' : 'skriver'} ${lokal.length} rader: ${lokal.map((r) => `${r.from}${r.to && r.to !== r.from ? '–' + r.to : ''} ${r.closed ? 'stengt' : `${r.opens}–${r.closes}`}`).join(', ')}`)
  if (!TORR) await client.patch(id).set({specialHours: lokal.map(tilSanity)}).commit()
  endret++
}
console.log(`${TORR ? 'Prøvekjøring: ' : ''}${endret} restauranter ${TORR ? 'ville fått' : 'fikk'} nye endrede åpningstider.`)
