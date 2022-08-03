// SPDX-FileCopyrightText: 2017-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import axios from "axios"

/**
 * Defines the base url and headers for http calls
 */

const Version = axios.create({
  baseURL: "/version",
  headers: {
    "X-Requested-With": "XMLHttpRequest",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept",
    "Access-Control-Allow-Methods": "GET, POST, DELETE, PUT",
  },
})

export default {
  get() {
    return Version.get("/")
  },
}
