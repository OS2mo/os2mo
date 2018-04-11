import { Service } from './HttpCommon'

export default {
  /**
   * Get a list of all available facets
   * @param {String} orgUuid - organisation uuid
   * @returns {Array} a list of all available facets
   */
  employees (orgUuid, query) {
    query = query || ''
    return Service.get(`/o/${orgUuid}/e/?query=${query}`)
      .then(response => {
        return response.data.items
      })
      .catch(error => {
        console.log(error.response)
      })
  },

  cprLookup (query) {
    return Service.get(`/e/cpr_lookup/?q=${query}`)
      .then(response => {
        return response.data
      })
      .catch(error => {
        console.log(error.response)
      })
  },

  organisations (orgUuid, query) {
    query = query || ''
    return Service.get(`/o/${orgUuid}/ou/?query=${query}`)
      .then(response => {
        return response.data.items
      })
      .catch(error => {
        console.log(error.response)
      })
  },

  /**
   * Get a list of possible addresses based on search query
   * @param {String} orgUuid - the uuid of the organisation
   * @param {String} query - a query string to be used for lookup
   * @param {String} global - whether or not the lookup should be in the entire country, or contained to the municipality of the organisation
   * @returns {Array} a list of address suggestions based on search query
   */
  getGeographicalLocation (orgUuid, query, global) {
    global = global || null
    let location = global ? '&global=1' : '&global=0'
    return Service.get(`/o/${orgUuid}/address_autocomplete/?q=${query}${location}`)
      .then(response => {
        return response.data
      })
  }
}
