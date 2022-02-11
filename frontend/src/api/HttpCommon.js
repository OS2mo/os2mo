// SPDX-FileCopyrightText: 2017-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import axios from 'axios'
import keycloak from '@/main'

/**
 * Defines the base url and headers for http calls
 */

const Service = axios.create({
  baseURL: '/service',
  timeout: 60 * 1000,
})

const Download = axios.create({
  baseURL: '/service',
  // Needs a byte array, since the zipped file is binary and not the default JSON-format
  responseType: 'arraybuffer',
})

const ApiV1 = axios.create({
  baseURL: '/api/v1',
})

const get_by_axios = function(url, axios) {
  return axios
    .get(url)
    .catch(err => {
      console.warn('Request failed', err)

      return new Promise(function (resolve, reject) {
        reject(err)
      })
    })
}

const get_by_graphql = function(query) {
  return axios({
    method: 'post',
    baseURL: 'http://localhost:5000/graphql',
    url: '',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${keycloak.token}`,
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Site': 'same-site'
    },
    data: {query: query}

    //POST http://localhost:5000/graphql

    // POST http://localhost:5000/graphql/
    //mode: 'cors',
    //credentials: 'same-origin',
  })
  .then((response) => {
    console.log('got response', reponse)
    return response
  })
  .catch((err) => {
    console.error('Somehting went horribly wrong', err)
  })
}

Service.interceptors.response.use(
  response => response,
  error => {
    const {status} = error.response;
    if (status === 403) {
      if (localStorage.moLocale === 'da'){
        alert('Du har ikke rettigheder til at foretage denne operation.')
      } else if (localStorage.moLocale === 'en') {
        alert('You do not have the privileges to perform this operation.')
      }
    }
    return Promise.reject(error);
 }
);

Service.interceptors.request.use(function (config){
  config.headers["Authorization"] = "Bearer " + keycloak.token
  return config
})

Download.interceptors.request.use(function (config){
  config.headers["Authorization"] = "Bearer " + keycloak.token
  return config
})

ApiV1.interceptors.request.use(function (config){
  config.headers["Authorization"] = "Bearer " + keycloak.token
  return config
})

export {
  get_by_graphql
}

export default {
  get (url) {
    return get_by_axios(url, Service)
  },
  post: Service.post,
  api_v1_get(url) {
    return get_by_axios(url, ApiV1)
  },
  download: Download.get,
}
