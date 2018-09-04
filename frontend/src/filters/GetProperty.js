import Vue from 'vue'

Vue.filter('getProperty', function (value, property) {
  if (!value || !value[property]) return '-'
  return value[property]
})
