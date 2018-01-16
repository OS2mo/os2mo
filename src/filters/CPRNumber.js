
import Vue from 'vue'

Vue.filter('CPRNumber', value => {
  if (!value) return ''
  if (value.length !== 10) return value

  value = value.toString()
  return value.slice(0, 6) + '-' + value.slice(6)
})
