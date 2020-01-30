// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Vue from 'vue'
import VueI18n from 'vue-i18n'
import { da } from './locales/da'

Vue.use(VueI18n)

const messages = {
  da: da
}

export default new VueI18n({
  locale: 'da', // set locale
  messages
})
