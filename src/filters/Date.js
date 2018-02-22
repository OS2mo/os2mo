import Vue from 'vue'

const moment = require('moment')
// require('moment/locale/da')

// Vue.use(require('vue-moment'), {
//   moment
// })
Vue.filter('date', function (value) {
  if (value === null || value === undefined) return
  return moment(value).format('DD-MM-YYYY')
})
