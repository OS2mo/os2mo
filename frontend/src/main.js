import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import App from './App'
import router from './router'
import VueI18n from 'vue-i18n'
import { da } from './i18n/da'
import VeeValidate, { Validator } from 'vee-validate'
import DateInRange from './validators/DateInRange'
import messagesDA from '../node_modules/vee-validate/dist/locale/da'
import VueShortKey from 'vue-shortkey'
import store from './store'

import 'vue-awesome/icons'
import Icon from 'vue-awesome/components/Icon'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue'

import './assets/css/global.css'
import 'moment/locale/da'

Vue.config.productionTip = false

const veeConfig = {
  dateFormat: 'DD-MM-YYYY',
  delay: 100,
  locale: 'da',
  inject: false
}

Validator.localize('da', messagesDA)

Validator.extend('date_in_range', DateInRange)

Vue.use(BootstrapVue)
Vue.use(VueI18n)
Vue.use(VeeValidate, veeConfig)
Vue.use(VueShortKey, { prevent: ['input', 'textarea'] })
Vue.component('icon', Icon)

const messages = {
  da: da
}

const i18n = new VueI18n({
  locale: 'da', // set locale
  messages
})

new Vue({
  router,
  store,
  i18n,
  render: h => h(App)
}).$mount('#app')
