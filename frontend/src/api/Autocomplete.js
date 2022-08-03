// SPDX-FileCopyrightText: 2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Service from "./HttpCommon"

export default {
  _getServiceUrl(entity, query) {
    let params = new URLSearchParams()
    params.append("query", query)
    return `/${entity}/autocomplete/?${params}`
  },

  _call(entity, query) {
    return Service.get(this._getServiceUrl(entity, query))
      .then((response) => {
        return response.data.items
      })
      .catch((error) => {
        console.log(error.response)
      })
  },

  /**
   * Search for an employee in an organisation
   * @param {String} query - search query
   * @returns {Array} - a list of employees matching the query
   */
  employees(query) {
    query = query || ""
    return this._call("e", query)
  },

  /**
   * Search for organisation units within an organisation
   * @param {String} query - search query
   * @returns {Array} - a list of organisation units matching the query
   */
  organisations(query) {
    query = query || ""
    return this._call("ou", query)
  },
}
