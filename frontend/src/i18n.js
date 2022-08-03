// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Vue from "vue"
import VueI18n from "vue-i18n"
import { en, da } from "vuejs-datepicker/dist/locale"

Vue.use(VueI18n)

function loadLocaleMessages() {
  const messages = {}

  // Match on "./locales/da/shared.json", "./locales/en/tabs.json", etc.
  const locales = require.context("./locales", true, /(\w+)\/(\w+)\.json/i)

  locales.keys().forEach((key) => {
    const matched = key.match(/(\w+)\/(\w+)\.json/i)
    if (matched && matched.length > 2) {
      const locale = matched[1] // = 'da', 'en', etc.
      const section = matched[2] // = 'shared', 'tabs', etc.

      // Add the JSON contents under its locale and section
      if (!(locale in messages)) {
        messages[locale] = {}
      }
      messages[locale][section] = locales(key)
    }
  })

  return messages
}

const i18n = new VueI18n({
  locale: localStorage.moLocale || process.env.VUE_APP_I18N_LOCALE || "da",
  fallbackLocale: process.env.VUE_APP_I18N_FALLBACK_LOCALE || "da",
  messages: loadLocaleMessages(),
})
export default i18n

export function getDatepickerLocales() {
  return {
    en: en,
    da: da,
  }
}

const translation_prefix = "i18n:"
const translation_prefix_length = translation_prefix.length

/**
 * Test whether a string should be translated
 * @param {String} value - some string
 * @returns {boolean} whether the value contains the translation_prefix, and
 * as such should be translated
 */
export function has_translation_prefix(value) {
  return value.substring(0, translation_prefix_length) === translation_prefix
}

/**
 * Translate a prefixed string
 * @param {String} translation_table - the lookup table used for translation
 * @param {String} value - a string with a proper prefix followed by a key used to lookup in table
 * @returns {String} the translation
 */
export function translate_prefixed(translation_table, value) {
  return i18n.t(translation_table + "." + value.slice(translation_prefix_length))
}
