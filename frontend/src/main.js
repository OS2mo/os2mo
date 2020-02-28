// SPDX-FileCopyrightText: 2017-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Vue from 'vue'
import App from './App'
import router from './router'
import i18n from './i18n.js'
import VueShortKey from 'vue-shortkey'
import store from './store'
import { sync } from 'vuex-router-sync'
import './vee.js'
import '@babel/polyfill'
import './icons.js'
import 'bootstrap/dist/css/bootstrap.css'
import './assets/css/global.css'
import 'moment/locale/da'

import '@/views/employee/install'
import '@/views/organisation/install'
import '@/modules/install'

sync(store, router)

Vue.config.productionTip = false

Vue.use(VueShortKey, { prevent: ['input', 'textarea'] })

new Vue({
  router,
  store,
  i18n,
  render: h => h(App)
}).$mount('#app')
