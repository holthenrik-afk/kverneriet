import {defineConfig} from 'sanity'
import {structureTool} from 'sanity/structure'
import {visionTool} from '@sanity/vision'
import {schemaTypes} from './schemaTypes'
import {SITE_TEXT_AREAS} from './schemaTypes/documents'
import {PostPreview} from './preview/PostPreview'

// Studio for kverneriet.com. Innholdet her bygges til statiske sider av tools/fetch_sanity.py + tools/build.py.
export default defineConfig({
  name: 'default',
  title: 'Kverneriet',
  projectId: 'u0hod2sg',
  dataset: 'production',
  plugins: [
    structureTool({
      // Blogginnlegg får en «Forhåndsvisning»-fane ved siden av skjemaet. Nettsiden er statisk
      // og kan ikke vise utkast, så Studioet tegner innlegget selv. Se preview/postHtml.ts.
      defaultDocumentNode: (S, {schemaType}) =>
        schemaType === 'post'
          ? S.document().views([S.view.form().title('Rediger'), S.view.component(PostPreview).title('Forhåndsvisning')])
          : S.document(),
      structure: (S) =>
        S.list()
          .title('Innhold')
          .items([
            S.listItem().title('Tekster på nettsiden').child(
              S.list()
                .title('Tekster på nettsiden')
                .items([
                  S.listItem().title('Endrede tekster').child(
                    S.documentTypeList('siteText').title('Endrede tekster').filter('_type == "siteText" && (defined(no) || defined(en))').initialValueTemplates([]),
                  ),
                  S.divider(),
                  ...SITE_TEXT_AREAS.map((omrade) =>
                    S.listItem().title(omrade).child(
                      S.documentTypeList('siteText')
                        .title(omrade)
                        .filter('_type == "siteText" && omrade == $omrade')
                        .params({omrade})
                        .defaultOrdering([{field: 'rekkefolge', direction: 'asc'}])
                        .initialValueTemplates([]),
                    ),
                  ),
                ]),
            ),
            S.divider(),
            S.listItem().title('Restauranter').child(S.documentTypeList('venue').title('Restauranter')),
            S.listItem().title('Menyer').child(S.documentTypeList('menu').title('Menyer')),
            S.divider(),
            S.listItem().title('Blogg').child(S.documentTypeList('post').title('Blogginnlegg').defaultOrdering([{field: 'publishedAt', direction: 'desc'}])),
            S.listItem().title('Presseomtaler').child(S.documentTypeList('pressItem').title('Presseomtaler').defaultOrdering([{field: 'order', direction: 'asc'}])),
            S.listItem().title('Spørsmål og svar').child(S.documentTypeList('faqItem').title('Spørsmål og svar')),
            S.listItem().title('Landingssider').child(S.documentTypeList('landingPage').title('Landingssider')),
            S.divider(),
            S.listItem().title('Innstillinger').id('siteSettings').child(S.document().schemaType('siteSettings').documentId('siteSettings')),
          ]),
    }),
    visionTool(),
  ],
  schema: {
    types: schemaTypes,
    templates: (prev) => prev.filter((t) => !['siteSettings', 'siteText'].includes(t.schemaType)),
  },
  document: {
    actions: (prev, {schemaType}) => (['siteSettings', 'siteText'].includes(schemaType) ? prev.filter((a) => !['unpublish', 'delete', 'duplicate'].includes(a.action || '')) : prev),
  },
})
