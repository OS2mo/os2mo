// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Vue from 'vue'
import VueI18n from 'vue-i18n'
import { da } from './locales/da'

Vue.use(VueI18n)

const messages = {
  da: da,
}

const translation_prefix = 'i18n:'
const translation_prefix_length = translation_prefix.length


let i18n = new VueI18n({
    locale: 'da', // set locale
    messages
});


export default i18n

/**
* Test whether a string should be translated
* @param {String} value - some string
* @returns {boolean} whether the value contains the translation_prefix, and
 * as such should be translated
*/
export function has_translation_prefix(value) {
    return value.substr(0, translation_prefix_length) === translation_prefix
}


/**
* Translate a prefixed string
* @param {String} translation_table - the lookup table used for translation
* @param {String} value - a string with a proper prefix followed by a key used to lookup in table
* @returns {String} the translation
*/
export function translate_prefixed(translation_table, value) {
    return i18n.t(translation_table + '.' + value.slice(translation_prefix_length))
}
