import axios from 'axios'
import store from '@/vuex/store'
import {AUTH_LOGOUT} from '@/vuex/actions/auth'

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

Service.interceptors.response.use(
  undefined, err => {
    return new Promise(function (resolve, reject) {
      if (err.response.status === 401 && err.response.config && !err.response.config.__isRetryRequest) {
        store.dispatch(AUTH_LOGOUT)
      }
      throw err
    })
  }
)

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
