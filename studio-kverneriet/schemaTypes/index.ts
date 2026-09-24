import {allergenCode, barHours, craftItem, fact, kitchenHours, localizedString, localizedText, menuAddon, menuItem, menuSection, packageItem, photo, richText} from './objects'
import {faqItem, landingPage, menu, post, pressItem, siteSettings, venue} from './documents'

export const schemaTypes = [
  // objekter
  kitchenHours, barHours, localizedText, localizedString, photo, menuItem, menuAddon, menuSection, packageItem, allergenCode, craftItem, fact, richText,
  // dokumenter
  siteSettings, venue, menu, pressItem, faqItem, post, landingPage,
]
