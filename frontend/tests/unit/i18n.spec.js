// SPDX-FileCopyrightText: 2017-2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import i18n from '@/i18n.js'
import { getDatepickerLocales } from '@/i18n.js'

describe('i18n.js:loadLocaleMessages', () => {
  it('should detect "en" and "da" locales', async () => {
    const messages = i18n.messages
    expect(Object.keys(messages)).toEqual(expect.arrayContaining(['da', 'en']))
    expect(Object.keys(messages['da'])).toEqual(Object.keys(messages['en']))
  })

  it('should detect the same i18n keys for all locales', async () => {
    const listAllKeys = function (obj) {
      var keys = []

      const visit = function (obj, prefix) {
        for (const [key, value] of Object.entries(obj)) {
          // If value is itself another object (e.g. a nested dictionary),
          // recurse into it.
          if (typeof value === 'object') {
            visit(value, key)
          }
          keys.push(`${prefix}.${key}`)
        }
      }

      visit(obj, 'root')
      return keys
    }

    const daKeys = listAllKeys(i18n.messages['da'])
    const enKeys = listAllKeys(i18n.messages['en'])
    expect(daKeys).toEqual(expect.arrayContaining(enKeys))
  })
})

describe('i18n.js:getDatepickerLocales', () => {
  it('should load "en" and "da" locales', async () => {
    const locales = getDatepickerLocales()
    expect(Object.keys(locales)).toEqual(expect.arrayContaining(['da', 'en']))
    expect(Object.keys(locales['da'])).toEqual(Object.keys(locales['en']))
  })
})
