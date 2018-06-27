import axios from 'axios'

/**
 * Defines the base url and headers for http calls
 */

const Service = axios.create({
  baseURL: '/service',
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept',
    'Access-Control-Allow-Methods': 'GET, POST, DELETE, PUT'
  }
})

export default {
  get (url) {
    return Service
      .get(url)
  },

  post (url, payload) {
    return Service
      .post(url, payload)
  }
}
