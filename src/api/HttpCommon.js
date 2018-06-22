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

function responseErrorHandler (error) {
  if (error.response.status === 401) {
    // Route to login page, or something
    console.log(error.response.statusText)
  }
}

export default {
  get (url) {
    return Service
      .get(url)
      .catch(responseErrorHandler)
  },

  post (url, payload) {
    return Service
      .post(url, payload)
      .catch(responseErrorHandler)
  }
}
