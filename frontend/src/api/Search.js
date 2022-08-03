// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Service from "./HttpCommon"
import store from "@/store"

export default {
  /**
   * Search for an employee in an organisation
   * @param {String} orgUuid - organisation uuid
   * @param {String} query - search query. Can be either a name or FULL CPR number
   * @returns {Array} a list of employees matching the query
   */
  employees(orgUuid, query) {
    query = query || ""
    let serviceUrl = `/o/${orgUuid}/e/?query=${query}`

    return Service.get(serviceUrl)
      .then((response) => {
        return response.data.items
      })
      .catch((error) => {
        console.log(error.response)
      })
  },

  /**
   * Search for organisation units within an organisation
   * @param {String} orgUuid - organisation uuid
   * @param {String} query - search query.
   * @param {String} date - used for 'at' query parameter
   * @param {String} details - level of details to include for each result
   * @returns {Array} a list of organisation units matching the query
   */
  organisations(orgUuid, query, date, details) {
    query = query || ""
    let serviceUrl = `/o/${orgUuid}/ou/?query=${query}&at=${date}&details=${details}`

    return Service.get(serviceUrl)
      .then((response) => {
        return response.data.items
      })
      .catch((error) => {
        console.log(error.response)
      })
  },

  /**
   * Look up a CPR number in the service platform
   * @param {String} query - search query. Can ONLY be a FULL CPR number
   * @returns {Object} the data matching the query
   */
  cprLookup(query) {
    return Service.get(`/e/cpr_lookup/?q=${query}`)
      .then((response) => {
        return response.data
      })
      .catch((error) => {
        store.commit("log/newError", { type: "ERROR", value: error.response.data })
        return error.response.data
      })
  },

  /**
   * Get a list of possible addresses based on search query
   * @param {String} orgUuid - the uuid of the organisation
   * @param {String} query - a query string to be used for lookup
   * @param {String} global - whether or not the lookup should be in the entire country, or contained to the municipality of the organisation
   * @returns {Array} a list of address suggestions based on search query
   */
  getGeographicalLocation(orgUuid, query, global) {
    global = global || null
    let location = global ? "&global=1" : "&global=0"
    return Service.get(
      `/o/${orgUuid}/address_autocomplete/?q=${query}${location}`
    ).then((response) => {
      return response.data
    })
  },
}
