// SPDX-FileCopyrightText: 2017-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import axios from 'axios'
import store from '@/store'
import { Auth } from '@/store/actions/auth'

/**
 * Defines the base url and headers for http calls
 */

const Service = axios.create({
  baseURL: '/service',
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
    'X-Client-Name': 'OS2mo-UI',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept',
    'Access-Control-Allow-Methods': 'GET, POST, DELETE, PUT'
  }
})
const ApiV1 = axios.create({
  baseURL: '/api/v1',
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
    'X-Client-Name': 'OS2mo-UI',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept',
    'Access-Control-Allow-Methods': 'GET, POST, DELETE, PUT'
  }
})

function get_by_axios (url, axios) {
  return axios
    .get(url)
    .catch(err => {
      console.warn('request failed', err)

      if (err.response.status === 401) {
        return store.dispatch(Auth.actions.AUTH_REQUEST)
      }

      return new Promise(function (resolve, reject) {
        reject(err)
      })
    })
}



export default {
  get (url) {
    return get_by_axios(url, Service)
  },
  post: Service.post,
  api_v1_get(url) {
    return get_by_axios(url, ApiV1)
  }
}
frontend/src/locales/da/shared.json
