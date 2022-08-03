// SPDX-FileCopyrightText: 2017-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import axios from "axios"
import keycloak from "@/main"

/**
 * Defines the base url and headers for http calls
 */

const Service = axios.create({
  baseURL: "/service",
  timeout: 60 * 1000,
})

const Download = axios.create({
  baseURL: "/service",
  // Needs a byte array, since the zipped file is binary and not the default JSON-format
  responseType: "arraybuffer",
})

Service.interceptors.response.use(
  (response) => response,
  (error) => {
    const { status } = error.response
    if (status === 403) {
      if (localStorage.moLocale === "da") {
        alert("Du har ikke rettigheder til at foretage denne operation.")
      } else if (localStorage.moLocale === "en") {
        alert("You do not have the privileges to perform this operation.")
      }
    }
    return Promise.reject(error)
  }
)

Service.interceptors.request.use(function (config) {
  config.headers["Authorization"] = "Bearer " + keycloak.token
  return config
})

Download.interceptors.request.use(function (config) {
  config.headers["Authorization"] = "Bearer " + keycloak.token
  return config
})

function get_by_axios(url, axios) {
  return axios.get(url).catch((err) => {
    console.warn("Request failed", err)

    return new Promise(function (resolve, reject) {
      reject(err)
    })
  })
}

export default {
  get(url) {
    return get_by_axios(url, Service)
  },
  post: Service.post,
  download: Download.get,
}
