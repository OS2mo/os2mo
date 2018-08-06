import axios from 'axios'
import store from '@/vuex/store'
import {AUTH_LOGOUT} from '@/vuex/actions/auth'
import router from '../router'

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
      if (err.response.status === 401 || err.response.status === 403) {
        store.dispatch(AUTH_LOGOUT)
          .then(response => {
            router.push({name: 'Login'})
          })
      }
      reject(err)
    })
  }
)
