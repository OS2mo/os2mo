// SPDX-FileCopyrightText: 2017-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Service from "./HttpCommon"
import URLSearchParams from "@ungap/url-search-params"

export default {
  /**
   * Get a list of all organisations
   * @param {Date} atDate - the date
   * @returns {Array} List of all organisations
   */
  getAll(atDate) {
    atDate = atDate || new Date()
    if (atDate instanceof Date) atDate = atDate.toISOString().split("T")[0]
    return Service.get(`/o/?at=${atDate}`)
      .then((response) => {
        return response.data
      })
      .catch((error) => {
        console.log(error.response)
      })
  },

  /**
   * Get an organisation
   * @param {String} OrgUuid - Uuid for the organisation to get
   * @returns {Object} an organisation object
   */
  get(uuid) {
    return Service.get(`/o/${uuid}/`)
      .then((response) => {
        return response.data
      })
      .catch((error) => {
        console.log(error.response)
      })
  },

  /**
   * Get the children of an organisation
   * @param {String} uuid - Uuid for current organisation
   * @param {Date} atDate - Date
   * @returns {Array} List of organisation units within the organisation
   */
  getChildren(uuid, atDate, extra) {
    if (atDate instanceof Date) atDate = atDate.toISOString().split("T")[0]

    const params = new URLSearchParams()

    if (atDate) {
      params.append("at", atDate)
    }

    if (extra !== undefined) {
      for (const key in extra) {
        params.append(key, extra[key])
      }
    }

    return Service.get(`/o/${uuid}/children?${params}`)
      .then((response) => {
        return response.data.sort((a, b) => (a.name > b.name ? 1 : -1))
      })
      .catch((error) => {
        console.log(error.response)
      })
  },
}
