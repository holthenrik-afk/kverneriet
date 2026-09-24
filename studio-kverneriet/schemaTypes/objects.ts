import {defineField, defineType} from 'sanity'

export const DAYS = [
  {title: 'Mandag', value: 'Monday'},
  {title: 'Tirsdag', value: 'Tuesday'},
  {title: 'Onsdag', value: 'Wednesday'},
  {title: 'Torsdag', value: 'Thursday'},
  {title: 'Fredag', value: 'Friday'},
  {title: 'Lørdag', value: 'Saturday'},
  {title: 'Søndag', value: 'Sunday'},
]

const time = (name: string, title: string) =>
  defineField({
    name,
    title,
    type: 'string',
    validation: (r) => r.regex(/^\d{2}:\d{2}$/, {name: 'klokkeslett', invert: false}).error('Skriv som 11:30'),
  })

export const kitchenHours = defineType({
  name: 'kitchenHours',
  title: 'Kjøkkentid',
  type: 'object',
  fields: [
    defineField({name: 'days', title: 'Dager', type: 'array', of: [{type: 'string'}], options: {list: DAYS}, validation: (r) => r.min(1)}),
    time('opens', 'Åpner'),
    time('closes', 'Stenger'),
  ],
  preview: {
    select: {days: 'days', opens: 'opens', closes: 'closes'},
    prepare: ({days, opens, closes}) => ({title: `${(days || []).map((d: string) => DAYS.find((x) => x.value === d)?.title).join(', ')}`, subtitle: `${opens}–${closes}`}),
  },
})

export const barHours = defineType({
  name: 'barHours',
  title: 'Bartid',
  type: 'object',
  fields: [
    defineField({name: 'days', title: 'Dager', type: 'array', of: [{type: 'string'}], options: {list: DAYS}, validation: (r) => r.min(1)}),
    time('closes', 'Stenger'),
  ],
  preview: {
    select: {days: 'days', closes: 'closes'},
    prepare: ({days, closes}) => ({title: `${(days || []).map((d: string) => DAYS.find((x) => x.value === d)?.title).join(', ')}`, subtitle: `til ${closes}`}),
  },
})

export const localizedText = defineType({
  name: 'localizedText',
  title: 'Tekst (norsk + engelsk)',
  type: 'object',
  fields: [
    defineField({name: 'no', title: 'Norsk', type: 'text', rows: 4, validation: (r) => r.required()}),
    defineField({name: 'en', title: 'Engelsk', type: 'text', rows: 4}),
  ],
})

export const localizedString = defineType({
  name: 'localizedString',
  title: 'Kort tekst (norsk + engelsk)',
  type: 'object',
  fields: [
    defineField({name: 'no', title: 'Norsk', type: 'string', validation: (r) => r.required()}),
    defineField({name: 'en', title: 'Engelsk', type: 'string'}),
  ],
})

export const photo = defineType({
  name: 'photo',
  title: 'Bilde',
  type: 'image',
  options: {hotspot: true},
  fields: [
    defineField({name: 'alt', title: 'Alt-tekst (beskriv hva bildet viser)', type: 'string', validation: (r) => r.required()}),
  ],
})

export const menuItem = defineType({
  name: 'menuItem',
  title: 'Rett',
  type: 'object',
  fields: [
    defineField({name: 'name', title: 'Navn', type: 'string', validation: (r) => r.required()}),
    defineField({name: 'price', title: 'Pris', type: 'string', description: 'Som på menyen, f.eks. «269.-» eller «190/295.-»', validation: (r) => r.required()}),
    defineField({name: 'description', title: 'Beskrivelse', type: 'text', rows: 3}),
    defineField({name: 'emphasis', title: 'Uthevet tillegg', type: 'string', description: 'F.eks. «Add a piece +45.»'}),
    defineField({name: 'quote', title: 'Sitat (valgfritt)', type: 'string'}),
    defineField({name: 'allergens', title: 'Allergener', type: 'array', of: [{type: 'string'}], options: {layout: 'tags'}, description: 'Koder fra allergen-nøkkelen, f.eks. E, H, M'}),
    defineField({name: 'maybeAllergens', title: 'Kan inneholde', type: 'array', of: [{type: 'string'}], options: {layout: 'tags'}}),
  ],
  preview: {select: {title: 'name', subtitle: 'price'}},
})

export const menuAddon = defineType({
  name: 'menuAddon',
  title: 'Tillegg / dip',
  type: 'object',
  fields: [
    defineField({name: 'name', title: 'Navn', type: 'string', validation: (r) => r.required()}),
    defineField({name: 'note', title: 'Merknad', type: 'string'}),
    defineField({name: 'delta', title: 'Pris', type: 'string', description: '«+39.-», «35.-» eller «free»'}),
    defineField({name: 'allergens', title: 'Allergener', type: 'array', of: [{type: 'string'}], options: {layout: 'tags'}}),
  ],
  preview: {select: {title: 'name', subtitle: 'delta'}},
})

export const menuSection = defineType({
  name: 'menuSection',
  title: 'Menyseksjon',
  type: 'object',
  fields: [
    defineField({name: 'id', title: 'Ankernavn', type: 'slug', description: 'Brukes i lenker, f.eks. burgers', options: {source: 'title'}, validation: (r) => r.required()}),
    defineField({name: 'title', title: 'Tittel', type: 'string', validation: (r) => r.required()}),
    defineField({name: 'intro', title: 'Innledning', type: 'text', rows: 2}),
    defineField({name: 'items', title: 'Retter', type: 'array', of: [{type: 'menuItem'}]}),
    defineField({name: 'upgradesTitle', title: 'Tittel på tillegg', type: 'string', description: 'F.eks. «Upgrades & Extras»'}),
    defineField({name: 'upgrades', title: 'Tillegg', type: 'array', of: [{type: 'menuAddon'}]}),
    defineField({name: 'dipsTitle', title: 'Tittel på dipper', type: 'string'}),
    defineField({name: 'dips', title: 'Dipper', type: 'array', of: [{type: 'menuAddon'}]}),
  ],
  preview: {select: {title: 'title', items: 'items'}, prepare: ({title, items}) => ({title, subtitle: `${(items || []).length} retter`})},
})

export const packageItem = defineType({
  name: 'packageItem',
  title: 'Matpakke',
  type: 'object',
  fields: [
    defineField({name: 'name', title: 'Navn', type: 'string', validation: (r) => r.required()}),
    defineField({name: 'price', title: 'Pris per person (kr)', type: 'number', validation: (r) => r.required()}),
    defineField({name: 'desc', title: 'Innhold', type: 'text', rows: 3}),
  ],
  preview: {select: {title: 'name', price: 'price'}, prepare: ({title, price}) => ({title, subtitle: `${price} kr`})},
})

export const allergenCode = defineType({
  name: 'allergenCode',
  title: 'Allergenkode',
  type: 'object',
  fields: [
    defineField({name: 'code', title: 'Kode', type: 'string', validation: (r) => r.required()}),
    defineField({name: 'name', title: 'Betydning', type: 'string', validation: (r) => r.required()}),
  ],
  preview: {select: {title: 'code', subtitle: 'name'}},
})

export const craftItem = defineType({
  name: 'craftItem',
  title: 'Håndverkskort',
  type: 'object',
  fields: [
    defineField({name: 'title', title: 'Tittel', type: 'localizedString', validation: (r) => r.required()}),
    defineField({name: 'body', title: 'Tekst', type: 'localizedText', validation: (r) => r.required()}),
    defineField({name: 'photo', title: 'Bilde', type: 'photo'}),
  ],
  preview: {select: {title: 'title.no', media: 'photo'}},
})

export const fact = defineType({
  name: 'fact',
  title: 'Faktapunkt',
  type: 'object',
  fields: [
    defineField({name: 'label', title: 'Etikett', type: 'string', validation: (r) => r.required()}),
    defineField({name: 'text', title: 'Tekst', type: 'string', validation: (r) => r.required()}),
    defineField({name: 'href', title: 'Lenke (valgfritt)', type: 'string'}),
  ],
  preview: {select: {title: 'label', subtitle: 'text'}},
})

export const richText = defineType({
  name: 'richText',
  title: 'Tekst',
  type: 'array',
  of: [
    {
      type: 'block',
      styles: [
        {title: 'Avsnitt', value: 'normal'},
        {title: 'Mellomtittel', value: 'h2'},
        {title: 'Liten tittel', value: 'h3'},
        {title: 'Sitat', value: 'blockquote'},
      ],
      lists: [{title: 'Punktliste', value: 'bullet'}, {title: 'Nummerert', value: 'number'}],
      marks: {
        decorators: [{title: 'Fet', value: 'strong'}, {title: 'Kursiv', value: 'em'}],
        annotations: [
          {
            name: 'link',
            title: 'Lenke',
            type: 'object',
            fields: [defineField({name: 'href', title: 'URL', type: 'url', validation: (r) => r.uri({scheme: ['http', 'https', 'mailto', 'tel'], allowRelative: true})})],
          },
        ],
      },
    },
    {type: 'photo'},
  ],
})
