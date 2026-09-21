# Kverneriet — nettside

High-end statisk nettside for Kverneriet, bygget på «Kverneriet Design System» (tokens, fonter og logo ligger i `tokens/` og `assets/`, kopiert fra designsystem-zip-en). Alt innhold er norsk som standard med engelsk via språkvelgeren.

## Bygg og kjør

```bash
python3 tools/build.py
python3 -m http.server 4173
```

`tools/build.py` genererer alle sider fra innholdslaget og skriver `<head>`, sitemap, llms.txt, robots, `_redirects`, responsive bilder, én CSS-fil (`kverneriet.css`) og cache-versjoner. Kjør den etter **enhver** endring i `content/`, `tools/`, `site.css` eller `site.js`. Sidene `index.html` og `takeaway/index.html` er håndskrevne, men header/footer/modal/FAQ/om-tekst settes inn av bygget.

## URL-struktur (samme som kverneriet.com i dag)

| Adresse | Fil | Kilde |
| --- | --- | --- |
| `/` | `index.html` | håndskrevet + `tools/build.py` |
| `/majorstua/`, `/solli/`, `/tonsberg/` | `<slug>/index.html` | `tools/build_venue.py` fra `content/venues.json` |
| `/majorstua/menu/`, `/solli/menu/`, `/tonsberg/menu/` | `<slug>/menu/index.html` | `tools/build_menu.py` fra `content/menus.js` (forhåndsrendret meny) |
| `/meny/` | `meny/index.html` | `tools/build_menu.py` (velg restaurant) |
| `/takeaway/` | `takeaway/index.html` | håndskrevet + `tools/build.py` |
| `/lunsj/`, `/julebord/`, `/selskap/`, `/late-night/` | `<slug>/index.html` | `tools/build_landing.py` |

Strukturen ble lagt om 16.09.2026 for at ingen adresser kverneriet.com rangerer på i dag (`/majorstua/`, `/solli/menu/` osv.) skal gå tapt ved lansering. Gamle adresser (`.html`, `/packages/`, `/giftcard/`) viderekobles på to måter: `_redirects` for Netlify/Cloudflare Pages, og HTML-stubber med meta refresh + canonical for GitHub Pages og andre verter uten viderekobling på serveren. Begge genereres fra samme tabell i `tools/seo_head.py`.

## Hosting på GitHub Pages

Repoet er klart for GitHub Pages: `.nojekyll` (ingen Jekyll-behandling), `CNAME` (kverneriet.com), `404.html`, HTML-stubber på de gamle adressene (`majorstua.html`, `/packages/`, `/giftcard/` …) og en workflow i `.github/workflows/pages.yml` som publiserer alt unntatt `tools/` og README ved hvert push til `main`.

1. Lag et tomt repo på GitHub (privat eller offentlig) og push:
   ```bash
   git remote add origin git@github.com:<bruker>/kverneriet-site.git
   git push -u origin main
   ```
2. I repoet: **Settings → Pages → Build and deployment → Source: GitHub Actions**. Workflowen kjører ved neste push (eller «Run workflow»).
3. Siden bruker rot-relative stier (`/assets/…`). Workflowen kjører `tools/rebase.py` med `base_path` fra `actions/configure-pages`, så den virker både som forhåndsvisning på `<bruker>.github.io/kverneriet/` og på roten av kverneriet.com når domenet er satt.
4. **Domene:** i **Settings → Pages → Custom domain** skriv `kverneriet.com`. Hos domeneleverandøren: fire A-poster for `kverneriet.com` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`, og en CNAME for `www` → `<bruker>.github.io`. Huk av «Enforce HTTPS» når DNS har slått gjennom.
5. Etter lansering: meld inn `https://kverneriet.com/sitemap.xml` i Search Console og test en restaurantside på search.google.com/test/rich-results.

Bygg alltid lokalt før push (`python3 tools/build.py`) – Actions bygger ikke, den kopierer bare. Filer over 100 MB avvises av GitHub; de største her er PDF-ene på ~4 MB.

## Sanity (kunden redigerer selv)

Innholdet redigeres i **https://kverneriet.sanity.studio** (Sanity-prosjekt `u0hod2sg`, datasett `production`, kildekode i `studio-kverneriet/`). Typene er på norsk: Restauranter, Menyer, Blogg, Presseomtaler, Spørsmål og svar, Landingssider og Innstillinger.

Slik henger det sammen:

1. Redaktøren trykker **Publish** i Studio.
2. `tools/fetch_sanity.py` henter innholdet (offentlig lesetilgang, ingen nøkkel) og skriver `content/venues.json`, `content/menus.js`, `content/press.json`, `content/landing.json`, `content/site-copy.json` og `content/blog.json`.
3. `tools/build.py` bygger sidene som før. Bilder lastet opp i Sanity serveres fra Sanitys CDN med `srcset` (`?w=…&auto=format`), lokale bilder går gjennom `tools/images.py` som før.
4. GitHub Actions kjører 2–3 ved push, hvert 10. minutt (`schedule`), manuelt (`gh workflow run pages.yml`), og ved webhook fra Sanity (`repository_dispatch`, type `sanity-publish`).

**Webhook (valgfritt, gir oppdatering innen et par minutter i stedet for innen ti):** i sanity.io/manage → API → Webhooks: URL `https://api.github.com/repos/holthenrik-afk/kverneriet/dispatches`, metode POST, header `Authorization: Bearer <GitHub-token med repo-tilgang>` og `Accept: application/vnd.github+json`, body `{"event_type":"sanity-publish"}`, trigger på create/update/delete.

**Gi kunden tilgang:** sanity.io/manage → prosjektet → Members → inviter e-post med rollen Editor. De logger inn på kverneriet.sanity.studio med Google eller e-post.

**Lokalt:** `cd studio-kverneriet && npm run dev` åpner Studio på localhost:3333. `npx sanity deploy` publiserer ny Studio-versjon (etter endringer i `schemaTypes/`). Første innlasting av dagens innhold ble gjort med `tools/sanity_seed.py` + `sanity dataset import` (21.09.2026); scriptet kan kjøres igjen med `--replace` for å nullstille.

**Bloggen:** innlegg av typen «Blogginnlegg» bygges til `/blogg/` og `/blogg/<slug>/` med BlogPosting-markup. Lenken «Blogg» i meny og footer vises først når det finnes minst ett publisert innlegg.

## Innholdslaget («CMS»)

- **`content/venues.json`** – skrives av `fetch_sanity.py` (rediger i Sanity, ikke her). Én kilde for restaurantfakta: adresse, telefon, e-post, geo, kart-lenker, Facebook, Zenchef-id, kjøkken- og bartider, lunsjtider, bestillingskanaler, PDF-menyer, matpakker og priser. Brukes av restaurantsidene, footeren (NAP på alle sider), landingssidene, FAQ, JSON-LD og llms.txt. Hentet fra kverneriet.com 16.09.2026.
- **`content/menus.js`** – menyene, skrives av `fetch_sanity.py` fra Sanity (opprinnelig importert ordrett fra kverneriet.com med `tools/import-menus.py`). Allergen-nøkkelen leses fra kjøkkenets egne koder (SN = sennep, SY = soya, S = sulfitt, SD = skalldyr osv.).
- **`content/i18n.js`** – håndskrevne UI-tekster (no + en). **`content/i18n-gen.js`** genereres av bygget (om-tekster, FAQ, åpningstider, skjema-tekster) – ikke rediger den.
- **`tools/pages.py`** – titler, meta-beskrivelser og delingsbilde per side (tittel ≤ 60, beskrivelse ≤ 155 tegn, sjekkes ved bygging).
- **`content/press.json`** – presseomtalene (fra Sanity); `tools/media.py` lager kort, logostripe og Review/NewsArticle i JSON-LD fra samme liste. `content/landing.json` og `content/site-copy.json` – tekstene på landingssidene og forsiden, også fra Sanity.

## Booking

«Book bord» åpner modalen på alle sider. Øverst velger du restaurant; valget styrer både booking og take-away-fanen. **Online booking** viser Kverneriets Zenchef-widget (samme løsning som kverneriet.com bruker i dag, restaurant-id i `venues.json`) i en ramme inne i modalen – ekte booking med bekreftelse, uten å forlate siden. **Større grupper** (over 8, 7 i Tønsberg) fyller ut forespørselen; siden nettstedet er statisk uten backend, åpnes e-postprogrammet med forespørselen ferdig utfylt til restaurantens bookingadresse (`book.major@`, `book.solli@`, `book.tbg@`). Skal forespørselen gå rett til et system, bytt `mailto:`-delen i `site.js` (`wireBooking`) mot et POST-kall. Hver restaurantside har samme skjema i `#booking`, med en vanlig lenke til Zenchef som fallback uten JavaScript.

## SEO og AEO (svarmotorer)

Gjennomgått 16.09.2026 (152 agenter, 113 funn verifisert). Det som er på plass:

- **Adresser bevart** fra dagens kverneriet.com, `_redirects` for resten, `sitemap.xml` generert fra sideregisteret.
- **Menyen ligger i HTML-en** (ikke bare JavaScript) på egne adresser per restaurant, med priser, allergener og Menu-markup. `meny.js` er kun en reserve.
- **Restaurant-JSON-LD** per restaurant med adresse, geo, kart, E.164-telefon, åpningstider (åpner med kjøkkenet, stenger med baren), ReserveAction mot Zenchef, hasMenu, sameAs (Facebook, Wolt, Foodora) og presseomtaler – nøyaktig de som vises på siden (Dagbladet 2020 6/6 ligger på Solli, der testen ble gjort). Organization/WebSite med @id, BreadcrumbList på undersider, FAQPage speilet fra de synlige spørsmålene. Ingen aggregateRating (presseterninger gir ikke stjerner i Google uansett).
- **Synlig NAP** i footeren på alle sider og i praktisk-seksjonen på hver restaurantside; åpningstider på norsk («til 23.00», ikke «to»).
- **FAQ** på alle sider med sanne svar fra datalaget (hvor, åpningstider, booking, take-away, barnemeny, glutenfrie fries, priser, veibeskrivelse).
- **`llms.txt`** med restaurantfakta, adresser, meny-lenker, booking-lenker og pakker; `robots.txt` slipper GPTBot, ClaudeBot, PerplexityBot og Google-Extended inn.
- **Titler/beskrivelser** innenfor visningsgrensene med «burger» + sted på alle 13 sider; H1 med restaurantnavn; landingssider med sted og produkt i overskrifter, norsk late night-vokabular og lenker til restaurantene.
- **Ytelse:** responsive bilder (`<picture>` med WebP, srcset 480–2000 px, width/height mot layout-hopp, `fetchpriority="high"` på hero), én CSS-fil i stedet for ti i kjede, Google Fonts lastet riktig (den gamle `@import`-en lå etter `@font-face` og ble ignorert), Bourton forhåndslastet, Dagbladet-terningen 55 KB.
- **Ikoner:** `favicon.ico`, SVG-ikon, apple-touch-icon og `site.webmanifest` (generert fra logomerket, `assets/icons/`).
- **Sporing:** alle CTA-er og utgående bestillingslenker har `data-track="handling:sted:kanal"` → `window.dataLayer` (`kv_click`). OrderX-lenkene har UTM. Lim inn GTM-containeren i `<head>` (via `tools/seo_head.py`) når kontoen er klar.

### Fortsatt åpent
- **Engelsk versjon** finnes bare klientside (localStorage) og indekseres ikke. Enten aksepter norsk-only, eller generer `/en/`-sider fra ordbøkene med hreflang.
- **Gruppeforespørsel** går via `mailto:` til backend finnes. Zenchef-avtalen dekker online booking.
- **Google Business Profile**-lenker (delingslenker per restaurant) og Instagram-profil bør inn i `venues.json` (`sameAs`) når de foreligger.
- Fasiliteter (høystoler, rullestol, parkering, hund) er bevisst ikke påstått – legg inn i FAQ når Kverneriet bekrefter.
- Validér på search.google.com/test/rich-results og meld inn `sitemap.xml` i Search Console ved lansering.

## Struktur

- `styles.css` + `tokens/` – designsystemets kilde (ett bevisst avvik: brødtekst Montserrat i stedet for Newsreader). `site.css` – sidelaget. Bygget slår dem sammen til `kverneriet.css`.
- `site.js` – språk, sporing, modal, booking (Zenchef-ramme + mailto), mobilmeny, scrollspy. `meny.js` – reserve-rendrer for menysidene.
- `assets/img/` – originalfoto fra Dropbox-arkivet; `assets/img/r/` – genererte varianter (kan slettes og bygges på nytt). Piknikserien har et barn på bildene: `ta-hero.jpg`, `craft-pack.jpg` og `ta-press-boxes.jpg` er fysisk beskåret uten barnet – ikke bytt tilbake til originalene.
- `assets/press/` – avislogoer (SVG-masker, PNG for Tønsbergs Blad og Mer av Oslo), Dagbladets terning (ekte, 256 px).
- `tools/press-confirmed-2026-09-15.json` – de 90 verifiserte omtalene (rådata for `media.py`).
- `tools/bundle*.py` – pakker sider til selvstendig HTML for Figma-import (html.to.design).

## Designsystem-regler

Bourton kun til display/uppercase, korall kun på handlinger, maks én mørk (teal) seksjon per side, Barlow Condensed til etiketter.
