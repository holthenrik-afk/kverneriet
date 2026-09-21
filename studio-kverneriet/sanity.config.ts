import {defineConfig} from 'sanity'
import {structureTool} from 'sanity/structure'
import {visionTool} from '@sanity/vision'
import {schemaTypes} from './schemaTypes'

// Studio for kverneriet.com. Innholdet her bygges til statiske sider av tools/fetch_sanity.py + tools/build.py.
export default defineConfig({
  name: 'default',
  title: 'Kverneriet',
  projectId: 'u0hod2sg',
  dataset: 'production',
  plugins: [
    structureTool({
      structure: (S) =>
        S.list()
          .title('Innhold')
          .items([
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
    templates: (prev) => prev.filter((t) => !['siteSettings'].includes(t.schemaType)),
  },
  document: {
    actions: (prev, {schemaType}) => (schemaType === 'siteSettings' ? prev.filter((a) => !['unpublish', 'delete', 'duplicate'].includes(a.action || '')) : prev),
  },
})
